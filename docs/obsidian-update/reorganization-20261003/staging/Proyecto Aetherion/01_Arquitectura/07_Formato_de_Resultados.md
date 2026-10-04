---
proyecto: Aetherion
tipo: resultados
tags: [aetherion, json, esquema]
knowledge_id: vault-legacy-proyecto-aetherion-01-arquitectura-07-formato-de-resultados
title: "Formato de resultados"
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

# Formato de resultados

## Resultado del motor

El JSON incluye schema_version, created_at, hardware y lista results. Cada elemento puede conservar modelo, proveedor, tarea, categoría, prompt, temperatura, contexto, respuesta, passed, error, hardware, métricas y uso bruto.

El motor organiza archivos por fecha y nombre de corrida con hora. El cliente también define ClientRunRecord: identificador AET-YYYYMMDD-XXXXXXXX, benchmark, versión de modelo, runtime, precisión, hardware, resultado, estado, versiones y notas.

## Persistencia del cliente

LocalResultStore escribe JSON por ID en una carpeta derivada, crea archivo temporal, vacía buffer, hace fsync y reemplaza atómicamente. Al listar, ignora archivos ilegibles o JSON inválido. pending_upload filtra registros con estados pending/failed; por sí solo no demuestra que exista subida remota.

## Ejemplo conceptual

    {
      "schema_version": 1,
      "created_at": "ISO-8601 UTC",
      "hardware": {},
      "results": [{
        "model": "nombre-local",
        "provider": "ollama",
        "task": "deterministic_math",
        "passed": true,
        "error": null,
        "metrics": {}
      }]
    }

Este es un ejemplo, no un resultado real.

## Compatibilidad y manejo

Los resultados incluyen prompts, salidas y detalles del equipo; inspeccionar antes de compartir. Antes de cambiar campos, versionar esquema, mantener lectores de versiones anteriores y cubrir migraciones con pruebas. Confirmar cuál componente produjo cada JSON antes de buscarlo.

## Navegación documental

Volver a [[Proyecto Aetherion/01_Arquitectura/00_Mapa_Arquitectura]].

Desglose temático: [[Proyecto Aetherion/01_Arquitectura/Resultados/01_JSON_del_Motor]] · [[Proyecto Aetherion/03_Datos_y_Operaciones/04_Persistencia_Atomica]].
