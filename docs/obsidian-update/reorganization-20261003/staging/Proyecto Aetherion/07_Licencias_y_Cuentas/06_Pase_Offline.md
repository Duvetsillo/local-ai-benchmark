---
knowledge_id: vault-20261003-proyecto-aetherion-07-licencias-y-cuentas-06-pase-offline
title: "Pase offline y límites temporales"
project: Aetherion
domain: 07_Licencias_y_Cuentas
note_type: process
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/07_Licencias_y_Cuentas/00_Mapa_Licencias_y_Cuentas]]"]
related: []
replaces: []
source_refs: ["[[Proyecto Aetherion/06_Historial/09_Cuentas_Servicio_Renovacion_2026-09-30]]"]
tags: ["aetherion", "area/07-licencias-y-cuentas", "process"]
---

# Pase offline y límites temporales
El pase firmado ofrece continuidad limitada; no garantiza revocación instantánea de un dispositivo desconectado.

## Modelo y límites offline

El servidor firma un pase con `offline_until = última validación + 7 días`, limitado además por vencimiento de licencia + 7 días. El cliente lo almacena con DPAPI, verifica con la clave pública incluida en el pase y lo liga al Device ID actual. El cache recuerda `last_seen_utc` para detectar retroceso temporal del reloj en el modo offline.

El acceso offline es una tolerancia de continuidad, no una revocación instantánea: al desactivar una cuenta o cortar renovación, el usuario desconectado puede usar el pase que ya recibió hasta su fecha límite. El cierre de sesión elimina el cache local; por eso volver a iniciar sesión después de cerrar sesión requiere conectividad. Este comportamiento es parte del equilibrio acordado entre continuidad y control de acceso.

## Despliegue reproducible

Archivos fuente: `server/Dockerfile`, `server/compose.yaml`, `server/Caddyfile`, `server/.env.example`, `server/requirements.txt` y `server/README.md`.

1. Requiere VPS Linux, Docker Engine/Compose, dominio y puertos entrantes TCP 80/443. UDP 443 es opcional.
2. Sustituir todos los valores de ejemplo del `.env`; no reutilizar token de muestra.
3. Obtener `AETHERION_LICENSE_PUBLIC_KEY_N` de la constante pública actual. Confirmar que el generador y servidor usan la misma autoridad.
4. Usar `docker compose --env-file .env up -d --build`.
5. Guardar copias consistentes del volumen SQLite y volumen de certificados/datos Caddy; limitar acceso SSH y de archivos.
6. Probar alta, login, logout, renovación, desactivación y acceso offline con cuenta de ensayo antes de entregar.

No se ha desplegado una instancia pública al cierre de este hito: faltan dominio, VPS y secretos operativos. La dirección sigue editable para poder conectarlos después.

## Archivos cambiados en el repositorio

- `src/local_ai_benchmark/client/auth.py`: transporte HTTP, validación de HTTPS, sesión DPAPI, pase offline y control de huella/reloj.
- `src/local_ai_benchmark/client/desktop.py`: puerta de acceso, formularios, URL, recuperación de sesión, indicador de cuenta, cierre y bloqueo de benchmark.
- `server/app.py`: API FastAPI, SQLite, Argon2id, firma de pases, administración de licencia/usuario.
- `server/`: contenedor y despliegue Compose/Caddy, guía y configuración de ejemplo.
- `tools/Aetherion-License-Manager.ps1`: ajustes server-side protegidos, sincronización al emitir y panel de cuentas/renovaciones.
- `README.md`, `.gitignore`, `tools/README-License-Manager.md`: guía, exclusión de secretos y operación.
- Copia visual del License Manager en `C:\Users\Dayve\Desktop\Aetherion License Manager\`.

No se alteró la clave privada de firma existente ni se guardó su contenido en el repositorio o en Obsidian.

## Verificación y estado de entrega

Verificado en esta sesión:

- Análisis sintáctico AST de `desktop.py`, `auth.py` y `server/app.py` sin errores.
- Parser de PowerShell sin errores para el License Manager actualizado.
- Inspección estática de rutas y flujo de interfaz; no se ejecutó la suite automatizada ni una instancia VPS.

Pendiente antes de uso real/distribución:

1. Proveer dominio y VPS, reemplazar todos los secretos de ejemplo y desplegar HTTPS.
2. Probar de punta a punta contra el servicio desplegado y comprobar firewall, persistencia y copias de seguridad.
3. Build del cliente completada; `downloads/Aetherion-Client.exe` ahora refleja la integración de cuentas y se abrió correctamente. Hash y causa del fallo están en la sección de cierre.
4. Realizar recorrido funcional completo de autenticación, panel administrativo, benchmark y detención con el servicio de ensayo desplegado.
5. Compilar y abrir License Manager actualizado en el escritorio; confirmar conexión y flujo administrativo con una cuenta de prueba.
6. Realizar ensayo de renovación, suspensión, revocación y pase offline de siete días en dispositivos controlados.

El análisis sintáctico confirma que el código es parseable; no certifica dependencias, interfaces HTTP en un despliegue real, UI, build, seguridad integral ni experiencia de cliente. Mantener el estado como implementación de fuente pendiente de VPS, build y validación manual.

## Decisiones registradas

- Persistencia central en servidor propio/VPS, elección del usuario.
- Dirección pública todavía sin definir; URL configurable en cliente y administrador.
- Una licencia para un equipo; una cuenta por licencia.
- No emitir nueva clave para renovación pagada; cambiar la fecha en el servidor.
- Offline limitado a siete días de gracia.
- Benchmark y archivos locales; API central no recopila resultados.

## Continuidad sugerida

1. Retomar el diagnóstico del ejecutable documentado en [[Proyecto Aetherion/04_Calidad/02_Incidente_Arranque_Cliente]].
2. Obtener VPS/dominio y usar [[Proyecto Aetherion/06_Historial/09_Cuentas_Servicio_Renovacion_2026-09-30#Despliegue reproducible|el runbook de despliegue]].
3. Actualizar configuración de servidor seguro y ejecutar una prueba de aceptación completa, documentando solo datos ficticios.
4. Construir una versión firmada para distribución luego de validar el arranque de la versión nueva.

## Enlaces

- [[Proyecto Aetherion/00_Gobierno/00_MOC_Aetherion]]
- [[Proyecto Aetherion/00_Gobierno/02_Estado_Actual]]
- [[Proyecto Aetherion/06_Historial/07_Licenciamiento_Offline_2026-09-30]]
- [[Proyecto Aetherion/06_Historial/08_Generador_Licencias_y_Detener_Benchmark_2026-09-30]]
- [[Proyecto Aetherion/04_Calidad/04_Riesgos_y_Controles]]
- [[Proyecto Aetherion/05_Roadmap/02_Decisiones_Tecnicas]]

## Cierre del incidente de arranque

- Causa raíz reproducida en el ejecutable: faltaba `cryptography` en Python 3.14.7, por lo que PyInstaller no la podía empaquetar. El traceback acabó en `ModuleNotFoundError: No module named 'cryptography'` al importar `client/auth.py`.
- Instalada la dependencia `cryptography 50.0.2`; el hook oficial de PyInstaller la incorporó en el siguiente build.
- Compilación con Python 3.14.7 y PyInstaller 6.22.3 completada mediante `build_client.py` (salida `dist` y copia `downloads`).
- El ejecutable nuevo abrió la ventana Aetherion con su puerta de acceso. Identidad del archivo: 17,713,859 bytes, SHA-256 `949E8615E74EB298A3867BB454F768C2A00693AA9DF2E6DBBD85ABCC11656329`.
- Estado: el incidente de arranque reproducido queda resuelto en esta build. Falta la prueba integral contra VPS/dominio real y revisar flujos completos cuando el servicio esté configurado; no se ejecutó la suite automatizada.
- [[Proyecto Aetherion/04_Calidad/02_Incidente_Arranque_Cliente]]

## Procedencia y contexto

El contenido procede de [[Proyecto Aetherion/06_Historial/09_Cuentas_Servicio_Renovacion_2026-09-30]]. Conserva las condiciones de ese registro; no acredita una ejecución nueva durante la organización del vault.
