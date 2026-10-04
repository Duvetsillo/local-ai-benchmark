---
proyecto: Aetherion
tipo: ux
tags: [aetherion, gui, experiencia]
knowledge_id: vault-legacy-proyecto-aetherion-02-cliente-01-experiencia-y-pantallas
title: "Experiencia y pantallas"
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
> Esta composición corresponde al corte anterior. La revisión estructural posterior es [[Proyecto Aetherion/02_Cliente/06_Studio_Estructura_2026-10-03]].


# Experiencia y pantallas

## Marco

La composición actual en fuente usa Tkinter, título AETHERION Client, tamaño inicial 1200 × 820 y mínimo 1020 × 720. Contiene navegación lateral, encabezado contextual, estado de runtime y vistas de trabajo. Son dimensiones configuradas en código, no una garantía para todos los DPI.

## Vistas

- **Dashboard:** estado general, hardware, runtime, modelos y benchmark reciente.
- **Benchmarks:** configuración de ejecución, suite y explicación del laboratorio.
- **Models:** modelos disponibles, metadatos y orientación de compatibilidad.
- **Results:** resultados locales y resumen de validaciones.
- **Hardware:** perfil del equipo.
- **History:** ejecuciones guardadas.
- **Settings:** carpeta de modelos y configuración local.

La navegación debe cambiar el contenido de trabajo, no limitarse a decorar una sola pantalla.

## Jerarquía de información

1. Marca, vista activa y estado del cliente/runtime.
2. Resumen de runtime, modelos y última corrida.
3. Perfil de hardware y orientación de compatibilidad.
4. Configuración de benchmark, progreso, salida y acciones.
5. Resultados e historial locales.

## Acciones

Cambiar vista, refrescar modelos, elegir modelo y carpeta GGUF, descargar modelos del catálogo, obtener/instalar runtimes compatibles, ejecutar o detener un benchmark, revisar resultados y abrir su carpeta local. La instalación o ejecución de instaladores del sistema debe conservar consentimiento del usuario.

## Estados vacíos y fallos

Debe manejar ningún modelo, Ollama ausente, dependencias faltantes, hardware parcial, carpeta vacía, historial sin datos y proveedor no disponible. La explicación debe decir qué ocurrió y el siguiente paso útil.

## Criterios visuales

Jerarquía clara, contraste legible, éxito y error comunicados también con texto, espaciado y alineación coherentes, escalado Windows y resoluciones menores. El registro no debe desplazar controles esenciales.

La navegación y las siete vistas se reportaron implementadas en la sesión del 29-09-2026 y constan en el fuente actual. La apariencia del EXE más reciente no está confirmada: su último arranque observado mostró “Unhandled exception in script”. Ver [[Proyecto Aetherion/04_Calidad/02_Incidente_Arranque_Cliente]].

## Navegación documental

Volver a [[Proyecto Aetherion/02_Cliente/00_Mapa_Cliente]].
