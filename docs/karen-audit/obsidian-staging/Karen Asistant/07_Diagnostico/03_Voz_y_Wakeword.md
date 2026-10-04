---
knowledge_id: "karen-audit-20261003-03"
title: "Karen — audio, Whisper y wake word"
project: "Karen"
domain: "diagnostico"
note_type: "evidence"
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

# Karen — audio, Whisper y wake word

## Micrófono

Windows y sounddevice enumeran el Fifine, entradas de audio integrado y VB-Audio. El dispositivo de entrada predeterminado observado fue 1; varios dispositivos aceptan mono int16 a 16 kHz según check_input_settings. Se verificó formato, no calidad acústica ni captura en vivo.

El fallo reproducido está en detect_microphone: usa `isinstance(devices, list)`, pero query_devices devuelve DeviceList y esa comprobación es falsa. No recorre ningún dispositivo, retorna None y la GUI deshabilita «Activar micrófono». La misma condición se reprodujo en 3.11 y 3.14.

Además, la enumeración de sounddevice y la de sr.Microphone/PyAudio no deben tratarse como índices intercambiables sin comprobar el dispositivo concreto. El código mezcla ambas rutas. Los scripts diagnósticos tienen índices fijos que ya no son una selección fiable: el índice 4 ni aparece como entrada en la enumeración actual. No se ejecutaron esos scripts, porque graban audio.

## Whisper

Whisper base cargó desde el archivo de caché existente, en CPU. Transcribió el MP3 local de 13,92 s, detectando español y generando 153 caracteres en tres segmentos. La operación duró aproximadamente 5,66 s. Se conservó la medida, no el texto de la grabación. No se descargó modelo ni se capturó voz nueva.

El cliente fija `model="base"` en recognize_whisper aunque config.py permita whisper_model. La ruta de voz con sr.Microphone no se completó; faltaría ensayar el reconocimiento real usando el Fifine y el runtime elegido.

## Modelo karen.onnx

El archivo de 350.767 bytes cargó con ONNX Runtime en CPU. Entrada float de forma `[1,28,96]`, salida karen `[1,1]`. SHA-256: `9378bf0706a486bf115b01f6d027b09bae23b90babafedef52f0585fbdde1c27`.

Una entrada sintética de features completamente cero produjo aproximadamente 0,90089. Esto es una señal que merece investigar, pero **no es una prueba con silencio real**: features cero no equivalen necesariamente a la representación de audio silencioso. No prueba por sí sola falsos positivos ni identifica si el archivo es v1 o v2.

El cliente actual no importa openWakeWord u ONNX Runtime ni abre este archivo. La activación implementada consiste en transcribir una frase y buscar la subcadena “karen”, borrar sus apariciones y enviar el resto. Después desactiva la escucha. No es el pipeline ONNX continuo con warm-up y confirmaciones descrito en las notas históricas.

## Respuesta hablada

Edge-TTS y pyttsx3 están disponibles en 3.11. ffmpeg y ffprobe funcionan; la muestra MP3 es legible. Sin embargo, cliente.py no genera ni reproduce TTS. El campo «Voz» se lee al guardar, pero no conecta con un sintetizador ni se persiste.

No se probó síntesis online de Edge-TTS ni reproducción de altavoces. No llamar «asistente de voz completo» a una ventana que solo muestra texto. Para la próxima sesión se debe definir TTS principal y alternativa local, estados de audio y prevención de que Karen se reactive por su propia voz.

## Historial relevante

[[Karen Asistant/KAREN_Error8_WakeWordV2]] describe falsos positivos de la v1 y negativos de habla para reentrenamiento. [[Karen Asistant/KAREN_Cliente_Streaming]] describe streaming, warm-up y confirmación consecutiva. Son antecedentes útiles, pero no se confirmó que esa implementación esté en el archivo actual ni que el modelo actual haya superado su validación.
