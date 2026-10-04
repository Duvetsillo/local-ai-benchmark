---
proyecto: Aetherion
tipo: arquitectura
tags: [aetherion, arquitectura, python]
knowledge_id: vault-legacy-proyecto-aetherion-01-arquitectura-01-arquitectura-general
title: "Arquitectura general"
project: Aetherion
domain: 01_Arquitectura
note_type: reference
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/01_Arquitectura/00_Mapa_Arquitectura]]"]
related: []
replaces: []
source_refs: []
---

# Arquitectura general

## Vista por capas

Usuario → interfaz Tkinter / CLI / dashboard local → BenchmarkEngine → suite de tareas y validadores → proveedor → Ollama local o llama.cpp/GGUF → resultado JSON local.

En paralelo, el motor obtiene un perfil de hardware y métricas que los runtimes exponen.

## Componentes principales

- models.py define estructuras de hardware, modelos, tareas y resultados.
- tasks.py declara prompts, categorías y reglas de validación.
- providers.py define protocolo de generación, proveedor Ollama, proveedor llama.cpp y router.
- engine.py orquesta tareas, tiempos, métricas y persistencia del benchmark.
- client/ contiene la interfaz, registro del cliente, almacenamiento y perfil del equipo.
- cli.py ofrece comandos de operación.
- web.py y web/ sirven un dashboard local.

## Dependencias opcionales

psutil amplía telemetría de CPU/RAM; nvidia-smi puede obtener datos de GPU NVIDIA; llama-cpp-python permite inferencia GGUF. Ollama es un servicio externo al proceso Python, pero se configura localmente por defecto.

## Modelo de ejecución de la GUI

El hilo principal crea widgets y ejecuta el ciclo Tkinter. Operaciones lentas se realizan en segundo plano y comunican eventos de progreso a la vista. Mantener actualizaciones de widgets en el hilo principal.

## Fronteras

El prompt va al proveedor seleccionado. Las respuestas, telemetría e información del equipo entran al JSON local. Un endpoint remoto cambia la frontera de privacidad. Los resultados requieren inspección antes de compartir.

## Riesgos

Diferencias entre entorno Python y ejecutable congelado, métricas incompletas, validadores simples, versiones de runtime incompatibles y migración futura de JSON.

## Navegación documental

Volver a [[Proyecto Aetherion/01_Arquitectura/00_Mapa_Arquitectura]].
