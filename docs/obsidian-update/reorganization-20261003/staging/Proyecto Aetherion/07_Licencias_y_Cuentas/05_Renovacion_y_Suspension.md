---
knowledge_id: vault-20261003-proyecto-aetherion-07-licencias-y-cuentas-05-renovacion-y-suspension
title: "Renovación y suspensión"
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

# Renovación y suspensión
La renovación cambia la fecha central sin emitir otra clave. La suspensión y el offline tienen ventanas de aplicación distintas.

## 4. Renovar y administrar

1. Abrir **Manage accounts** en License Manager, que consulta `GET /v1/admin/users`.
2. Seleccionar una cuenta y fijar cuántos días añadir.
3. Confirmar el pago fuera del sistema; pulsar **Extend selected account**.
4. El servicio calcula `max(vencimiento actual, ahora UTC) + días`, reactiva cuenta/licencia y responde nuevo vencimiento. No se genera ni se envía otra clave.
5. El próximo check-in del cliente recibe un pase renovado. Mientras no haya conexión, el pase local anterior sigue sujeto a sus límites.
6. **Disable / enable** suspende y revoca sesiones activas o restaura la cuenta. La comprobación online aplica los cambios inmediatamente; un equipo desconectado puede conservar el pase firmado hasta terminar su periodo limitado.

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

## Procedencia y contexto

El contenido procede de [[Proyecto Aetherion/06_Historial/09_Cuentas_Servicio_Renovacion_2026-09-30]]. Conserva las condiciones de ese registro; no acredita una ejecución nueva durante la organización del vault.
