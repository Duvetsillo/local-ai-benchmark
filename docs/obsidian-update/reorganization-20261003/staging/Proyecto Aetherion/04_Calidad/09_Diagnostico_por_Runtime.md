---
knowledge_id: vault-20261003-proyecto-aetherion-04-calidad-09-diagnostico-por-runtime
title: "Diagnóstico de runtimes y resultados"
project: Aetherion
domain: 04_Calidad
note_type: process
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/04_Calidad/00_Mapa_Calidad]]"]
related: []
replaces: []
source_refs: ["[[Proyecto Aetherion/04_Calidad/03_Guia_de_Diagnostico]]"]
tags: ["aetherion", "area/04-calidad", "process"]
---

# Diagnóstico de runtimes y resultados
Recorrido de diagnóstico por síntoma. Registrar el mensaje exacto, productor del archivo y entorno antes de cambiar configuración.

## Ollama no descubierto

Confirmar servicio, ollama list y /api/tags en 127.0.0.1:11434. Capturar error HTTP/timeout antes de variar código.

## GGUF visible pero no carga

Verificar extensión, ruta, espacio, llama-cpp-python y compatibilidad GPU/CPU. El archivo visible no garantiza carga.

## Sin métricas GPU

Revisar nvidia-smi; distinguir detección de aceleración real. Aceptar unknown/null en equipo sin proveedor de telemetría.

## JSON ausente

Revisar directorio elegido, permisos, espacio, fecha y si el motor o el cliente generó el archivo. Conservar error; no borrar temporales sin revisarlos.

## Reporte de error

Fecha:
    Commit:
    Hash del exe:
    Windows/DPI:
    Python/PyInstaller:
    Acción:
    Error exacto:
    Desde fuente también falla:
    Proveedor/modelo:
    Ruta de resultados:

## Procedencia y contexto

El contenido procede de [[Proyecto Aetherion/04_Calidad/03_Guia_de_Diagnostico]]. Conserva las condiciones de ese registro; no acredita una ejecución nueva durante la organización del vault.
