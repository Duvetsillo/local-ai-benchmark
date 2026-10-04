---
knowledge_id: vault-20261003-proyecto-aetherion-07-licencias-y-cuentas-04-alta-y-acceso
title: "Alta y acceso de cuenta"
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

# Alta y acceso de cuenta
El primer alta reclama la licencia; los accesos siguientes usan la cuenta ligada a ese dispositivo.

## 3. Reclamar e iniciar sesión

1. Al abrir Aetherion sin sesión válida aparece la pantalla de acceso; el espacio de trabajo queda oculto.
2. El cliente muestra y permite copiar Device ID y pide URL del servicio.
3. En el primer alta el usuario aporta clave, nombre de cuenta, contraseña y confirmación.
4. El servidor valida firma, vigencia, licencia sincronizada, equipo, estado sin reclamar y unicidad de usuario; reclama licencia y crea usuario/sesión en una transacción.
5. Las siguientes visitas usan username y contraseña. La cuenta queda ligada a un solo equipo y a su licencia.
6. La interfaz muestra estado de plan/vencimiento y ofrece SIGN OUT.

Si la clave es antigua y el servidor no la conoce, la sincronización administrativa debe realizarse primero. El flujo actual sincroniza automáticamente las claves creadas por la versión nueva de License Manager. No introducir claves de clientes como valores documentales ni registrarlas en logs.

## Procedencia y contexto

El contenido procede de [[Proyecto Aetherion/06_Historial/09_Cuentas_Servicio_Renovacion_2026-09-30]]. Conserva las condiciones de ese registro; no acredita una ejecución nueva durante la organización del vault.
