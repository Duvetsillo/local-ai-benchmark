---
knowledge_id: vault-20261003-proyecto-aetherion-04-calidad-08-cierre-cryptography
title: "Cierre del fallo de cryptography en el EXE"
project: Aetherion
domain: 04_Calidad
note_type: evidence
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/04_Calidad/00_Mapa_Calidad]]"]
related: []
replaces: []
source_refs: ["[[Proyecto Aetherion/04_Calidad/02_Incidente_Arranque_Cliente]]"]
tags: ["aetherion", "area/04-calidad", "evidence"]
---

# Cierre del fallo de cryptography en el EXE
Evidencia histórica de cierre. La corrección pertenece al entorno de build y a esa compilación; no demuestra autenticación online ni compatibilidad universal.

## Causa raíz y resolución — 2026-09-30

La nueva build reproducía el diálogo. El traceback indicaba `ModuleNotFoundError: No module named 'cryptography'` durante el import de `local_ai_benchmark.client.auth`; el Python 3.14.7 usado por PyInstaller no tenía instalada la dependencia declarada por el proyecto (`cryptography>=45.0`). El archivo de advertencias de PyInstaller confirmaba que el módulo estaba ausente.

Se instaló `cryptography 50.0.2` en ese entorno; PyInstaller ejecutó su hook de cryptography y `python build_client.py` terminó con código 0. Se cerró normalmente la instancia que tenía bloqueado el EXE, se actualizó `dist` y `downloads`, y se verificó que ambas copias corresponden a SHA-256 `949E8615E74EB298A3867BB454F768C2A00693AA9DF2E6DBBD85ABCC11656329`, tamaño 17,713,859 bytes. El archivo de descarga se abrió; el proceso presentó la ventana `AETHERION Client` y la pantalla de inicio de sesión/creación de cuenta, sin el diálogo de excepción. El cliente quedó al frente.

Este cierre resuelve el incidente de arranque observado en esta configuración; no equivale a una certificación universal del ejecutable ni a una validación end-to-end del servicio. El backend sigue sin despliegue porque falta dominio/VPS. La pantalla de acceso requiere una URL HTTPS configurada para autenticar usuarios. Mantener pendiente la prueba del flujo completo con servidor real y una licencia de ensayo.

Build: Python 3.14.7, PyInstaller 6.22.3, Windows 11. Fecha de archivo: 2026-09-30 18:53 local. No se ejecutó la suite automatizada.

Ver también [[Proyecto Aetherion/06_Historial/09_Cuentas_Servicio_Renovacion_2026-09-30#Cierre del incidente de arranque]].

## Procedencia y contexto

El contenido procede de [[Proyecto Aetherion/04_Calidad/02_Incidente_Arranque_Cliente]]. Conserva las condiciones de ese registro; no acredita una ejecución nueva durante la organización del vault.
