---
proyecto: Aetherion
tipo: privacidad
tags: [aetherion, privacidad, datos-locales]
knowledge_id: vault-legacy-proyecto-aetherion-03-datos-y-operaciones-01-privacidad-y-almacenamiento
title: "Privacidad y almacenamiento"
project: Aetherion
domain: 03_Datos_y_Operaciones
note_type: reference
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/03_Datos_y_Operaciones/00_Mapa_Datos_y_Operaciones]]"]
related: []
replaces: []
source_refs: []
---

# Privacidad y almacenamiento

## Declaración documentada

El README dice que no hay telemetría ni llamadas a APIs en la nube. Los prompts van al proveedor seleccionado. Si se configura un endpoint remoto, cambia esa garantía contextual y debe advertirse con claridad.

## Datos potenciales

Nombre de modelo/proveedor, categoría/tarea, prompt, respuesta, estado de validación, error, detalles del equipo, tiempos, métricas, fecha y parámetros. Esto permite reproducibilidad y también puede revelar información técnica.

## Ubicación

La guía del repositorio indica %LOCALAPPDATA%/Aetherion/results. El cliente acepta base_dir personalizado. El motor y LocalResultStore escriben formatos/rutas diferentes: identificar el productor antes de buscar o limpiar archivos.

## Reglas

1. Inspeccionar JSON/capturas antes de compartir.
2. No guardar contraseñas, certificados o API keys en las notas.
3. Mantener modelos grandes fuera del repositorio.
4. Respaldar corridas importantes.
5. Revisar permisos y espacio libre.
6. Evitar capturas con nombre de usuario o rutas privadas.

No está documentada una política automática de retención. Asumir que los archivos permanecen hasta que se gestionen. Una función futura de limpieza debe mostrar alcance, periodo y opciones de respaldo.

## Navegación documental

Volver a [[Proyecto Aetherion/03_Datos_y_Operaciones/00_Mapa_Datos_y_Operaciones]].
