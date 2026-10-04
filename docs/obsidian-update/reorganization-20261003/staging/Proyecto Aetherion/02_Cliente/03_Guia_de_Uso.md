---
proyecto: Aetherion
tipo: guia-usuario
tags: [aetherion, cliente, guia]
knowledge_id: vault-legacy-proyecto-aetherion-02-cliente-03-guia-de-uso
title: "Guía de uso del cliente"
project: Aetherion
domain: 02_Cliente
note_type: reference
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/02_Cliente/00_Mapa_Cliente]]"]
related: []
replaces: []
source_refs: []
---

> [!info] Lectura al 3 de octubre de 2026
> Las advertencias de arranque pertenecen al corte histórico. El estado vigente está en [[Proyecto Aetherion/00_Gobierno/02_Estado_Actual]].


# Guía de uso del cliente

## Preparación

Para Ollama: iniciar el servicio y tener un modelo instalado. Para GGUF: confirmar la ruta, la extensión .gguf y el espacio disponible. Una corrida puede consumir recursos considerables.

## Flujo previsto

1. Abrir Aetherion Client.
2. Activar el cliente con una licencia válida para ese equipo.
3. Esperar el descubrimiento de modelos y runtimes disponibles.
4. Elegir un modelo Ollama o GGUF; se puede seleccionar una carpeta GGUF propia o descargar un modelo desde el cliente.
5. Revisar compatibilidad estimada, memoria requerida, runtime y requisitos faltantes. Es orientación heurística, no una garantía de ejecución.
6. Elegir suite completa o categoría e iniciar el benchmark.
7. Observar progreso y resultados por tarea; **Stop benchmark** solicita una detención cooperativa y conserva las tareas ya terminadas.
8. Revisar validaciones y abrir la carpeta local de resultados JSON.

El cliente puede descargar el instalador oficial de Ollama y solicitar su ejecución; la instalación puede requerir autorización de Windows. La disponibilidad de `llama-cpp-python` en el EXE depende de cómo se distribuya el runtime y no debe suponerse una instalación silenciosa.

## Lectura de estado

PASS significa que la respuesta pasó la regla concreta. CHECK FAILED significa que no cumplió ese criterio automático. ERROR apunta a fallo operativo del proveedor/runtime. Ninguno por sí solo expresa calidad global.

## Buenas prácticas

Cerrar cargas pesadas durante una comparación; conservar hardware y parámetros; detener la corrida si el equipo se queda sin memoria; anotar el texto de errores antes de cerrar.

## Estado de distribución

La sesión del 29-09-2026 reportó que la compilación abría y pasó nueve pruebas locales. En la comprobación posterior del 30-09-2026, el ejecutable distribuible mostró “Unhandled exception in script”; esa observación más reciente gobierna el estado actual. Esta guía describe el flujo previsto, no garantiza que el binario actual complete el arranque. Revisar [[Proyecto Aetherion/04_Calidad/02_Incidente_Arranque_Cliente]].

## Navegación documental

Volver a [[Proyecto Aetherion/02_Cliente/00_Mapa_Cliente]].
