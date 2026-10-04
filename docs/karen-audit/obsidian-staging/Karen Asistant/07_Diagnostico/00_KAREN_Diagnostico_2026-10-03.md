---
knowledge_id: "karen-audit-20261003-00"
title: "Karen — diagnóstico y continuidad del 3 de octubre"
project: "Karen"
domain: "diagnostico"
note_type: "evidence"
version: "1.0.0"
status: "current"
created: "2026-10-03"
updated: "2026-10-03"
up: ["[[Karen Asistant/01_Core/KAREN]]"]
related: []
replaces: []
source_refs: ["AUDIT-KAREN-20261003", "CHAT-KAREN-20261003"]
tags: ["karen", "diagnostico", "sesion-2026-10-03"]
---

# Karen — diagnóstico y continuidad del 3 de octubre

> [!summary] Resultado
> La PC y el Homelab pueden generar respuestas. El cliente actual no está conectado correctamente a ese flujo: su URL predeterminada usa el puerto 3000, el detector de micrófono rechaza DeviceList y el lanzador contiene opciones incompatibles.

## Pedido de esta sesión

El usuario pidió revisar completamente `C:\Karen`, decir qué funciona, guardar el diagnóstico en Obsidian y dejar un mensaje al terminar para poder apagar la PC. El refinamiento y la conexión funcional se retomarán en la próxima sesión.

El objetivo acordado es una interfaz única y dinámica para Karen, con elección entre el servidor del Homelab y la PC principal de uso personal. El servidor es una opción, y la PC debe poder sostener el funcionamiento cuando el servidor no esté disponible. Se propuso mantener captura y wake word en la PC para que la activación no dependa de la conectividad. El cambio automático de nodo es una propuesta posterior a estabilizar la selección manual.

## Qué funciona, con evidencia

| Componente | Resultado observado | Alcance |
| --- | --- | --- |
| Código Python | Los cuatro módulos se pueden analizar | Sintaxis, no todo el comportamiento |
| GUI Tkinter | Se construyó a 980 × 760 en Python 3.11 y 3.14 | Comprobación de widgets; sin revisión visual completa |
| Dependencias 3.11 | Todas las dependencias importadas de la lista están disponibles | No implica compatibilidad de todas sus funciones |
| Ollama en la PC | HTTP 200, respuesta «OK», con qwen2:0.5b | Inferencia real mínima |
| Ollama en Homelab | HTTP 200, respuesta «OK.», con llama3.2:3b | Inferencia real mínima |
| API histórica de Karen | `/salud` responde HTTP 200 | No se probó `/chat` ni se revisó el servicio remoto |
| Whisper base | Transcribió el MP3 existente en CPU | No se grabó ni probó voz en vivo |
| ONNX | Carga en CPU y produce salida finita | No se probó detección real de la palabra |
| ffmpeg y ffprobe | Ejecutan y reconocen el MP3 | No se reprodujo audio |

## Navegación del diagnóstico

- [[Karen Asistant/07_Diagnostico/01_Inventario_y_Entorno]]: archivos, runtimes y recursos.
- [[Karen Asistant/07_Diagnostico/02_Servidor_y_PC]]: endpoints, modelos y generación real.
- [[Karen Asistant/07_Diagnostico/03_Voz_y_Wakeword]]: micrófono, Whisper, ONNX y respuesta hablada.
- [[Karen Asistant/07_Diagnostico/04_Fallos_del_Cliente]]: fallos reproducidos y riesgos del código.
- [[Karen Asistant/07_Diagnostico/05_Plan_Proxima_Sesion]]: orden de implementación y criterios de cierre.
- [[Karen Asistant/07_Diagnostico/06_Fuentes_y_Limites]]: fuentes, conservación y lo que no se verificó.

## Relación con el historial

Las notas de septiembre describen otro flujo: wake word ONNX → Whisper → Flask `/chat` → Ollama → Edge-TTS. El `cliente.py` actual no corresponde a esa implementación. Se conservan las notas antiguas como fuentes históricas y se registra esta diferencia, sin borrarlas ni atribuir al modelo v2 una validación inexistente.

[[Karen Asistant/01_Core/KAREN_Arquitectura]] · [[Karen Asistant/02_Roadmap/KAREN_Estado_Actual]] · [[Karen Asistant/KAREN_Cliente_Streaming]]
