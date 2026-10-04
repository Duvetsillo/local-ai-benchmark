---
proyecto: Aetherion
tipo: mapa-artefactos
tags: [aetherion, archivos]
knowledge_id: vault-legacy-proyecto-aetherion-06-historial-04-mapa-de-artefactos
title: "Mapa de artefactos"
project: Aetherion
domain: 06_Historial
note_type: evidence
version: 1.0.0
status: archived
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/06_Historial/00_Mapa_Historial]]"]
related: []
replaces: []
source_refs: []
---

> [!info] Lectura al 3 de octubre de 2026
> Registro de sesión fechado. Para decidir qué está vigente, consultar [[Proyecto Aetherion/00_Gobierno/02_Estado_Actual]]; no ejecutar los procedimientos preliminares sin leer sus ampliaciones posteriores.


# Mapa de artefactos

## Raíz

C:/Users/Dayve/Desktop/Carpetas/Local_AI_Benchmark

## Desarrollo

- src/local_ai_benchmark: paquete Python.
- tests: suite automatizada.
- results: resultados/datos locales.
- README.md: guía principal.
- pyproject.toml: configuración del paquete.

## Cliente/build

- src/local_ai_benchmark/client/desktop.py: ventana y flujo.
- src/local_ai_benchmark/client/licensing.py: verificación local de licencias y vínculo al equipo.
- client/theme.py: tokens visuales.
- Aetherion-Client.spec: configuración PyInstaller.
- build_client.py: build y copia.
- build/version_info.txt: metadatos de Windows.
- dist/Aetherion-Client.exe: salida compilada.
- downloads/Aetherion-Client.exe: copia de distribución.

## Sitio y herramienta del propietario

- `index.html`, páginas secundarias, `app.js`/`app.ts` y `styles.css`: sitio público de Aetherion.
- `tools/Aetherion-License-Manager.ps1` y `tools/README-License-Manager.md`: fuente y guía del administrador de licencias.
- Copia de trabajo de la GUI administrativa: `C:\Users\Dayve\Desktop\Aetherion License Manager\`. La autoridad privada queda en `%LOCALAPPDATA%\Aetherion\licensing\`; no copiarla al vault.

## Datos de usuario

README ubica resultados por defecto en el perfil local de Windows. GGUF puede ocupar muchos GB. Verificar ruta antes de mover o limpiar datos.

No colocar resultados, modelos, claves o certificados dentro de esta documentación.

## Cuentas y servicio de licencias

- `client/auth.py`: autenticación, URL configurable, sesión segura DPAPI y pase offline.
- `server/`: API y despliegue de VPS Docker/Caddy; ejemplo sin secretos reales.
- `tools/Aetherion-License-Manager.ps1`: emisión/sync de licencias, importación de claves antiguas, lista y renovaciones de cuentas.
- [[Proyecto Aetherion/06_Historial/09_Cuentas_Servicio_Renovacion_2026-09-30]] — runbook extenso y estado preciso.

Nunca incluir el `.env` real, token administrativo, contraseñas, datos de cuentas ni llaves privadas en el vault.

## Navegación documental

Volver a [[Proyecto Aetherion/06_Historial/00_Mapa_Historial]].
