---
knowledge_id: vault-20261003-proyecto-aetherion-01-arquitectura-08-cancelacion-cooperativa
title: "Cancelación cooperativa del benchmark"
project: Aetherion
domain: 01_Arquitectura
note_type: process
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/01_Arquitectura/00_Mapa_Arquitectura]]"]
related: []
replaces: []
source_refs: ["[[Proyecto Aetherion/06_Historial/08_Generador_Licencias_y_Detener_Benchmark_2026-09-30]]"]
tags: ["aetherion", "area/01-arquitectura", "process"]
---

# Cancelación cooperativa del benchmark
La acción Stop conserva las tareas terminadas y descarta la respuesta incompleta. La cancelación depende de que el proveedor avance o libere la lectura; no es instantánea.

## Botón Stop benchmark

El panel de ejecución ahora presenta **Stop benchmark** junto al control de inicio. Permanece deshabilitado mientras no hay una ejecución y se activa al iniciar un benchmark. Al pulsarlo:

1. La interfaz señaliza un evento de cancelación y presenta el estado **STOPPING BENCHMARK**.
2. El proveedor interrumpe su bucle al recibir el siguiente fragmento del flujo del modelo.
3. El motor descarta la tarea que estaba generándose para no tratar una salida parcial como una respuesta completa.
4. Los resultados de tareas que terminaron antes de la solicitud se mantienen y se escriben localmente.
5. El registro resume la ejecución con estado `stopped` e incluye `stopped_by_user: true`.
6. La interfaz vuelve a habilitar los controles al recibir la finalización.

La detención es cooperativa. En una respuesta Ollama, el cierre se procesa cuando llega el siguiente bloque de datos del stream; si el runtime no envía más bloques, puede tardar hasta que el timeout de la solicitud o del proveedor libere la lectura. En llama.cpp se comprueba el evento entre elementos del iterador, también cooperativamente. Cerrar la ventana mientras hay trabajo solicita detenerlo antes de cerrar.

## Procedencia y contexto

El contenido procede de [[Proyecto Aetherion/06_Historial/08_Generador_Licencias_y_Detener_Benchmark_2026-09-30]]. Conserva las condiciones de ese registro; no acredita una ejecución nueva durante la organización del vault.
