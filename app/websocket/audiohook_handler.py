from datetime import datetime
from typing import Optional
from app.websocket.connection_manager import ConnectionManager
from app.utils.audio_buffer import AudioBuffer
from app.core.pcm_converter import PCMConverter
from app.core.embedding_generator import EmbeddingGenerator
from app.core.voice_matcher import VoiceMatcher
from app.repositories.voice_repository import VoiceRepository
from app.dependencies import get_model_manager
from app.schemas.audiohook import IdentificationResult


class AudioHookHandler:
    def __init__(
        self,
        audio_buffer: AudioBuffer,
        connection_manager: ConnectionManager,
        voice_repository: VoiceRepository,
        session_service=None
    ):
        self.audio_buffer = audio_buffer
        self.connection_manager = connection_manager
        self.voice_repository = voice_repository
        self.session_service = session_service

        model_manager = get_model_manager()
        classifier = model_manager.get_classifier()
        self.embedding_generator = EmbeddingGenerator(classifier)
        self.voice_matcher = VoiceMatcher()
        self.pcm_converter = PCMConverter()

    def set_session_service(self, session_service):
        self.session_service = session_service

    async def identify_speaker(self, conversation_id: str):
        print(f"[{conversation_id}] Iniciando identificación...")

        try:
            chunks = self.audio_buffer.get_chunks(conversation_id)
            threshold = self.audio_buffer.get_threshold(conversation_id)

            waveform = self.pcm_converter.ulaw_chunks_to_waveform(chunks)

            embedding = self.embedding_generator.generate_embedding(waveform)

            voice_pool = self.voice_repository.get_all_embeddings()

            result = self.voice_matcher.find_match(embedding, voice_pool, threshold)

            result_message = IdentificationResult(
                conversation_id=conversation_id,
                identified=result["identified"],
                person_id=result.get("person_id"),
                score=result["score"],
                all_scores=result["all_scores"],
                threshold=result.get("threshold", threshold),
                completed_at=datetime.now(),
                message=result.get("message")
            )

            if self.session_service:
                self.session_service.store_identification_result(
                    conversation_id,
                    result_message.model_dump(mode='json')
                )

            await self.connection_manager.send_json(
                result_message.model_dump(mode='json'),
                client_id="audiohook"
            )

            print(f"[{conversation_id}] Identificación completada: {result.get('person_id', 'DESCONOCIDO')}")

            self.audio_buffer.pause(conversation_id)
            self.audio_buffer.clear(conversation_id)

        except Exception as e:
            print(f"Error en identificación para {conversation_id}: {str(e)}")
            error_result = {
                "conversation_id": conversation_id,
                "identified": False,
                "person_id": None,
                "score": 0.0,
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            }

            if self.session_service:
                self.session_service.store_identification_result(conversation_id, error_result)

            await self.connection_manager.send_json(error_result, client_id="audiohook")
