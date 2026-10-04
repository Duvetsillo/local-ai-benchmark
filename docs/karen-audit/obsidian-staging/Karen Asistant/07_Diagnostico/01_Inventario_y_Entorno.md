---
knowledge_id: "karen-audit-20261003-01"
title: "Karen — inventario y entorno de ejecución"
project: "Karen"
domain: "diagnostico"
note_type: "reference"
version: "1.0.0"
status: "current"
created: "2026-10-03"
updated: "2026-10-03"
up: ["[[Karen Asistant/07_Diagnostico/00_KAREN_Diagnostico_2026-10-03]]"]
related: []
replaces: []
source_refs: ["AUDIT-KAREN-20261003", "CHAT-KAREN-20261003"]
tags: ["karen", "diagnostico", "sesion-2026-10-03"]
---

# Karen — inventario y entorno de ejecución

## Carpeta inspeccionada

`C:\Karen` contiene `cliente.py`, `config.py`, `requirements.txt`, `start_karen.ps1`, dos scripts de diagnóstico de micrófono, `karen.onnx`, `ffmpeg.exe`, `ffprobe.exe`, una muestra MP3, `.env.example`, configuración de VS Code y archivos de caché Python. La enumeración recursiva encontró 16 archivos. No se encontró `server.py`, scripts de entrenamiento, pruebas automatizadas ni un repositorio `.git` dentro de esta carpeta. Esto no demuestra que no existan en otro equipo.

| Archivo | Función observada |
| --- | --- |
| cliente.py | GUI Tkinter y cliente directo de API Ollama |
| config.py | Dataclass, valores predeterminados, variables de entorno y validación |
| start_karen.ps1 | Lanzamiento con Python 3.11; contrato desalineado con parse_args |
| diagnose_devices.py | Captura desde índices fijos 31, 33 y 41; no ejecutado |
| diagnose_mic.py | Captura de diez segundos desde índice fijo 4; no ejecutado |
| karen.onnx | Modelo con entrada de features 1 × 28 × 96; no usado por cliente.py |
| muestra_friday_dalia.mp3 | Muestra existente de 13,92 s, mono, 24 kHz; no se modificó |
| .vscode/launch.json | Perfiles de servidor y activación manual; contiene un flag rechazado |

## Runtimes comprobados

- Python 3.11.9: NumPy 2.4.6, requests 2.34.2, sounddevice 0.5.6, SpeechRecognition 3.17.0, PyAudio 0.2.14, Whisper 20250625, ONNX Runtime 1.29.0, openWakeWord 0.6.0, Edge-TTS 7.2.8, soundfile 0.14.0, pyttsx3 2.99, Torch 2.13.0 y Tk 8.6 importan.
- Python 3.14.7: GUI y mayoría de imports disponibles, pero faltan PyAudio y pyttsx3. Tk es 9.0, ONNX Runtime 1.30.0 y Torch 2.14.0.
- El launcher `py` reconoce ambas versiones; `python` en PATH apunta a 3.14. El script selecciona 3.11 explícitamente.

Para la siguiente sesión conviene usar 3.11 como base conocida de diagnóstico. Los requirements no fijan versiones y no existe un entorno virtual dentro de C:\Karen; preparar un entorno reproducible antes de ampliar la implementación.

## PC principal observada

Windows 11 Home, AMD Ryzen 5 5500, seis núcleos y doce hilos, aproximadamente 15,87 GiB de RAM visible y GPU NVIDIA RTX 2060. También aparece el adaptador spacedesk. La lectura puntual mostró 2,71 GiB libres, no una medida de pico ni de memoria disponible permanentemente. No se confirmó VRAM ni aceleración CUDA de Whisper.

Ollama estaba ejecutándose en la PC. Los pesos Whisper `tiny.pt` y `base.pt` ya estaban en caché. No se instalaron paquetes ni se descargaron modelos durante el diagnóstico.

## Configuración

El valor efectivo era servidor `http://192.168.100.66:3000`, modelo `qwen2:0.5b`, Whisper base y dispositivo de entrada sin selección explícita. No había API key efectiva. No hay `.env` en la carpeta y el código no carga archivos dotenv: `.env.example` sirve de referencia, no se aplica automáticamente. No se copian claves ni tokens a las notas.
