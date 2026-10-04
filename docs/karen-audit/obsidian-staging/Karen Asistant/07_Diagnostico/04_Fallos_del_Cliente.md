---
knowledge_id: "karen-audit-20261003-04"
title: "Karen — fallos reproducidos y riesgos del cliente"
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

# Karen — fallos reproducidos y riesgos del cliente

## Bloqueos reproducidos

| Prioridad | Hallazgo | Evidencia | Acción siguiente |
| --- | --- | --- | --- |
| P0 | Configuración de endpoint incompatible | Generación en 3000 retorna 405; catálogo es HTML | Perfiles de API correctos y prueba de contrato |
| P0 | No detecta el micrófono | DeviceList no es list; GUI muestra botón disabled | Corregir selección y comprobar índice en el backend de captura |
| P0 | Lanzador no corresponde al parser | --whisper-model, --no-wake-word y --input-device rechazados con salida 2 | Alinear CLI, launcher y perfiles VS Code |
| P1 | Guardar no persiste | Cambia KarenClient, pero no actualiza la dataclass ni escribe archivo | Guardado validado y recuperación al reiniciar |
| P1 | Wake word ONNX desconectado | Sin carga o inferencia de karen.onnx en cliente.py | Reconectar pipeline y medir falsas activaciones |
| P1 | Respuesta hablada ausente | No hay llamada a TTS o reproducción | Conectar síntesis y ciclo de audio |

El contrato CLI se comprobó ejecutando la función parse_args extraída del AST, sin arrancar escucha ni el script completo. Los argumentos --server, --model y --api-key sí se aceptan. El launcher pasa --whisper-model siempre, por lo que falla antes de abrir el programa. También usa cliente.py por ruta relativa sin fijar el directorio al del script.

## Configuración desconectada

Se comprobó la validación de URL, límites positivos y overrides. Pero muchas opciones del dataclass no se usan en el flujo actual: input_device, wake_word_enabled, umbrales, sample_rate, command_seconds, voice_rate, voice_pitch, memory_dir y memory_files. Whisper base y timeout 90 aparecen fijados directamente.

El botón Guardar prepara un cliente HTTP nuevo; no escribe configuración ni modifica self.config. La prueba de widgets con una URL inicial distinta confirmó que client.server cambia y config.server conserva el valor anterior. El nombre de la acción induce a esperar persistencia que no existe.

## Hilos y estados de interfaz

test_api, send_prompt y listen_loop llaman a log o config de widgets desde hilos secundarios. El código solo usa root.after para una actualización puntual. Se observó el patrón en fuente; no se forzó una excepción ni se realizó una prueba de concurrencia. Centralizar eventos en el hilo de GUI debe formar parte de la estabilización.

La escucha no maneja completamente la apertura de sr.Microphone dentro de su try, porque el contexto se abre antes del bucle de captura. Un fallo al abrir podría finalizar el hilo dejando un estado de escucha incorrecto. Tras una detección el cliente apaga la escucha en vez de volver automáticamente a esperar el nombre.

El cliente permite múltiples envíos sin un control de solicitud activa. No hay cancelación, cambio automático de nodo ni distinción de estados de ambos nodos. Usa stream=False, por lo que no muestra respuesta token a token.

## Historial, identidad y seguridad de presentación

ask envía prompt aislado mediante /api/generate; no incorpora memoria de Obsidian, identidad, historial conversacional o herramientas del sistema. Las rutas FRIDAY declaradas en config.py no se leen. No afirmar que Karen tiene memoria o control de PC por tener esos campos.

El campo API key no está enmascarado. En la configuración observada estaba vacío; no hubo exposición de una clave real durante el diagnóstico. El código transmite Bearer si existe, pero el contrato de autenticación debe definirse por adaptador antes de cambiar entre servicios.

## Diferencia frente al historial

Las notas antiguas describen una versión con Flask /chat, Edge-TTS y openWakeWord. Los archivos actuales describen un cliente Tkinter para Ollama directo. No hay evidencia suficiente de cuándo o por quién se sustituyó aquel flujo. Conservar ambas descripciones fechadas y decidir cuál es la base que se recuperará, sin mezclarlas como si fueran el mismo programa.
