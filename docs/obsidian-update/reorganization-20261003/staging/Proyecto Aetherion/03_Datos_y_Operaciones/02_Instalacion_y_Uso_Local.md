---
proyecto: Aetherion
tipo: operaciones
tags: [aetherion, setup, local]
knowledge_id: vault-legacy-proyecto-aetherion-03-datos-y-operaciones-02-instalacion-y-uso-local
title: "Instalación y operación"
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

> [!info] Lectura al 3 de octubre de 2026
> El texto anterior conserva una advertencia de arranque ya cerrada para una build. La entrega Studio 03 y sus límites se registran en [[Proyecto Aetherion/00_Gobierno/02_Estado_Actual]].


# Instalación y operación

## Requisitos documentados

Python 3.11+ para desarrollar; Ollama para ese backend; psutil opcional para telemetría; nvidia-smi opcional para GPU NVIDIA; llama-cpp-python opcional para GGUF; PyInstaller para construir el cliente.

## Cliente distribuido

El README dice descargar downloads/Aetherion-Client.exe, abrir, elegir modelo/suite y consultar JSON local. La versión actual requiere resolver el incidente de arranque primero.

## Desarrollo

El README propone entorno virtual, instalación de extras, comandos CLI y dashboard local. Aislar el Python de desarrollo facilita reproducir build y no depender de paquetes globales.

## Ollama

Endpoint esperado: http://127.0.0.1:11434. Revisar que el servicio responda y que ollama list muestre el modelo. Evitar lanzar una segunda instancia de servidor si ya existe una activa.

## GGUF

Elegir carpeta personalizada o usar la predeterminada del proveedor. Los modelos pueden ocupar muchos GB y requerir runtime compatible. GPU depende del build de llama-cpp-python.

## Operación prudente

Ejecutar con el equipo estable; cerrar cargas competidoras; no instalar runtime sin revisar compatibilidad; capturar mensajes exactos; registrar versiones de Python, PyInstaller, runtime y driver al diagnosticar.

## Navegación documental

Volver a [[Proyecto Aetherion/03_Datos_y_Operaciones/00_Mapa_Datos_y_Operaciones]].
