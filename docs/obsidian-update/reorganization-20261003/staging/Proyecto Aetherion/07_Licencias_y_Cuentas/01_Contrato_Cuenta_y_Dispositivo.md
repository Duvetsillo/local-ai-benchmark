---
knowledge_id: vault-20261003-proyecto-aetherion-07-licencias-y-cuentas-01-contrato-cuenta-y-dispositivo
title: "Cuenta, licencia y dispositivo"
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

# Cuenta, licencia y dispositivo
Esta nota reúne el contrato funcional registrado para el servicio central. El servicio no recopila los resultados del benchmark.

## Requisitos acordados

- Usuario nuevo: necesita una clave válida emitida por el propietario y sincronizada al servicio; la clave se reclama al crear username y contraseña.
- Cuenta: una cuenta por clave; contraseña mínima de 12 caracteres; los nombres de usuario aceptan letras, números, punto, guion y guion bajo.
- Un solo dispositivo: el ID se compara durante registro e inicio de sesión.
- Usuario existente: inicia sesión con sus credenciales; no vuelve a introducir una clave.
- Renovación: el propietario amplía la vigencia de esa cuenta después de confirmar pago; los días se agregan al vencimiento futuro o desde hoy si ya expiró.
- Sesión: puede cerrarse desde el cliente; el cierre revoca la sesión online y borra el pase local.
- Continuidad sin Internet: siete días como máximo desde la última validación, en el mismo perfil de Windows y equipo. Hace falta volver a conectarse para renovar ese pase.
- Configuración: el cliente y License Manager permiten fijar la URL. Se exige HTTPS salvo loopback local.

## Componentes

| Componente | Responsabilidad | Ubicación |
|---|---|---|
| Aetherion Client | Puerta de acceso, alta, inicio/cierre, renovación de sesión y uso local del benchmark | `src/local_ai_benchmark/client/desktop.py`, `client/auth.py` |
| Verificador de clave | RSA-PSS y huella estable del equipo | `src/local_ai_benchmark/client/licensing.py` |
| License Manager | Emite y firma la clave localmente; sincroniza la licencia y administra cuentas en el servicio | `tools/Aetherion-License-Manager.ps1`, copia en Escritorio |
| API | Registro, autenticación, licencias, sesiones, renovaciones y pases offline firmados | `server/app.py` |
| Almacenamiento | Usuarios, hashes, licencias reclamadas y sesiones revocables | SQLite persistente en volumen Docker |
| HTTPS | TLS automatizado para el dominio elegido | `server/Caddyfile`, Compose + Caddy |

## Decisiones registradas

- Persistencia central en servidor propio/VPS, elección del usuario.
- Dirección pública todavía sin definir; URL configurable en cliente y administrador.
- Una licencia para un equipo; una cuenta por licencia.
- No emitir nueva clave para renovación pagada; cambiar la fecha en el servidor.
- Offline limitado a siete días de gracia.
- Benchmark y archivos locales; API central no recopila resultados.

## Procedencia y contexto

El contenido procede de [[Proyecto Aetherion/06_Historial/09_Cuentas_Servicio_Renovacion_2026-09-30]]. Conserva las condiciones de ese registro; no acredita una ejecución nueva durante la organización del vault.
