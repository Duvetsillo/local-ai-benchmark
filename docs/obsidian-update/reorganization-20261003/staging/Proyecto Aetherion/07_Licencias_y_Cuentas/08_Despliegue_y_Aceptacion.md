---
knowledge_id: vault-20261003-proyecto-aetherion-07-licencias-y-cuentas-08-despliegue-y-aceptacion
title: "Despliegue y aceptación del servicio"
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

# Despliegue y aceptación del servicio
Runbook del servicio y pendientes históricos. La build del cliente sí tiene corrección posterior; el despliegue y recorrido completo permanecen sin evidencia nueva.

## Despliegue reproducible

Archivos fuente: `server/Dockerfile`, `server/compose.yaml`, `server/Caddyfile`, `server/.env.example`, `server/requirements.txt` y `server/README.md`.

1. Requiere VPS Linux, Docker Engine/Compose, dominio y puertos entrantes TCP 80/443. UDP 443 es opcional.
2. Sustituir todos los valores de ejemplo del `.env`; no reutilizar token de muestra.
3. Obtener `AETHERION_LICENSE_PUBLIC_KEY_N` de la constante pública actual. Confirmar que el generador y servidor usan la misma autoridad.
4. Usar `docker compose --env-file .env up -d --build`.
5. Guardar copias consistentes del volumen SQLite y volumen de certificados/datos Caddy; limitar acceso SSH y de archivos.
6. Probar alta, login, logout, renovación, desactivación y acceso offline con cuenta de ensayo antes de entregar.

No se ha desplegado una instancia pública al cierre de este hito: faltan dominio, VPS y secretos operativos. La dirección sigue editable para poder conectarlos después.

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

## Procedencia y contexto

El contenido procede de [[Proyecto Aetherion/06_Historial/09_Cuentas_Servicio_Renovacion_2026-09-30]]. Conserva las condiciones de ese registro; no acredita una ejecución nueva durante la organización del vault.

Consulta [[Proyecto Aetherion/00_Gobierno/02_Estado_Actual]] para el corte vigente y [[Proyecto Aetherion/04_Calidad/02_Incidente_Arranque_Cliente]] para el cierre del fallo empaquetado.
