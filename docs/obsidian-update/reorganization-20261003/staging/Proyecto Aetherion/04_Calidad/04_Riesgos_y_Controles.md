---
proyecto: Aetherion
tipo: riesgos
tags: [aetherion, riesgos, calidad]
knowledge_id: vault-legacy-proyecto-aetherion-04-calidad-04-riesgos-y-controles
title: "Riesgos y controles"
project: Aetherion
domain: 04_Calidad
note_type: reference
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/04_Calidad/00_Mapa_Calidad]]"]
related: []
replaces: []
source_refs: []
---

> [!info] Lectura al 3 de octubre de 2026
> El fallo histórico de cryptography tiene cierre registrado. Los riesgos de DPI, autenticación online y benchmark real siguen pendientes; ver [[Proyecto Aetherion/00_Gobierno/02_Estado_Actual]].


# Riesgos y controles

| Riesgo | Impacto | Control |
|---|---|---|
| Error de arranque | Cliente distribuido inutilizable | Traceback, build de diagnóstico, prueba interactiva. |
| Validador simple | Sobreinterpretación de puntuación | Mostrar regla y límites. |
| Presión de memoria | Equipo lento o agotamiento de RAM | Mostrar hardware y permitir detener de forma segura. |
| Endpoint remoto | Cambia destino de prompts | Indicar servidor y revisar privacidad. |
| Resultados compartidos | Exposición de prompts/equipo | Inspección antes de compartir. |
| Runtime incompatible | Fallo o CPU fallback | Registrar build, driver y runtime efectivo. |
| Schema evoluciona | Historial antiguo deja de leerse | Versionado, migraciones y pruebas. |
| Imports ausentes en PyInstaller | Falla solo en empaquetado | Revisar warnings y validar en perfil limpio. |
| Documentación atrasada | Operación engañosa | Marcar fecha y fuente de cada estado. |

## Prioridad actual

El error genérico de arranque sigue abierto. No declarar estable el ejecutable hasta reproducir y cerrar el incidente. No inferir causa solo por advertencias de PyInstaller.

## Gestión

Convertir riesgo en acción con dueño, criterio de cierre y fecha. Diferenciar potencial de incidente observado.

## Navegación documental

Volver a [[Proyecto Aetherion/04_Calidad/00_Mapa_Calidad]].
