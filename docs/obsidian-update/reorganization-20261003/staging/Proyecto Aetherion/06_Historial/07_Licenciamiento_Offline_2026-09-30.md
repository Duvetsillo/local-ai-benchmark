---
proyecto: Aetherion
tipo: diseño-y-operacion
fecha: 2026-09-30
estado: implementado-en-fuente-build-pendiente
tags: [aetherion, licencias, activacion, rsa, friday]
knowledge_id: vault-legacy-proyecto-aetherion-06-historial-07-licenciamiento-offline-2026-09-30
title: "Activación por clave y licencias offline"
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


> [!info] Actualización 2026-09-30
> El flujo de propietario ya usa el administrador gráfico separado documentado en [[Proyecto Aetherion/06_Historial/08_Generador_Licencias_y_Detener_Benchmark_2026-09-30]]. Las instrucciones de CLI que aparezcan más abajo corresponden al diseño preliminar y quedan supersedidas: usa `C:\Users\Dayve\Desktop\Aetherion License Manager\Start-Aetherion-License-Manager.bat`. La clave privada se protege con DPAPI en `signing_key.dpapi`, no con contraseña en un PEM. El trial implementado está fijado en 7 días.

# Activación por clave y licencias offline

## Objetivo

Requerir una clave antes de acceder al espacio de trabajo del cliente Aetherion y permitir que el propietario genere claves por dispositivo con distintos plazos. La identidad de experiencia sigue los criterios profesionales y precisos documentados en [[Proyecto FRIDAY/IDENTITY]] y [[Proyecto FRIDAY/SOUL]].

## Modelo acordado

- Una clave queda vinculada a **un solo equipo**.
- El cliente muestra un identificador derivado de la identidad del sistema operativo. La interfaz permite copiarlo.
- El propietario emite la clave con el identificador y entrega al cliente una cadena firmada.
- La aplicación valida la firma localmente; no requiere servicio web ni envía telemetría.
- Se definieron planes `duration`, `trial` y `unlimited`.
- La opción `duration` permite días personalizados, por ejemplo 3.
- `trial` queda configurado inicialmente en 7 días (`TRIAL_DAYS = 7`), a la espera de la confirmación final del plazo.
- `unlimited` no caduca, pero sigue vinculado a un equipo.
- El vencimiento de los planes limitados se calcula en UTC desde la emisión.

## Flujo para quien usa el cliente

1. Al iniciar sin una licencia válida, Aetherion muestra la pantalla de activación y oculta el espacio de trabajo.
2. La pantalla presenta el ID del equipo y permite copiarlo.
3. El propietario usa el generador administrativo con el ID y el plan deseado.
4. La persona pega la clave completa y activa el cliente.
5. La aplicación conserva la licencia localmente en `%LOCALAPPDATA%/Aetherion/license.json`.
6. La licencia y la fecha de último uso se revisan al inicio, cada 30 segundos y antes de iniciar un benchmark. Al caducar, se vuelve a bloquear el área de trabajo hasta que se introduzca otra clave válida.

## Flujo del propietario: preparación inicial

Desde la raíz del repositorio:

```powershell
python tools\aetherion_license_admin.py init-signing-key
```

La utilidad genera una clave RSA de 2048 bits. Solicita una contraseña y guarda la privada cifrada en `%LOCALAPPDATA%/Aetherion/licensing/signing_key.pem`; escribe solo el módulo público en `src/local_ai_benchmark/client/licensing.py`. La contraseña y una copia de recuperación de la clave deben custodiarse de forma segura. La privada no se debe enviar al cliente, incluir en `downloads`, subir al repositorio o compartir con quienes reciben licencias. El generador vuelve a pedir la contraseña cada vez que firma una licencia.

Después de inicializar la clave, se requiere compilar una nueva versión para que el EXE incluya la pública correspondiente. Un cliente construido antes de la inicialización no puede validar las claves de esa autoridad.

## Emisión de claves

```powershell
# Clave válida durante 3 días desde su emisión
python tools\aetherion_license_admin.py issue --machine-id ID_DEL_EQUIPO --plan duration --days 3

# Trial configurado inicialmente por 7 días
python tools\aetherion_license_admin.py issue --machine-id ID_DEL_EQUIPO --plan trial

# Sin fecha de vencimiento, en un solo equipo
python tools\aetherion_license_admin.py issue --machine-id ID_DEL_EQUIPO --plan unlimited
```

El generador imprime la cadena firmada en stdout. Copiarla completa a la interfaz. El comando acepta además `--licensed-to` como etiqueta informativa. La licencia contiene plan, UUID, destinatario opcional, equipo, emisión y vencimiento; el runtime no necesita guardar un nombre personal.

## Diseño de seguridad

- Firma offline RSA 2048 con SHA-256 y padding PSS mediante la dependencia `cryptography`; la biblioteca recomienda PSS para firmas de aplicaciones nuevas ([documentación RSA](https://cryptography.io/en/45.0.3/hazmat/primitives/asymmetric/rsa/)).
- `licensing.py` contiene el verificador y la clave pública; el generador privado vive en el directorio `tools` y carga el material privado local.
- El ID visible es un SHA-256 truncado derivado del identificador de Windows `MachineGuid` (o de una fuente disponible en otros sistemas). El valor de origen no se muestra.
- El estado registra la última hora válida para detectar una regresión significativa del reloj local.
- Una firma inválida, otro ID de equipo, licencia expirada o retroceso horario bloquean la activación.

La licencia es un control offline, no una protección inviolable. Sin un servidor no hay revocación remota y un usuario con control sobre el equipo puede alterar el reloj, borrar estado local, parchear el binario o inspeccionar la aplicación. La fecha de último uso en un archivo local eleva el coste de retroceder el reloj, pero no sustituye una autoridad remota o almacenamiento de confianza.

## Archivos del repositorio

- `src/local_ai_benchmark/client/licensing.py`: cálculo del ID, serialización, verificador, guardado local y firma usada por la utilidad.
- `src/local_ai_benchmark/client/desktop.py`: pantalla de activación, inicialización condicional del dashboard, control periódico y etiqueta del plan en la navegación.
- `tools/aetherion_license_admin.py`: inicialización de par de firma y emisión de licencias.
- `README.md`: preparación, comandos de emisión y limitaciones.
- `pyproject.toml`: incluye `cryptography` como dependencia del cliente para usar primitivas criptográficas mantenidas.

## Estado de validación al 2026-09-30

- Los tres archivos Python se analizaron sintácticamente; no se informaron errores.
- No se añadieron ni ejecutaron pruebas, de acuerdo con el alcance pedido.
- La inicialización de la clave privada no se ejecutó en esta sesión; no se creó ni registró una clave maestra.
- No se compiló un nuevo EXE de licencias.
- El ejecutable distribuible existente no incorpora el cambio. El incidente anterior de `Unhandled exception in script` sigue abierto; comprobar primero la compilación empaquetada antes de publicar la versión protegida.
- El comportamiento funcional de firma, activación y vencimiento aún requiere validación en una compilación preparada después de resolver el incidente.

## Continuidad

1. Confirmar si el trial debe conservar 7 días o cambiar a otro plazo.
2. Inicializar la clave de firma en el equipo que actuará como autoridad de licencias y custodiar una copia segura de recuperación.
3. Conseguir el traceback y resolver el arranque de PyInstaller.
4. Compilar el cliente con la clave pública inicializada.
5. Generar una clave de prueba por equipo y validar activación, transferencia entre equipos, caducidad, reloj y reactivación.
6. Solo después reemplazar la descarga principal y documentar hash y captura.

## Enlaces

- [[Proyecto Aetherion/00_Gobierno/00_MOC_Aetherion]]
- [[Proyecto Aetherion/00_Gobierno/02_Estado_Actual]]
- [[Proyecto Aetherion/04_Calidad/02_Incidente_Arranque_Cliente]]
- [[Proyecto Aetherion/06_Historial/06_Rediseño_Interfaz_2026-09-30]]

## Navegación documental

Volver a [[Proyecto Aetherion/06_Historial/00_Mapa_Historial]].
