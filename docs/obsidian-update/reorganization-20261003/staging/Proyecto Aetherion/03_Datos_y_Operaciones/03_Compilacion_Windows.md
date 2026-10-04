---
proyecto: Aetherion
tipo: build
tags: [aetherion, pyinstaller, windows]
knowledge_id: vault-legacy-proyecto-aetherion-03-datos-y-operaciones-03-compilacion-windows
title: "Compilación Windows"
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

# Compilación Windows

## Archivos

- Aetherion-Client.spec define entrypoint y opciones PyInstaller.
- build/version_info.txt describe recursos/versiones Windows.
- build_client.py compila, firma opcional y copia salida.
- dist/Aetherion-Client.exe es salida de build.
- downloads/Aetherion-Client.exe es copia distribuible.

## Script

build_client.py corre PyInstaller con limpieza, revisa que exista el ejecutable, lo firma si hay variable AETHERION_CERTIFICATE y lo copia a downloads. La firma puede requerir variables de entorno protegidas. Nunca versionar certificados ni contraseñas.

## Release prudente

1. Revisar commit y árbol de trabajo.
2. Usar entorno y versión Python conocidos.
3. Instalar dependencias de build.
4. Compilar en limpio y guardar el log completo.
5. Revisar hash, tamaño, warnings y recursos.
6. Abrir en sesión interactiva.
7. Verificar dashboard, flujo simple y archivo JSON.
8. Revisar firma si aplica.
9. Decidir explícitamente si el binario se versiona.

## Depuración

Construir un artefacto temporal con consola y el mismo entrypoint; no sobrescribir distribución con un debug build. Capturar traceback, imports y rutas congeladas. Que PyInstaller finalice solo prueba que generó un archivo, no que la app abre.

## Navegación documental

Volver a [[Proyecto Aetherion/03_Datos_y_Operaciones/00_Mapa_Datos_y_Operaciones]].
