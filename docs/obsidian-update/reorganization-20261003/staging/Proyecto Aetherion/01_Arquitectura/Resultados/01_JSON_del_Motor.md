---
knowledge_id: vault-20261003-proyecto-aetherion-01-arquitectura-resultados-01-json-del-motor
title: "JSON del motor de evaluación"
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
source_refs: ["[[Proyecto Aetherion/01_Arquitectura/07_Formato_de_Resultados]]"]
tags: ["aetherion", "area/01-arquitectura", "process"]
---

# JSON del motor de evaluación
Distingue el formato de salida del motor del registro usado por el cliente. El ejemplo conservado es conceptual, no una corrida real.

## Resultado del motor

El JSON incluye schema_version, created_at, hardware y lista results. Cada elemento puede conservar modelo, proveedor, tarea, categoría, prompt, temperatura, contexto, respuesta, passed, error, hardware, métricas y uso bruto.

El motor organiza archivos por fecha y nombre de corrida con hora. El cliente también define ClientRunRecord: identificador AET-YYYYMMDD-XXXXXXXX, benchmark, versión de modelo, runtime, precisión, hardware, resultado, estado, versiones y notas.

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

## Procedencia y contexto

El contenido procede de [[Proyecto Aetherion/01_Arquitectura/07_Formato_de_Resultados]]. Conserva las condiciones de ese registro; no acredita una ejecución nueva durante la organización del vault.
