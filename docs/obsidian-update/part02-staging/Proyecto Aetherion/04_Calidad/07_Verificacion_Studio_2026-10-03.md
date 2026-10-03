---
knowledge_id: aetherion-studio03-07_verificacion_studio_2026-10-03
title: Studio 03 — evidencia y límites
project: Aetherion
domain: cliente
note_type: evidence
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[00-Home/Project Home]]"]
related: []
replaces: []
source_refs: [CHAT-20261003-C, REPO-20261003-C]
tags: [aetherion, studio, continuidad]
---

# Studio 03 — evidencia y límites

## Comprobaciones

La suite existente pasó: 18 pruebas. Una comprobación de interfaz con datos temporales recorrió ventanas de 1020×720, 1200×820 y 1600×1000. Verificó la separación entre Workspace y Benchmark, la selección del modelo desde la tarjeta sugerida, la visibilidad del botón de ejecución en el laboratorio, su foco, la búsqueda de modelos, el estado sin coincidencias y la restauración de la colección al limpiar la búsqueda.

Se crearon dos registros ficticios únicamente en una carpeta temporal de prueba. La comprobación confirmó dos filas en la tabla, el orden de velocidad descendente y el valor numérico correspondiente en el gráfico. Los registros de prueba no se importaron en la colección del usuario. No se ejecutaron modelos reales.

Se probaron acciones deshabilitadas durante operaciones y habilitadas después. Se midieron 12 combinaciones de texto principal, secundario, muted y quiet sobre las superficies canvas, surface y surface_elevated. Todas superaron 4,5:1; el mínimo fue 5,71:1. Esto no certifica todos los estados o controles ni una norma completa de accesibilidad.

## Aplicación de la habilidad de diseño

Se leyó completamente la salida de ui-ux-pro-max y sus referencias. La primera propuesta Enterprise Gateway con Brutalism no encajaba. Se hizo una única búsqueda más precisa: Data-Dense Dashboard sí aportó una dirección apropiada para datos, pero el patrón comercial se descartó. No se persistió esa plantilla comercial como autoridad del producto.

La búsqueda Compare Categories recomendó barras con etiquetas y tabla complementaria. La aplicación utiliza Canvas para el gráfico y Treeview nativo para los registros, adaptando la recomendación al stack real Tkinter. No existe una guía de Tkinter en los stacks de la habilidad, por lo que las decisiones específicas se apoyan en el código y en reglas generales verificables.

## Límites pendientes

La aplicación sigue usando Tkinter. Esta revisión no incorpora un framework nuevo, pero sí cambia composición, navegación y flujos de presentación. No se hizo una auditoría con lector de pantalla, una revisión de capturas completa ni una autenticación online. Tampoco se ensayaron todas las escalas DPI. Las guías móviles de safe areas y tamaños de pantalla de teléfono no corresponden a este cliente Windows.

La compilación completó correctamente. Se inspeccionó el ejecutable final: incluye la identidad STUDIO 03, el módulo de layouts Studio y Tcl. Se entrega como Aetherion-Studio-03.exe. La documentación no atribuye aceptación estética ni éxito comercial a pruebas funcionales.
