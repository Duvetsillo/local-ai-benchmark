---
proyecto: Aetherion
tipo: alcance
tags: [aetherion, producto, principios]
knowledge_id: vault-legacy-proyecto-aetherion-00-gobierno-03-alcance-y-principios
title: "Alcance y principios"
project: Aetherion
domain: 00_Gobierno
note_type: reference
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/00_Gobierno/00_Mapa_Gobierno]]"]
related: []
replaces: []
source_refs: []
---

# Alcance y principios

## Objetivo

Ayudar a comparar modelos locales en el propio equipo. Cada corrida debe conservar contexto suficiente: modelo, proveedor, tareas, parámetros, hardware y métricas disponibles.

## Incluido

1. Perfil básico del hardware y detección de capacidades.
2. Descubrimiento con Ollama y archivos GGUF.
3. Suite pequeña de tareas.
4. Validación automática por tarea.
5. Resultados JSON locales.
6. Cliente Tkinter para selección y ejecución.
7. CLI y dashboard local descritos por el README.
8. Extensión de proveedores y tareas a través del código.

## Fuera del alcance confirmado

- Servicios remotos como backend predeterminado.
- Telemetría o carga automática a la nube.
- Afirmar que una regla simple representa toda la calidad.
- Garantizar aceleración GPU idéntica entre equipos.
- Proclamar evidencia científica sin repeticiones y protocolo.
- Modificar web o configuración al atender una solicitud exclusivamente visual.

## Principios

### Localidad y privacidad

La inferencia usa el proveedor configurado. Los resultados quedan en archivos locales. Si se configura un endpoint remoto, debe informarse claramente: la privacidad deja de ser idéntica a la ejecución en el propio dispositivo.

### Comparabilidad

Una métrica sin contexto puede engañar. Registrar proveedor, versión del modelo, parámetros, hardware, tiempo, resultado de tarea y datos no disponibles.

### Transparencia

Los campos desconocidos se presentan como desconocidos o nulos. No inventar telemetría ni convertir una ausencia en cero.

### Evolución

El roadmap no es funcionalidad implementada. Separar actual, planeado, observado e inferido.

### Control de alcance

Cuando la tarea pida solo apariencia, limitar el cambio a colores, tipografía, tamaño, espaciado, alineación, bordes y estados visuales. No cambiar providers, resultados, tareas, almacenamiento, web ni configuración.

## Navegación documental

Volver a [[Proyecto Aetherion/00_Gobierno/00_Mapa_Gobierno]].
