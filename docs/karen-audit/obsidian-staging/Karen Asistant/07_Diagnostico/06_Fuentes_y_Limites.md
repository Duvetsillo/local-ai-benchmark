---
knowledge_id: "karen-audit-20261003-06"
title: "Karen — fuentes, evidencia y límites del diagnóstico"
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

# Karen — fuentes, evidencia y límites del diagnóstico

## Registro de fuentes

| ID | Fuente | Tratamiento |
| --- | --- | --- |
| CHAT-KAREN-20261003 | Conversación visible de voz sobre dos nodos y diagnóstico | Requisitos y plan conservados en índice y próxima sesión |
| CODE-KAREN-20261003 | Archivos legibles de C:\Karen y enumeración completa | Inspección estática y hashes; código sin cambios |
| RUNTIME-KAREN-20261003 | Python 3.11/3.14, imports, CLI, GUI, dispositivos, ONNX, ffmpeg | Informes JSON locales y notas por área |
| NETWORK-KAREN-20261003 | GET de versiones, catálogos y salud; generación sintética acotada | Respuestas comprobadas sin copiar datos privados |
| STT-KAREN-20261003 | Whisper base y muestra MP3 existente | Transcripción local; solo medidas conservadas |
| LEGACY-KAREN-202609 | MOC, arquitectura, estado, cliente streaming, error wakeword, bitácora y decisiones existentes | Antecedentes fechados; no sobrescritos ni tratados como implementación actual |

## Evidencia local

Los informes quedan en `docs/karen-audit` del workspace Local_AI_Benchmark: runtime-311.json, runtime-314.json, focused-311.json, network-311.json, inference-311.json y stt-311.json. El script audit_runtime.py registra pruebas acotadas y reproduce las comprobaciones; no sirve como lanzador de Karen.

| Archivo de código | SHA-256 observado |
| --- | --- |
| cliente.py | a4d0a35e4193df59c39720f2e7daae91ae423d1f2a18945413976bd5a8cc1b43 |
| config.py | 8134eff0d8b51af141eaf4eab396b64f8c362337a300ee4849c3581eb71e4984 |
| diagnose_devices.py | 4eda5cfe6bfcb49196b778f6367da73314497d2defb41cd24a6006c9fcc57afe |
| diagnose_mic.py | 155f7d110a77041e81d002c772e6230eff9fc748098efb9327cd024229171c30 |

## Conservación y autorización

La reorganización anterior dejó intactos los archivos Karen y Friday. Esta petición posterior autoriza guardar el diagnóstico de Karen: se añaden siete notas nuevas, sin alterar las notas previas, Friday, el código C:\Karen ni la configuración del grafo. El índice nuevo enlaza los mapas existentes para integrarse mediante backlinks.

Se mantiene la preferencia B de organización equilibrada para sintetizar la conversación. Los informes preservan el detalle técnico y las condiciones de las pruebas. No se elimina contenido histórico ni se afirma acceso a conversaciones no visibles.

## Lo que no se hizo

- No se corrigió ni rediseñó el cliente.
- No se instaló paquete, descargó modelo o reentrenó wake word.
- No se grabó voz nueva ni se reprodujo audio.
- No se validó el pipeline completo de micrófono a respuesta hablada.
- No se probó detección con positivos/negativos reales ni se confirmó que ONNX sea v2.
- No se accedió por SSH al servidor, se inspeccionó systemd ni se verificó /chat.
- No se ejecutaron acciones de control de Windows o Proxmox, se reiniciaron servicios ni se cambió red.
- No se apagó la PC ni se creó una tarea programada.

La notificación de cierre es el mensaje final de esta conversación. No implica que el asistente continúe después de apagar el equipo. Las notas permiten retomar la próxima sesión sin depender de esa continuidad.
