---
proyecto: Aetherion
tipo: implementacion-y-operacion
fecha: 2026-09-30
estado: cliente-reconstruido-y-abierto-vps-y-prueba-integral-pendientes
tags: [aetherion, licencias, cuentas, autenticacion, servicio, vps, offline, seguridad]
knowledge_id: vault-legacy-proyecto-aetherion-06-historial-09-cuentas-servicio-renovacion-2026-09-30
title: "Cuentas Aetherion, servicio central y renovaciones"
project: Aetherion
domain: 06_Historial
note_type: evidence
version: 1.0.0
status: archived
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/06_Historial/00_Mapa_Historial]]"]
related: []
replaces: []
source_refs: []
---

> [!info] Lectura al 3 de octubre de 2026
> Registro de sesión fechado. Para decidir qué está vigente, consultar [[Proyecto Aetherion/00_Gobierno/02_Estado_Actual]]; no ejecutar los procedimientos preliminares sin leer sus ampliaciones posteriores.


# Cuentas Aetherion, servicio central y renovaciones

## Resumen del hito

Se amplió el modelo de activación de Aetherion para que una licencia sirva como invitación de un solo uso para crear una cuenta del cliente. Una vez reclamada, la cuenta se identifica con username y contraseña; el cliente inicia y cierra sesión, y el propietario puede consultar cuentas, suspenderlas o sumar días a su vigencia sin entregar una segunda clave. La licencia y el usuario permanecen ligados al mismo Device ID. El benchmark y los resultados siguen locales; el servidor gestiona autenticación y derecho de uso.

El código se integró en el repositorio del Escritorio. El endpoint queda configurable porque todavía no se ha seleccionado dominio ni VPS. Por ello esta nota distingue implementación de fuente, despliegue e integración real del ejecutable: son hitos distintos.

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

## Secuencia operativa completa

### 1. Preparar el servicio del propietario

1. Elegir un VPS Linux y un dominio controlado por el propietario, con DNS dirigido al VPS.
2. Copiar `server/` al host, crear `.env` desde `.env.example` y establecer dominio, secreto de administrador aleatorio y `PUBLIC_KEY_N` del proyecto.
3. Arrancar Docker Compose. Caddy obtiene y renueva TLS. No publicar el puerto interno 8000 directamente.
4. Confirmar `/health` sobre HTTPS.
5. En License Manager guardar la misma URL y el token administrativo. El programa valida la ruta de salud y cifra los ajustes con DPAPI para el usuario de Windows.
6. El cliente final guarda su URL bajo `%LOCALAPPDATA%\Aetherion\service.json` al autenticar.

La URL y las credenciales reales no se guardan en este vault. Mantener `.env`, el token, el volumen de datos y la clave privada de firma fuera del repositorio y de Obsidian.

### 2. Emitir una licencia nueva

1. El usuario proporciona el Device ID de 32 caracteres hexadecimales.
2. License Manager crea un payload `AETH1` firmado con RSA-PSS y la autoridad privada local protegida por DPAPI.
3. Antes de mostrar la clave, License Manager ejecuta `POST /v1/admin/licenses` con el token administrativo.
4. El servidor verifica la firma con la clave pública del proyecto y registra solo el hash SHA-256 de la cadena completa, más el ID, la máquina, el plan y la fecha.
5. Solo si el servidor confirmó la sincronización, la interfaz presenta la clave para entregarla al usuario.

Planes actuales: Trial de siete días, duración personalizada de 1 a 3650 días e ilimitada. Unlimited no caduca y no ofrece acción de renovar días. No regenerar autoridad: una autoridad RSA distinta invalidaría correspondencia con las claves ya emitidas.

### 3. Reclamar e iniciar sesión

1. Al abrir Aetherion sin sesión válida aparece la pantalla de acceso; el espacio de trabajo queda oculto.
2. El cliente muestra y permite copiar Device ID y pide URL del servicio.
3. En el primer alta el usuario aporta clave, nombre de cuenta, contraseña y confirmación.
4. El servidor valida firma, vigencia, licencia sincronizada, equipo, estado sin reclamar y unicidad de usuario; reclama licencia y crea usuario/sesión en una transacción.
5. Las siguientes visitas usan username y contraseña. La cuenta queda ligada a un solo equipo y a su licencia.
6. La interfaz muestra estado de plan/vencimiento y ofrece SIGN OUT.

Si la clave es antigua y el servidor no la conoce, la sincronización administrativa debe realizarse primero. El flujo actual sincroniza automáticamente las claves creadas por la versión nueva de License Manager. No introducir claves de clientes como valores documentales ni registrarlas en logs.

### 4. Renovar y administrar

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

### Modelo y límites offline

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

## Navegación documental

Volver a [[Proyecto Aetherion/06_Historial/00_Mapa_Historial]].

Desglose temático: [[Proyecto Aetherion/07_Licencias_y_Cuentas/01_Contrato_Cuenta_y_Dispositivo]] · [[Proyecto Aetherion/07_Licencias_y_Cuentas/02_Preparar_Servicio]] · [[Proyecto Aetherion/07_Licencias_y_Cuentas/03_Emitir_y_Sincronizar]] · [[Proyecto Aetherion/07_Licencias_y_Cuentas/04_Alta_y_Acceso]] · [[Proyecto Aetherion/07_Licencias_y_Cuentas/05_Renovacion_y_Suspension]] · [[Proyecto Aetherion/07_Licencias_y_Cuentas/06_Pase_Offline]] · [[Proyecto Aetherion/07_Licencias_y_Cuentas/07_Datos_y_Seguridad]] · [[Proyecto Aetherion/07_Licencias_y_Cuentas/08_Despliegue_y_Aceptacion]].
