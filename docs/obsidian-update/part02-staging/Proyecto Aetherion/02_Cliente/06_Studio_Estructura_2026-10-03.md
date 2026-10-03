---
knowledge_id: aetherion-studio03-06_studio_estructura_2026-10-03
title: Studio 03 — arquitectura de la experiencia
project: Aetherion
domain: cliente
note_type: decision
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

# Studio 03 — arquitectura de la experiencia

## Problema y dirección

El usuario indicó que la entrega Atelier seguía siendo «misma interfaz, diferentes colores». La corrección acepta que el objetivo no es cambiar solamente la apariencia: necesita una organización distinta de pantallas y tareas. Studio 03 conserva la paleta para que la revisión se pueda evaluar por su estructura.

Se sustituye la navegación lateral por navegación superior. Los destinos principales son Workspace, Models, Benchmark y Results. Hardware, History y Settings quedan en un segundo nivel visible. El acceso de cuenta existente y el motor de benchmarks se mantienen.

## Inicio y laboratorio separados

Workspace es un punto de partida: introducción, modelo sugerido por compatibilidad estimada, resumen del equipo, últimos experimentos y próximos pasos. El modelo sugerido permite preparar la configuración del benchmark. Si no hay modelos, el estado vacío permite iniciar la descarga. La sugerencia no se presenta como una victoria medida ni como una puntuación universal.

Benchmark aloja el formulario, la ejecución, la parada, los estados de progreso y el registro técnico. La consola ya no domina la pantalla inicial. El dock mantiene disponible la acción principal mientras la configuración se desplaza. El cambio se comprobó verificando que la consola no está visible en Workspace y sí en Benchmark.

## Biblioteca y resultados

Models presenta tarjetas de modelos con proveedor, precisión disponible, tamaño y compatibilidad estimada. Una búsqueda filtra por nombre o proveedor. Cada tarjeta permite preparar ese modelo en Benchmark. Las acciones de selección y actualización se deshabilitan durante operaciones.

Results presenta velocidades de generación mediante barras y una tabla de registros. Las barras usan el último dato disponible por modelo y muestran hasta cuatro modelos, ordenados por velocidad. La leyenda advierte que las suites pueden diferir. No se inventan velocidades, resultados o actividad. La tabla contiene las ejecuciones locales y permite ordenar por fecha, velocidad, número de checks aprobados o nombre. Enter, doble clic o el botón de apertura permiten consultar el registro guardado.

## Relación con documentación anterior

Esta revisión continúa [[Proyecto Aetherion/02_Cliente/05_Presencia_Atelier_2026-10-03]] y responde a la crítica posterior del usuario. La dirección se registra en el archivo de sistema visual MASTER de Aetherion Studio dentro del repositorio. [[Proyecto Aetherion/04_Calidad/07_Verificacion_Studio_2026-10-03]] identifica las pruebas realizadas y sus límites.

El nombre del ejecutable Studio 03 y su título de ventana distinguen esta entrega de los archivos anteriores que permanecen en uso. No se declara aceptada su estética hasta recibir evaluación del usuario.
