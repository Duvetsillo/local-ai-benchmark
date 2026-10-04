---
knowledge_id: vault-20261003-proyecto-aetherion-01-arquitectura-proveedores-02-llamacpp-gguf
title: "Proveedor llama.cpp y GGUF"
project: Aetherion
domain: 01_Arquitectura
note_type: process
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/01_Arquitectura/00_Mapa_Arquitectura]]"]
related: []
replaces: []
source_refs: ["[[Proyecto Aetherion/01_Arquitectura/04_Proveedores_Locales]]"]
tags: ["aetherion", "area/01-arquitectura", "process"]
---

# Proveedor llama.cpp y GGUF
La carpeta contiene archivos de modelo; el backend y sus dependencias determinan si pueden ejecutarse. La presencia de un archivo no acredita carga ni aceleración.

## llama.cpp y GGUF

LlamaCppProvider busca archivos .gguf en una carpeta configurable. llama-cpp-python se importa cuando se solicita generación, así que no es requisito para el flujo Ollama. La instancia cargada se conserva en memoria.

La aceleración GPU depende de build de llama-cpp-python, driver y compatibilidad. Ver un GGUF no garantiza que pueda cargarse ni que use GPU.

## Fallos comunes

Servicio inactivo, modelo no instalado, ruta inválida, dependencia ausente, memoria insuficiente, incompatibilidad del driver/runtime.

## Privacidad

El destino predeterminado es local. Si se configura un servidor remoto, cambia el destino de prompts y respuestas; documentarlo claramente y evitar credenciales en Obsidian.

## Procedencia y contexto

El contenido procede de [[Proyecto Aetherion/01_Arquitectura/04_Proveedores_Locales]]. Conserva las condiciones de ese registro; no acredita una ejecución nueva durante la organización del vault.
