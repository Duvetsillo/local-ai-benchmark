---
proyecto: Aetherion
tipo: calidad
tags: [aetherion, pruebas, calidad]
knowledge_id: vault-legacy-proyecto-aetherion-04-calidad-01-estrategia-de-verificacion
title: "Estrategia de verificación"
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

# Estrategia de verificación

## Pruebas presentes

Hay pruebas para tareas, hardware, motor, core cliente y CLI. Su existencia no prueba que hayan pasado y no cubre por sí sola interacción visual empaquetada.

## Capas

### Importación

Comprobar imports del paquete y entrypoints bajo versión soportada de Python.

### Unidades

Validadores con casos positivos/negativos, serialización, almacenamiento local, JSON corrupto, errores provider y métricas ausentes.

### Integración

Descubrimiento con y sin Ollama; carga GGUF con runtime disponible/no disponible; benchmark corto; verificar salida JSON.

### GUI

Construir ventana, recorrer secciones, probar estados vacíos y errores, tamaños/DPI, cerrar y navegar con teclado.

### Paquete Windows

Ejecutar en perfil limpio sin depender del Python global; verificar Tcl/Tk, imports, datos, permisos, ventana, cierre, carpeta de resultados y corrida mínima. Comparar consola vs windowed.

## Criterio de aceptación visual

La ventana abre sin traceback; la paleta reciente aparece en el binario; controles esenciales responden; textos son legibles con escalado; no se modifica lógica fuera del alcance.

## Evidencia

Registrar fecha, commit, hash del exe, Windows, resolución/DPI, backend, modelo y resultado. En esta sesión no se ejecutó la suite. No registrar una build como funcional solo porque compiló.

## Navegación documental

Volver a [[Proyecto Aetherion/04_Calidad/00_Mapa_Calidad]].
