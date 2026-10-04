---
knowledge_id: vault-20261003-proyecto-aetherion-01-arquitectura-proveedores-01-ollama
title: "Proveedor Ollama"
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

# Proveedor Ollama
Ollama es un runtime externo al proceso Python, configurado localmente por defecto. Confirmar servicio y modelo antes de atribuir un fallo a la GUI.

## Interfaz común

Los proveedores generan texto a partir de modelo, prompt, temperatura y contexto, y devuelven respuesta, tiempo hasta primer token, tiempo total y uso expuesto por el runtime. El router separa el motor del backend particular.

## Ollama

OllamaProvider usa por defecto http://127.0.0.1:11434, descubre modelos con /api/tags y genera en streaming mediante /api/generate. Concatena segmentos, toma tiempo de primer token y conserva métricas cuyo nombre termina en _duration o _count.

Los errores de red y parseo se traducen a ProviderError. Para una falla, confirmar servicio, endpoint y modelo instalado antes de cambiar código.

## Privacidad

El destino predeterminado es local. Si se configura un servidor remoto, cambia el destino de prompts y respuestas; documentarlo claramente y evitar credenciales en Obsidian.

## Procedencia y contexto

El contenido procede de [[Proyecto Aetherion/01_Arquitectura/04_Proveedores_Locales]]. Conserva las condiciones de ese registro; no acredita una ejecución nueva durante la organización del vault.
