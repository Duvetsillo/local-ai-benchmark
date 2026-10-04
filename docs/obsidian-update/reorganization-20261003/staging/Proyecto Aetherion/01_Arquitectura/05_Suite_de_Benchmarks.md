---
proyecto: Aetherion
tipo: suite
tags: [aetherion, evaluacion, validadores]
knowledge_id: vault-legacy-proyecto-aetherion-01-arquitectura-05-suite-de-benchmarks
title: "Suite de benchmarks"
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

# Suite de benchmarks

| Tarea | Categoría | Regla actual |
|---|---|---|
| dns_explanation | general | Debe resultar en dos frases. |
| duplicate_files | coding | Código Python compilable con nombre de función esperado. |
| deterministic_math | math | Debe aparecer el número 888. |
| json_profile | json | JSON válido con valores de perfil fijados. |
| spanish_summary | spanish | Debe contener palabras clave de memoria/datos/CPU. |

## Interpretación

true significa que el texto pasó esa regla; false que no la cumplió; null que no hubo una calificación binaria. Error de proveedor es un problema operativo, no una respuesta mala.

## Límites

Una explicación de dos frases puede ser falsa; incluir 888 no excluye texto incorrecto; código que compila puede ser lógicamente erróneo; una palabra clave no evalúa comprensión profunda. Presentar el resultado como señal exploratoria, no clasificación universal ni auditoría de seguridad.

## Repetibilidad

Mantener constantes modelo/version, backend, temperatura, contexto y tareas. Registrar hardware, runtime y parámetros. Si importa la variabilidad, repetir varias corridas y reportar distribución. No atribuir repeticiones estadísticas a la versión actual si aún no existen.

## Ampliación

Cada tarea nueva necesita prompt estable, categoría, regla clara y pruebas de éxito, fallo y límites. Describir qué mide y qué no mide junto a su implementación.

## Navegación documental

Volver a [[Proyecto Aetherion/01_Arquitectura/00_Mapa_Arquitectura]].
