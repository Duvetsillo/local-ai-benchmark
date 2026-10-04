---
proyecto: Aetherion
tipo: flujo
tags: [aetherion, desktop, flujo]
knowledge_id: vault-legacy-proyecto-aetherion-01-arquitectura-02-flujo-del-cliente
title: "Flujo del cliente de escritorio"
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

# Flujo del cliente de escritorio

## Arranque

El punto de entrada desktop.py crea la raíz Tkinter y AetherionDesktopClient. La sesión prepara proveedor/router, motor, almacén, perfil básico y ruta de resultados. Después construye vistas y programa comprobación de dependencias y descubrimiento de modelos.

## Descubrimiento

Se consultan modelos de Ollama y archivos GGUF de una carpeta elegida. La presencia en la lista no garantiza que el runtime vaya a cargar el modelo ni que disponga de memoria suficiente.

## Selección

La persona elige modelo y suite o categoría. La interfaz muestra detalles y orientación. Una recomendación heurística no reemplaza una medición de rendimiento real.

## Ejecución

La acción inicia un benchmark en segundo plano. El motor obtiene hardware, resuelve tareas y pide cada generación al proveedor. La GUI recibe eventos para progreso y resultados.

## Validación y persistencia

Cada salida pasa por el validador correspondiente. Se recogen tiempos y métricas disponibles y se escribe un JSON. Los campos dependen del runtime; la falta de dato no debe interpretarse como cero.

## Revisión

Las vistas incluyen dashboard, modelos, resultados e historial. La acción para abrir la carpeta conduce a los archivos locales.

## Estados que la GUI debe comunicar

Conexión, descubrimiento, modelo ausente, dependencia faltante, corrida en progreso, éxito, salida no validada, error de proveedor y cierre durante corrida.

## Pendiente de evidencia

El flujo se deduce del código. No se confirmó visualmente cada vista ni se completó una corrida desde el ejecutable empaquetado.

## Navegación documental

Volver a [[Proyecto Aetherion/01_Arquitectura/00_Mapa_Arquitectura]].
