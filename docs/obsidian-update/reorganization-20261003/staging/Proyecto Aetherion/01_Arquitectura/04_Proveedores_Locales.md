---
proyecto: Aetherion
tipo: proveedores
tags: [aetherion, ollama, gguf]
knowledge_id: vault-legacy-proyecto-aetherion-01-arquitectura-04-proveedores-locales
title: "Proveedores locales"
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

# Proveedores locales

## Interfaz común

Los proveedores generan texto a partir de modelo, prompt, temperatura y contexto, y devuelven respuesta, tiempo hasta primer token, tiempo total y uso expuesto por el runtime. El router separa el motor del backend particular.

## Ollama

OllamaProvider usa por defecto http://127.0.0.1:11434, descubre modelos con /api/tags y genera en streaming mediante /api/generate. Concatena segmentos, toma tiempo de primer token y conserva métricas cuyo nombre termina en _duration o _count.

Los errores de red y parseo se traducen a ProviderError. Para una falla, confirmar servicio, endpoint y modelo instalado antes de cambiar código.

## llama.cpp y GGUF

LlamaCppProvider busca archivos .gguf en una carpeta configurable. llama-cpp-python se importa cuando se solicita generación, así que no es requisito para el flujo Ollama. La instancia cargada se conserva en memoria.

La aceleración GPU depende de build de llama-cpp-python, driver y compatibilidad. Ver un GGUF no garantiza que pueda cargarse ni que use GPU.

## Fallos comunes

Servicio inactivo, modelo no instalado, ruta inválida, dependencia ausente, memoria insuficiente, incompatibilidad del driver/runtime.

## Privacidad

El destino predeterminado es local. Si se configura un servidor remoto, cambia el destino de prompts y respuestas; documentarlo claramente y evitar credenciales en Obsidian.

## Navegación documental

Volver a [[Proyecto Aetherion/01_Arquitectura/00_Mapa_Arquitectura]].

Desglose temático: [[Proyecto Aetherion/01_Arquitectura/Proveedores/01_Ollama]] · [[Proyecto Aetherion/01_Arquitectura/Proveedores/02_LlamaCpp_GGUF]].
