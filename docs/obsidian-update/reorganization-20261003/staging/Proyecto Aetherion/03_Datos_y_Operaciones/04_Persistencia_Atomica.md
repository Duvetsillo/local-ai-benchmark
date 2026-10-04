---
knowledge_id: vault-20261003-proyecto-aetherion-03-datos-y-operaciones-04-persistencia-atomica
title: "Persistencia atómica y lectura del historial"
project: Aetherion
domain: 03_Datos_y_Operaciones
note_type: process
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/03_Datos_y_Operaciones/00_Mapa_Datos_y_Operaciones]]"]
related: []
replaces: []
source_refs: ["[[Proyecto Aetherion/01_Arquitectura/07_Formato_de_Resultados]]"]
tags: ["aetherion", "area/03-datos-y-operaciones", "process"]
---

# Persistencia atómica y lectura del historial
Escritura atómica evita exponer un JSON parcialmente escrito. Ignorar un archivo ilegible al listar no significa que se haya reparado; conservarlo para diagnóstico.

## Persistencia del cliente

LocalResultStore escribe JSON por ID en una carpeta derivada, crea archivo temporal, vacía buffer, hace fsync y reemplaza atómicamente. Al listar, ignora archivos ilegibles o JSON inválido. pending_upload filtra registros con estados pending/failed; por sí solo no demuestra que exista subida remota.

## Compatibilidad y manejo

Los resultados incluyen prompts, salidas y detalles del equipo; inspeccionar antes de compartir. Antes de cambiar campos, versionar esquema, mantener lectores de versiones anteriores y cubrir migraciones con pruebas. Confirmar cuál componente produjo cada JSON antes de buscarlo.

## Procedencia y contexto

El contenido procede de [[Proyecto Aetherion/01_Arquitectura/07_Formato_de_Resultados]]. Conserva las condiciones de ese registro; no acredita una ejecución nueva durante la organización del vault.
