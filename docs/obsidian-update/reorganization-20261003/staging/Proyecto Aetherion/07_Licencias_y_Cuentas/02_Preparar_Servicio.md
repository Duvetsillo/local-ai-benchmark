---
knowledge_id: vault-20261003-proyecto-aetherion-07-licencias-y-cuentas-02-preparar-servicio
title: "Preparación del servicio propio"
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

# Preparación del servicio propio
Procedimiento documentado, pendiente de evidencia de despliegue real.

## 1. Preparar el servicio del propietario

1. Elegir un VPS Linux y un dominio controlado por el propietario, con DNS dirigido al VPS.
2. Copiar `server/` al host, crear `.env` desde `.env.example` y establecer dominio, secreto de administrador aleatorio y `PUBLIC_KEY_N` del proyecto.
3. Arrancar Docker Compose. Caddy obtiene y renueva TLS. No publicar el puerto interno 8000 directamente.
4. Confirmar `/health` sobre HTTPS.
5. En License Manager guardar la misma URL y el token administrativo. El programa valida la ruta de salud y cifra los ajustes con DPAPI para el usuario de Windows.
6. El cliente final guarda su URL bajo `%LOCALAPPDATA%\Aetherion\service.json` al autenticar.

La URL y las credenciales reales no se guardan en este vault. Mantener `.env`, el token, el volumen de datos y la clave privada de firma fuera del repositorio y de Obsidian.

## Procedencia y contexto

El contenido procede de [[Proyecto Aetherion/06_Historial/09_Cuentas_Servicio_Renovacion_2026-09-30]]. Conserva las condiciones de ese registro; no acredita una ejecución nueva durante la organización del vault.
