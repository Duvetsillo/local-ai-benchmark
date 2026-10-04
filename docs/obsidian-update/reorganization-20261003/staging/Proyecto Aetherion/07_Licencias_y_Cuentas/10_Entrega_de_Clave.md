---
knowledge_id: vault-20261003-proyecto-aetherion-07-licencias-y-cuentas-10-entrega-de-clave
title: "Entrega de la clave al titular"
project: Aetherion
domain: 07_Licencias_y_Cuentas
note_type: process
version: 1.0.0
status: archived
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/07_Licencias_y_Cuentas/00_Mapa_Licencias_y_Cuentas]]"]
related: []
replaces: []
source_refs: ["[[Proyecto Aetherion/06_Historial/08_Generador_Licencias_y_Detener_Benchmark_2026-09-30]]"]
tags: ["aetherion", "area/07-licencias-y-cuentas", "process"]
---

# Entrega de la clave al titular
Secuencia del hito de administrador offline. Al operar con servicio central, añadir la sincronización y reclamación descritas en [[Proyecto Aetherion/07_Licencias_y_Cuentas/03_Emitir_y_Sincronizar]] y [[Proyecto Aetherion/07_Licencias_y_Cuentas/04_Alta_y_Acceso]].

## Ruta operativa de emisión

1. Construir y entregar la versión del cliente Aetherion que ya incluye la clave pública.
2. El usuario inicia el cliente y copia **DEVICE ID** de la pantalla de activación.
3. El propietario inicia el administrador independiente.
4. Pega el ID en **Device ID** y añade un destinatario si es útil para control interno.
5. Selecciona Trial, Custom duration o Unlimited. Para tres días, selecciona Custom duration e introduce `3`.
6. Pulsa **Generate license key** y **Copy key**.
7. Comparte la cadena completa con el titular del equipo destino.
8. El titular pega la clave en Aetherion y verifica que el estado `ACTIVE` y el plan aparecen en la interfaz.

La expiración empieza al emitir; todavía no existe una opción «comenzar al activar». Las claves ilimitadas también contienen emisión e ID del equipo, aunque no fecha de expiración.

## Procedencia y contexto

El contenido procede de [[Proyecto Aetherion/06_Historial/08_Generador_Licencias_y_Detener_Benchmark_2026-09-30]]. Conserva las condiciones de ese registro; no acredita una ejecución nueva durante la organización del vault.
