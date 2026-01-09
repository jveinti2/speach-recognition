# Speech Recognition - Sistema de Identificación de Hablantes

Sistema de identificación biométrica de voz usando ECAPA-TDNN de SpeechBrain. Registra voces generando embeddings de 192-d e identifica hablantes por similitud coseno.

## Setup

### Windows

```bash
# 1. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate

# 2. Instalar dependencias
python -m pip install --upgrade pip
python -m pip install torch==2.2.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### Linux

```bash
# 1. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependencias
python -m pip install --upgrade pip
python -m pip install torch==2.2.2 torchaudio==2.2.2
pip install -r requirements.txt
```

## Opción 1: Probar con Notebooks

```bash
pip install jupyter
jupyter notebook
```

Ejecuta los notebooks en orden:
1. **`notebooks/voice_register.ipynb`** - Registra una nueva voz (graba 10s → genera embedding → guarda)
2. **`notebooks/voice_comparative.ipynb`** - Identifica un hablante (graba 10s → compara con BD)

**Gestionar voces:**
```bash
ls voices_db/              # Ver voces registradas
rm voices_db/{persona_id}.npy  # Eliminar una voz
```

## Opción 2: Probar con API

```bash
python run.py
```

API disponible en `http://localhost:8000`

**Endpoints principales:**
- `POST /v1/voices` - Registrar voz
- `POST /v1/sessions/identify` - Identificar hablante
- WebSocket `/ws/audio-hook` - Stream de audio en tiempo real

Documentación interactiva: `http://localhost:8000/docs`

## Notas

- Requiere micrófono funcional
- Modelo se descarga automáticamente en primera ejecución
- Threshold identificación: 0.75 (ajustable)
- Solo CPU (sin GPU)
- Windows: usa backend 'soundfile' de torchaudio
