---
knowledge_id: vault-20261003-proyecto-aetherion-07-licencias-y-cuentas-09-autoridad-y-planes
title: "Autoridad de firma y planes"
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
source_refs: ["[[Proyecto Aetherion/06_Historial/08_Generador_Licencias_y_Detener_Benchmark_2026-09-30]]"]
tags: ["aetherion", "area/07-licencias-y-cuentas", "process"]
---

# Autoridad de firma y planes
La autoridad privada pertenece al propietario. Esta nota conserva el esquema de firma y planes del administrador; el flujo central posterior se desarrolla en [[Proyecto Aetherion/07_Licencias_y_Cuentas/03_Emitir_y_Sincronizar]].

## Administrador de licencias

La entrega de escritorio se ubica en:

`C:\Users\Dayve\Desktop\Aetherion License Manager\`

Archivos incluidos:

- `Start-Aetherion-License-Manager.bat`: acceso de inicio sin parámetros.
- `Aetherion-License-Manager.ps1`: interfaz gráfica Windows Forms y funciones de inicialización/firma.
- `README-License-Manager.md`: guía del propietario, requisitos y custodia de autoridad.

El fuente mantenible también vive en `tools/Aetherion-License-Manager.ps1`, junto con la documentación breve del administrador. Se ejecuta bajo Windows PowerShell/PowerShell para Windows. En esta entrega es una aplicación gráfica PowerShell, no un EXE instalable. Esto evita incorporar un segundo empaquetador al repositorio y deja visible el fuente de la herramienta administrativa.

### Interfaz del administrador

La ventana presenta un tema oscuro alineado con Aetherion, una ubicación seleccionable del proyecto, el control **Create authority**, campos de destinatario y de ID del equipo, selector de licencia, botón **Generate license key**, salida multilínea y botón de copia.

Planes disponibles:

| Opción | Plazo | Uso esperado |
|---|---:|---|
| Trial | 7 días desde emisión | Evaluación temporal predefinida |
| Custom duration | 1 a 3650 días | Periodo elegido en el campo Days (por ejemplo, 3 días) |
| Unlimited | Sin expiración | Acceso indefinido, todavía vinculado a un equipo |

El nombre de la persona o entidad es una etiqueta opcional. El ID de equipo requerido debe tener 32 caracteres hexadecimales y se copia desde la pantalla de activación del cliente.

### Preparación inicial de la autoridad

1. El propietario inicia `Start-Aetherion-License-Manager.bat`.
2. Confirma la ruta del repositorio en el campo superior; Browse permite cambiarla.
3. Pulsa **Create authority** una sola vez.
4. El administrador crea RSA de 2048 bits y protege el XML de la clave privada con Windows DPAPI para la cuenta actual.
5. La clave privada cifrada se almacena en `%LOCALAPPDATA%\Aetherion\licensing\signing_key.dpapi`.
6. El administrador escribe únicamente el módulo público en `src/local_ai_benchmark/client/licensing.py`.
7. Debe construirse una nueva versión de Aetherion para que su ejecutable incluya esa clave pública.
8. Una vez reconstruido el cliente, el propietario emite las licencias necesarias desde el administrador.

La autoridad se crea en una cuenta de Windows concreta. DPAPI evita guardar la clave privada en texto claro y restringe el descifrado a ese usuario/equipo de Windows. Se debe proteger el perfil que custodia la autoridad. Una pérdida o sustitución de la clave privada implica que las licencias de la autoridad previa dejan de corresponder a nuevas compilaciones.

El administrador compara el módulo de la clave privada con `PUBLIC_KEY_N` del código fuente seleccionado antes de cada emisión. Si no corresponden, rechaza firmar; así se evita producir claves para otro repositorio o bajo otra autoridad accidentalmente.

## Formato y validación

La cadena tiene la forma `AETH1.<payload-base64url>.<firma-base64url>`. El contenido firmado incluye versión, ID de licencia, plan, destinatario opcional, ID del equipo, hora de emisión y fecha de expiración (nula para Unlimited). La autoridad firma los bytes UTF-8 exactos que serializa .NET. El cliente verifica la firma RSA-PSS/SHA-256 y después valida el contenido del payload.

La verificación admite el tamaño de sal PSS elegido por el proveedor criptográfico de Windows y conserva los controles de versión, plan, equipo, fechas y estado local. El cliente sigue guardando la activación bajo `%LOCALAPPDATA%\Aetherion\license.json`, revalida al inicio, de forma periódica y antes de ejecutar un benchmark, y vuelve a mostrar el gate si pierde validez.

Los planes limitados calculan su fecha en UTC a partir del instante de emisión. Trial usa el valor configurado `TRIAL_DAYS = 7`. La activación exige que coincida el ID del equipo. El estado local recuerda la última hora observada para detectar retrocesos significativos del reloj.

### Límite de seguridad

Este es un esquema de licencia offline. No proporciona revocación remota ni inviolabilidad frente a alguien con control administrativo del equipo, capacidad de alterar el ejecutable o manipular el reloj/estado local. La clave privada se mantiene separada del cliente, pero una distribución comercial con controles más fuertes requeriría un servicio de licencias y una política de recuperación de autoridad.

## Procedencia y contexto

El contenido procede de [[Proyecto Aetherion/06_Historial/08_Generador_Licencias_y_Detener_Benchmark_2026-09-30]]. Conserva las condiciones de ese registro; no acredita una ejecución nueva durante la organización del vault.
