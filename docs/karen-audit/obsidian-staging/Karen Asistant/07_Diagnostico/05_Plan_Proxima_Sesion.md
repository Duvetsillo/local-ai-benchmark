---
knowledge_id: "karen-audit-20261003-05"
title: "Karen — plan para la próxima sesión"
project: "Karen"
domain: "diagnostico"
note_type: "task"
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

# Karen — plan para la próxima sesión

## Objetivo del usuario

Refinar Karen, conectarla al Homelab y ofrecer funcionamiento con la PC principal. Poder alternar entre ambos nodos desde una interfaz dinámica. Mantener wake word lo más refinado posible. La conversación dejó propuesto que el wake word y la captura permanezcan en la PC aunque el servidor esté desconectado.

Este plan es trabajo pendiente. La sesión de diagnóstico no aplicó correcciones ni rediseños.

## 1. Congelar una base recuperable

- [ ] Respaldar C:\Karen y registrar hashes antes de editar.
- [ ] Preparar entorno Python 3.11 con dependencias versionadas.
- [ ] Unificar punto de entrada, directorio de arranque, CLI y perfiles VS Code.

Cierre: una única forma reproducible de iniciar, sin argumentos rechazados ni dependencia del directorio desde donde se ejecute.

## 2. Conexión de dos nodos

- [ ] Perfil PC: Ollama localhost:11434 y modelo realmente instalado.
- [ ] Perfil Homelab: decidir entre Ollama directo :11434 o adaptador Flask :5000/chat según identidad, historial y capacidades requeridas.
- [ ] Comprobar contrato, catálogo y disponibilidad del modelo; mostrar el nodo y modelo activos.
- [ ] Elegir nodo manualmente y guardar configuración de forma persistente.
- [ ] Evaluar cambio automático después; no duplicar una petición en ambos nodos si ya se está ejecutando o existe historial remoto compartido.

Cierre: una pregunta real completa por cada perfil, error claro cuando un nodo falla y cambio de nodo sin reiniciar la aplicación. No abrir servicios adicionales o modificar red para resolver un contrato incorrecto.

## 3. Audio fiable

- [ ] Corregir detector DeviceList y elegir Fifine de forma consistente con el backend de captura.
- [ ] Respetar configuración Whisper y verificar captura/STT en vivo.
- [ ] Conectar TTS y probar altavoces, interrupción y recuperación.
- [ ] Estados claros: inactivo, escuchando nombre, capturando comando, transcribiendo, generando, hablando y error.

Cierre: frase hablada → texto → nodo elegido → respuesta hablada, y retorno a espera sin bloquear la ventana.

## 4. Wake word real

- [ ] Identificar procedencia y versión del ONNX actual por hash y artefactos de entrenamiento.
- [ ] Integrar frontend de audio y features apropiado antes de inferir el modelo.
- [ ] Evaluar positivos, habla negativa, ruido, silencio real y audio de la propia Karen.
- [ ] Calibrar umbral, warm-up, confirmaciones y cooldown con métricas; no validar por una sola muestra.
- [ ] Si requiere reentrenar, usar el plan de negativos de habla del historial y separar entrenamiento de inferencia.

Cierre: precisión útil en sesiones reales, tasa de falsas activaciones y latencia registradas; sin prometer fiabilidad por el antiguo 99,43 % de validación.

## 5. Interfaz y continuidad

- [ ] Separar configuración de uso diario y conversación; mostrar nodo, micrófono y estado de forma visible.
- [ ] Canalizar eventos de trabajadores al hilo principal; limitar solicitudes activas y ofrecer cancelación.
- [ ] Definir memoria por conversación y fronteras de acciones del sistema.
- [ ] Aplicar las skills de diseño pertinentes al stack elegido, luego revisar con el usuario.
- [ ] Guardar estado, evidencia y decisiones al cierre en Obsidian.

Cierre: recorrido completo con servidor disponible y no disponible, teclado, tamaños de ventana y errores. La estética se valida con el usuario, no mediante una afirmación del asistente.
