---
knowledge_id: vault-20261003-proyecto-aetherion-07-licencias-y-cuentas-07-datos-y-seguridad
title: "Datos de cuenta y controles documentados"
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

# Datos de cuenta y controles documentados
Distingue contraseña, token administrativo, sesión, pase offline y resultados locales. Los controles registrados no sustituyen una auditoría de seguridad.

## Datos y seguridad

| Dato | Tratamiento |
|---|---|
| Contraseña | El servicio conserva hash Argon2id con sal aleatoria; nunca recibe salida de logs con contraseña deliberadamente |
| Clave de licencia | Se valida por RSA-PSS; SQLite guarda SHA-256 de la cadena, no la clave original |
| Contraseña de administrador | Bearer token separado del cliente; License Manager lo cifra con Windows DPAPI |
| Token de sesión | Entropía aleatoria; la base guarda su SHA-256, sesión expira a los 30 días, logout y suspensión la revocan |
| Pase offline | Payload firmado Ed25519 por clave privada persistida en volumen server; el cliente comprueba firma, dispositivo y fechas |
| Cache de cliente | DPAPI bajo el perfil actual de Windows; incluye token de sesión/pase y última hora observada |
| Resultados de benchmark | Siguen guardándose en el dispositivo; no se sincronizan por este servicio |

El chequeo online ocurre cada cinco minutos en sesión abierta. El servicio no implementa cobro, email de recuperación ni restablecimiento de contraseña. Las renovaciones quedan a cargo del propietario tras verificar el pago.

### Modelo y límites offline

El servidor firma un pase con `offline_until = última validación + 7 días`, limitado además por vencimiento de licencia + 7 días. El cliente lo almacena con DPAPI, verifica con la clave pública incluida en el pase y lo liga al Device ID actual. El cache recuerda `last_seen_utc` para detectar retroceso temporal del reloj en el modo offline.

El acceso offline es una tolerancia de continuidad, no una revocación instantánea: al desactivar una cuenta o cortar renovación, el usuario desconectado puede usar el pase que ya recibió hasta su fecha límite. El cierre de sesión elimina el cache local; por eso volver a iniciar sesión después de cerrar sesión requiere conectividad. Este comportamiento es parte del equilibrio acordado entre continuidad y control de acceso.

## Procedencia y contexto

El contenido procede de [[Proyecto Aetherion/06_Historial/09_Cuentas_Servicio_Renovacion_2026-09-30]]. Conserva las condiciones de ese registro; no acredita una ejecución nueva durante la organización del vault.
