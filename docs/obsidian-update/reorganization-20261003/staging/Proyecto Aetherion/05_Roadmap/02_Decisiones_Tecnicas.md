---
proyecto: Aetherion
tipo: ADR
tags: [aetherion, decisiones]
knowledge_id: vault-legacy-proyecto-aetherion-05-roadmap-02-decisiones-tecnicas
title: "Registro de decisiones técnicas"
project: Aetherion
domain: 05_Roadmap
note_type: reference
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/05_Roadmap/00_Mapa_Roadmap]]"]
related: []
replaces: []
source_refs: []
---

# Registro de decisiones técnicas

## D001 — Ejecución local por defecto

Ollama o llama.cpp mantienen prompts en proveedor local configurado. Si se usa endpoint remoto, actualizar explícitamente la declaración de privacidad.

## D002 — Abstracción de proveedores

El motor usa protocolo común, así tareas y scoring no dependen directamente de un backend. Cada provider debe registrar qué métricas expone.

## D003 — Resultados JSON locales

Formato fácil de inspeccionar y copiar. Consecuencia: necesita política de retención y versionado.

## D004 — Tareas separadas de reglas

Cada tarea define prompt, categoría y validador. Cada regla requiere pruebas y documentación de límites.

## D005 — GUI Tkinter

Cliente ligero integrado con Python. Consecuencia: Tcl/Tk, escalado y PyInstaller requieren prueba empaquetada.

## D006 — Alcance visual

La solicitud anterior pidió refinar solo lo visual del cliente, sin página ni configuración. Preservar lógica y web ante nuevas mejoras visuales.

## D007 — No declarar release sin abrir

Una compilación exitosa no prueba que se pueda iniciar. Exigir evidencia de arranque visible.

## D008 — Activación offline ligada al equipo

El cliente valida localmente claves firmadas y vinculadas a un ID de equipo. El propietario mantiene el generador y la autoridad privada fuera del cliente; la clave privada se protege con DPAPI en Windows. Esta decisión no proporciona revocación remota ni resistencia a manipulación del equipo. Implementada en fuente; queda pendiente validar el flujo en un EXE funcional.

## D009 — Detención cooperativa del benchmark

La solicitud de Stop se propaga entre fragmentos del proveedor; se descarta la tarea interrumpida y se conservan los resultados de tareas terminadas. No es una interrupción instantánea si el proveedor está bloqueado esperando datos.

## Plantilla ADR

- Fecha y estado:
- Contexto:
- Decisión:
- Alternativas:
- Consecuencias:
- Reversión o revisión prevista:

## Navegación documental

Volver a [[Proyecto Aetherion/05_Roadmap/00_Mapa_Roadmap]].
