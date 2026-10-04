---
knowledge_id: vault-20261003-proyecto-aetherion-07-licencias-y-cuentas-03-emitir-y-sincronizar
title: "Emisión y sincronización de licencias"
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

# Emisión y sincronización de licencias
La emisión del esquema central exige sincronización del servidor antes de entregar la clave.

## 2. Emitir una licencia nueva

1. El usuario proporciona el Device ID de 32 caracteres hexadecimales.
2. License Manager crea un payload `AETH1` firmado con RSA-PSS y la autoridad privada local protegida por DPAPI.
3. Antes de mostrar la clave, License Manager ejecuta `POST /v1/admin/licenses` con el token administrativo.
4. El servidor verifica la firma con la clave pública del proyecto y registra solo el hash SHA-256 de la cadena completa, más el ID, la máquina, el plan y la fecha.
5. Solo si el servidor confirmó la sincronización, la interfaz presenta la clave para entregarla al usuario.

Planes actuales: Trial de siete días, duración personalizada de 1 a 3650 días e ilimitada. Unlimited no caduca y no ofrece acción de renovar días. No regenerar autoridad: una autoridad RSA distinta invalidaría correspondencia con las claves ya emitidas.

## Procedencia y contexto

El contenido procede de [[Proyecto Aetherion/06_Historial/09_Cuentas_Servicio_Renovacion_2026-09-30]]. Conserva las condiciones de ese registro; no acredita una ejecución nueva durante la organización del vault.
