---
proyecto: Aetherion
tipo: incidente
fecha: 2026-09-30
estado: resuelto-dependencia-faltante-corregida
tags: [aetherion, pyinstaller, tkinter, incidente]
knowledge_id: vault-legacy-proyecto-aetherion-04-calidad-02-incidente-arranque-cliente
title: "Incidente: “Unhandled exception in script”"
project: Aetherion
domain: 04_Calidad
note_type: reference
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/04_Calidad/00_Mapa_Calidad]]"]
related: []
replaces: []
source_refs: []
---

> [!info] Lectura al 3 de octubre de 2026
> Leer primero la sección «Causa raíz y resolución». Las hipótesis previas se conservan como historia del diagnóstico, no como estado actual.


# Incidente: “Unhandled exception in script”

## Resumen

La compilación PyInstaller finaliza, pero al abrir `downloads/Aetherion-Client.exe` se observa una instancia con el título **“Unhandled exception in script”**. No se obtuvo el traceback completo ni el texto interno del diálogo. El rediseño del fuente no basta para declarar la descarga funcional.

## Evidencia actualizada — 2026-09-30

- El fuente se analizó sintácticamente sin errores y su construcción de interfaz pudo llegar al bucle de eventos de Tkinter.
- PyInstaller 6.22.3 y Python 3.14.7 completaron el build.
- La copia de `downloads` y la salida de `dist` coincidían con SHA-256 `CCC88D3D9981743FD2FA812CD2EFCF6D4D42F2888F615924B663560F6B39AF37` durante la inspección.
- En lanzamientos desde la carpeta de descarga y desde el directorio raíz del repositorio se volvió a ver el título genérico de excepción.
- El proceso puede aparecer como `Responding=True` mientras el diálogo está abierto; esto no significa que el cliente esté operativo.
- No se capturó el mensaje expandido ni un traceback. La causa raíz del fallo empaquetado sigue sin determinarse.

## Error de UI conocido y ya corregido

Durante el rediseño, Tkinter indicó `TclError: unknown option "-padx"` en `Canvas.create_window`. El parámetro se retiró y el padding pasó al frame contenedor. Después de ese cambio la composición de la interfaz pudo inicializarse desde fuente. Esta es una excepción reproducida y corregida dentro del código UI; no se ha demostrado que explique el fallo del ejecutable empaquetado. Mantener ambos hechos separados hasta capturar evidencia nueva.

## Hipótesis todavía sin probar

- Excepción o importación que se comporta de modo distinto en el programa congelado.
- Recursos Tcl/Tk, DLL o dependencia no empaquetada.
- Ruta relativa o recurso requerido que falta en distribución.
- Incompatibilidad del runtime o una excepción temprana anterior a la ventana principal.

Ninguna de estas hipótesis debe tratarse como causa raíz sin traceback reproducible.

## Secuencia de diagnóstico

1. Recuperar el texto completo del diálogo (incluida la vista de detalles) o ejecutar una compilación con consola y depuración.
2. Registrar stdout y stderr completos sin truncamiento.
3. Confirmar qué archivo y proceso lanzan la ventana de error.
4. Contrastar el entrypoint fuente y el empaquetado, incluidas rutas y recursos.
5. Probar un cambio mínimo con salida aislada en carpeta temporal.
6. Abrir la compilación resultante y verificar que aparece el dashboard sin excepción.
7. Recorrer navegación, scroll, configuración, ejecución y resultados antes de reemplazar el artefacto estándar.

## Criterio de cierre

Cerrar solo después de obtener una ventana utilizable del EXE sin el diálogo genérico, revisar visualmente sus regiones principales y confirmar al menos un recorrido funcional de benchmark. Registrar hash, captura y configuración del build en [[Proyecto Aetherion/06_Historial/06_Rediseño_Interfaz_2026-09-30]].


## Relación con licencias (2026-09-30)

La activación se implementó en fuente en una continuación aparte. No corrige este fallo de arranque; mientras no se obtenga y solucione el traceback, el EXE no puede publicarse con la nueva puerta de licencia. Ver [[Proyecto Aetherion/06_Historial/07_Licenciamiento_Offline_2026-09-30]].

## Causa raíz y resolución — 2026-09-30

La nueva build reproducía el diálogo. El traceback indicaba `ModuleNotFoundError: No module named 'cryptography'` durante el import de `local_ai_benchmark.client.auth`; el Python 3.14.7 usado por PyInstaller no tenía instalada la dependencia declarada por el proyecto (`cryptography>=45.0`). El archivo de advertencias de PyInstaller confirmaba que el módulo estaba ausente.

Se instaló `cryptography 50.0.2` en ese entorno; PyInstaller ejecutó su hook de cryptography y `python build_client.py` terminó con código 0. Se cerró normalmente la instancia que tenía bloqueado el EXE, se actualizó `dist` y `downloads`, y se verificó que ambas copias corresponden a SHA-256 `949E8615E74EB298A3867BB454F768C2A00693AA9DF2E6DBBD85ABCC11656329`, tamaño 17,713,859 bytes. El archivo de descarga se abrió; el proceso presentó la ventana `AETHERION Client` y la pantalla de inicio de sesión/creación de cuenta, sin el diálogo de excepción. El cliente quedó al frente.

Este cierre resuelve el incidente de arranque observado en esta configuración; no equivale a una certificación universal del ejecutable ni a una validación end-to-end del servicio. El backend sigue sin despliegue porque falta dominio/VPS. La pantalla de acceso requiere una URL HTTPS configurada para autenticar usuarios. Mantener pendiente la prueba del flujo completo con servidor real y una licencia de ensayo.

Build: Python 3.14.7, PyInstaller 6.22.3, Windows 11. Fecha de archivo: 2026-09-30 18:53 local. No se ejecutó la suite automatizada.

Ver también [[Proyecto Aetherion/06_Historial/09_Cuentas_Servicio_Renovacion_2026-09-30#Cierre del incidente de arranque]].

## Navegación documental

Volver a [[Proyecto Aetherion/04_Calidad/00_Mapa_Calidad]].

Desglose temático: [[Proyecto Aetherion/04_Calidad/08_Cierre_Cryptography]].
