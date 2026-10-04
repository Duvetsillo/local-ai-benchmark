---
knowledge_id: vault-20261003-00-navegacion-guia-del-grafo
title: "Cómo recorrer el grafo"
project: Ecosistema
domain: navegacion
note_type: reference
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[00_MOC_Obsidian]]"]
related: []
replaces: []
source_refs: []
tags: ["ecosistema", "area/navegacion", "reference"]
---

# Cómo recorrer el grafo
## Estructura

Mapa general → proyecto → mapa de área → notas específicas. Los enlaces laterales unen conceptos que comparten un procedimiento o una condición; no se enlaza cada nota con todas las demás para aumentar artificialmente el número de líneas.

## Lectura visual

El grafo utiliza grupos por ruta: navegación, Aetherion, Ultron, Karen y Friday. Las carpetas de los dos últimos permanecen intactas. Aetherion tiene colores por área para identificar arquitectura, cliente, operaciones, evidencia, licencias y herramientas.

Se ocultan adjuntos y etiquetas como nodos; se mantienen visibles notas huérfanas y referencias no resueltas para no esconder defectos del contenido preservado. La distancia de enlaces se reduce y la repulsión aumenta respecto al ajuste anterior.

## Recorrido práctico

1. Abrir el grafo local de una nota de área.
2. Usar profundidad 1 para su familia y 2 para ver contexto.
3. En el grafo global filtrar por `path:"Proyecto Aetherion"` o `path:"Proyecto Ultron"` cuando se quiera revisar un proyecto.
4. Volver al mapa general para cambiar de rama.

La disposición exacta depende de la simulación de fuerzas y el tamaño de ventana. No es un diagrama con coordenadas fijas. No se requiere otro plugin.
