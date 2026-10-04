---
proyecto: Aetherion
tipo: mapa-codigo
tags: [aetherion, codigo, referencia]
knowledge_id: vault-legacy-proyecto-aetherion-01-arquitectura-03-mapa-del-codigo
title: "Mapa del código fuente"
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

# Mapa del código fuente

## Paquete local_ai_benchmark

| Archivo | Responsabilidad |
|---|---|
| __main__.py | Ejecutar paquete como módulo. |
| cli.py | Comandos de sistema, descubrimiento, benchmark y dashboard. |
| models.py | Dataclasses de hardware, modelo, tarea y resultado. |
| providers.py | Abstracción común y proveedores locales. |
| tasks.py | Tareas y reglas de validación. |
| engine.py | Orquestación de corrida, métricas y escritura JSON. |
| hardware.py | Perfil común de hardware. |
| web.py y web/ | Servidor y recursos del dashboard local. |

## Subpaquete client

- desktop.py: GUI Tkinter, navegación de siete vistas, activación, setup de runtimes, catálogo/descarga de modelos, eventos y arranque.
- theme.py: tokens de color y estilos ttk.
- core.py: identificador y registro de corrida.
- storage.py: persistencia local y lectura de historial.
- licensing.py: ID de equipo, validación y almacenamiento de licencias firmadas; la autoridad privada no pertenece al cliente.
- hardware.py: detección para el cliente.
- benchmark.py: flujo/adaptación de ejecución y cancelación cooperativa.
- api.py: operaciones de comunicación del cliente.
- updater.py: operaciones asociadas a actualización.
- ui.py y __main__.py: entrada alternativa; verificar relación antes de cambiarla.

`desktop.py` concentra varias interacciones del cliente; antes de ampliar su responsabilidad, comprobar si el flujo pertenece al motor, proveedor o almacenamiento.

## Producto web

- `index.html`, páginas de overview/models/compare y páginas legales, junto con `styles.css` y `app.js`/`app.ts`: sitio público de Aetherion.
- `src/local_ai_benchmark/web/`: dashboard local servido por el paquete Python; no confundirlo con el sitio público.

## Build

Aetherion-Client.spec elige punto de entrada y configuración PyInstaller. build_client.py invoca compilación, firma opcional y copia a downloads. pyproject.toml declara paquetes, extras y comandos.

## Pruebas listadas

test_tasks.py, test_hardware.py, test_engine.py, test_client_core.py, test_cli.py.

La lista de archivos no confirma que pasen. Consultar [[Proyecto Aetherion/04_Calidad/01_Estrategia_de_Verificacion]].

## Navegación documental

Volver a [[Proyecto Aetherion/01_Arquitectura/00_Mapa_Arquitectura]].
