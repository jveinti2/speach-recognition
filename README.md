# Speech Recognition - Sistema de Identificación de Hablantes

Sistema de reconocimiento de voz para identificación de hablantes usando embeddings ECAPA-TDNN de SpeechBrain.

## Descripción

Este proyecto implementa un sistema de identificación biométrica de voz que:
- **Registra** voces de usuarios generando embeddings de 192 dimensiones
- **Identifica** hablantes comparando audio capturado contra una base de datos de voces registradas
- Usa el modelo pre-entrenado **ECAPA-TDNN** de SpeechBrain (VoxCeleb dataset)
- Aplica **similitud coseno** para matching de voces (threshold 0.75)

## Requerimientos

- Python 3.8+
- Micrófono funcional
- Windows (configurado para backend 'soundfile' de torchaudio)
- ~500MB espacio para modelo y dependencias

## Instalación

### 1. Crear entorno virtual

```bash
python -m venv venv
```

### 2. Activar entorno virtual

```bash
venv\Scripts\activate
```

### 3. Actualizar pip

```bash
python -m pip install --upgrade pip
```

### 4. Instalar PyTorch y torchaudio (CPU only)

```bash
python -m pip install torch==2.2.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cpu
```

### 5. Instalar dependencias del proyecto

```bash
pip install speechbrain==0.5.16 faiss-cpu==1.8.0 numpy sounddevice soundfile
```

O usar el archivo de requerimientos:

```bash
pip install -r requirements.txt
```

### 6. Instalar Jupyter (necesario para notebooks)

```bash
pip install jupyter
```

### 7. Descargar modelo pre-entrenado

**Opción A - Descarga automática (recomendada):**

El modelo se descargará automáticamente la primera vez que ejecutes los notebooks. SpeechBrain lo descarga desde Hugging Face y lo guarda en `models/spkrec-ecapa-voxceleb/`.

**Opción B - Descarga manual:**

Si prefieres descargar el modelo manualmente:

```bash
# Descargar desde Hugging Face Hub
huggingface-cli download speechbrain/spkrec-ecapa-voxceleb --local-dir models/spkrec-ecapa-voxceleb
```

O descárgalo desde: https://huggingface.co/speechbrain/spkrec-ecapa-voxceleb

Asegúrate de que los archivos estén en `models/spkrec-ecapa-voxceleb/`:
- `classifier.ckpt` (~5MB)
- `embedding_model.ckpt` (~80MB)
- `hyperparams.yaml`
- `mean_var_norm_emb.ckpt`

## Uso

### 1. Iniciar Jupyter Notebook

```bash
jupyter notebook
```

### 2. Registrar voces

Abre y ejecuta `notebooks/voice_register.ipynb`:
- Graba 10 segundos de audio
- Genera embedding
- Guarda en `voices_db/{persona_id}.npy`

### 3. Identificar hablantes

Abre y ejecuta `notebooks/voice_comparative.ipynb`:
- Graba 10 segundos de audio
- Compara contra voces registradas
- Muestra identidad si score >= 0.75

## Gestión de Base de Datos

**Ver voces registradas:**
```bash
ls voices_db/
```

**Eliminar una voz:**
```bash
rm voices_db/{persona_id}.npy
```

## Estructura del Proyecto

```
speach-recognition/
├── notebooks/
│   ├── voice_register.ipynb      # Registro de nuevas voces
│   └── voice_comparative.ipynb   # Identificación de hablantes
├── models/
│   └── spkrec-ecapa-voxceleb/   # Modelo ECAPA-TDNN pre-entrenado
├── voices_db/                    # Base de datos de voces (.npy files)
├── audio/                        # Audio temporal
├── audio_tmp/                    # Audio temporal alternativo
├── requirements.txt              # Dependencias Python
└── README.md
```

## Parámetros Técnicos

- **Sample Rate:** 16 kHz
- **Canales:** Mono
- **Duración grabación:** 10 segundos
- **Dimensión embedding:** 192-d
- **Métrica similitud:** Coseno
- **Threshold identificación:** 0.75
- **Dispositivo:** CPU only

## Notas

- Los warnings de torchaudio/tqdm en los notebooks son esperados y no afectan la funcionalidad
- El sistema requiere acceso al micrófono
- El modelo ejecuta solo en CPU (no requiere GPU)
