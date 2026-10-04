---
proyecto: Aetherion
tipo: implementación-y-operación
fecha: 2026-09-30
estado: implementado-en-fuente-pendiente-de-build
tags: [aetherion, cliente, licencias, activacion, benchmark, interfaz, powershell]
knowledge_id: vault-legacy-proyecto-aetherion-06-historial-08-generador-licencias-y-detener-benchmark-2026-09-30
title: "Generador de licencias independiente y detención del benchmark"
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


# Generador de licencias independiente y detención del benchmark

## Propósito de esta fase

Esta fase concreta el flujo que faltaba alrededor de la activación del cliente Aetherion: el propietario cuenta con una herramienta separada para preparar la autoridad de firma y emitir claves, la aplicación cliente mantiene la activación obligatoria antes del espacio de trabajo y la ejecución de benchmark ofrece una acción explícita para detenerse. Se conserva el principio local-first de Aetherion: el identificador se genera en el equipo, la clave se valida sin conexión y los resultados permanecen locales.

La separación de roles es intencional. El operador del administrador posee la autoridad privada; quien recibe Aetherion obtiene únicamente el binario con la clave pública, además de la licencia de su equipo. La aplicación del propietario y el cliente licenciado son piezas diferentes.

## Resultado solicitado

- Crear un cliente independiente para que el propietario genere claves.
- Colocarlo dentro de una carpeta en el Escritorio.
- Impedir el uso normal de Aetherion cuando no hay una licencia válida y pedir la clave.
- Emitir claves para un solo equipo, con trial, duración específica e ilimitada.
- Mostrar un botón para detener el benchmark en curso.
- Registrar el diseño, el flujo y el estado de entrega en esta carpeta de Obsidian.

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

## Gate de activación del cliente

La pantalla de activación se conserva dentro del propio cliente. Sin licencia guardada, sin firma válida, con licencia vencida, con ID de otro equipo o con retroceso de reloj, el usuario ve el formulario de clave y el ID del dispositivo; la interfaz principal del benchmark permanece oculta. Al activar, el cliente guarda la cadena firmada localmente y vuelve al panel si la validación es satisfactoria.

La comprobación también se ejecuta al pedir un benchmark. La licencia no es solo un formulario inicial: una falla de estado durante la sesión devuelve la interfaz a la activación. El dueño puede copiar el ID mostrado, pegarlo en el administrador independiente, emitir la licencia y entregarla a la persona para activación.

## Botón Stop benchmark

El panel de ejecución ahora presenta **Stop benchmark** junto al control de inicio. Permanece deshabilitado mientras no hay una ejecución y se activa al iniciar un benchmark. Al pulsarlo:

1. La interfaz señaliza un evento de cancelación y presenta el estado **STOPPING BENCHMARK**.
2. El proveedor interrumpe su bucle al recibir el siguiente fragmento del flujo del modelo.
3. El motor descarta la tarea que estaba generándose para no tratar una salida parcial como una respuesta completa.
4. Los resultados de tareas que terminaron antes de la solicitud se mantienen y se escriben localmente.
5. El registro resume la ejecución con estado `stopped` e incluye `stopped_by_user: true`.
6. La interfaz vuelve a habilitar los controles al recibir la finalización.

La detención es cooperativa. En una respuesta Ollama, el cierre se procesa cuando llega el siguiente bloque de datos del stream; si el runtime no envía más bloques, puede tardar hasta que el timeout de la solicitud o del proveedor libere la lectura. En llama.cpp se comprueba el evento entre elementos del iterador, también cooperativamente. Cerrar la ventana mientras hay trabajo solicita detenerlo antes de cerrar.

## Cambios de código previstos en la rama de cliente

- `src/local_ai_benchmark/client/licensing.py`: aceptación de firma PSS de Windows y lectura del payload firmado como JSON UTF-8.
- `src/local_ai_benchmark/client/desktop.py`: estado y acción de detención, envío del evento al motor, estado final detenido y protección al cerrar.
- `src/local_ai_benchmark/engine.py`: propagación de cancelación, descarte de la tarea interrumpida y persistencia de tareas finalizadas.
- `src/local_ai_benchmark/providers.py`: comprobaciones cooperativas en los streams de Ollama y llama.cpp.
- `tools/Aetherion-License-Manager.ps1`: fuente del generador separado.
- `README.md` y `README-License-Manager.md`: guía operativa y enlace al administrador.
- `pyproject.toml`: dependencia criptográfica para verificar firmas en el cliente.

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

## Verificación documental y técnica

- Se verificó mediante el parser de PowerShell que el fuente Windows Forms no contiene errores sintácticos.
- En la primera apertura, Windows PowerShell mostró `KeySize is a ReadOnly property` al crear autoridad. Se sustituyó la instancia genérica por `RSACng(2048)`; la comprobación aislada de este proveedor confirmó exportación XML privada y firma/verificación RSA-PSS SHA-256.
- No se ejecutó la ventana interactiva ni se generó una autoridad en esta sesión; no se ha creado una clave privada real.
- No se ejecutó el conjunto de pruebas.
- La comprobación sintáctica Python se realizó con el runtime de Python incluido en el entorno de trabajo y terminó correctamente. No se ejecutó el cliente ni la suite de pruebas.
- No se verificó compatibilidad de firma real entre .NET y `cryptography` en un cliente construido.
- La versión descargable existente no se reconstruyó: antes ya se había observado `Unhandled exception in script` al iniciarla y esa causa aún requiere diagnóstico. Por tanto, el EXE que se distribuye no se debe considerar actualizado con el gate y Stop hasta resolver el arranque y construir una nueva versión.
- La creación de autoridad escribe `PUBLIC_KEY_N` en el repositorio del propietario. Ese paso debe realizarse en la computadora que operará las licencias y requiere una nueva compilación posterior.

## Incidencia de distribución heredada

En la sesión anterior se actualizó el archivo de descarga del cliente y se identificó que el EXE rediseñado abre con la excepción `Unhandled exception in script`. Esta incidencia es anterior al presente trabajo y sigue pendiente. La causa no está resuelta aquí; no se atribuye a licencias ni al nuevo botón. Mantener el binario marcado como no validado evita ofrecer una protección de licencia que todavía no se ha confirmado en el ejecutable distribuido.

## Criterios para completar la entrega del cliente

- Resolver el arranque empacado del cliente rediseñado y capturar el traceback útil.
- Ejecutar una comprobación de sintaxis Python y pruebas en un entorno con las dependencias del proyecto.
- Abrir la ventana del administrador bajo la cuenta que custodiará la autoridad.
- Crear la autoridad y reconstruir el cliente incorporando la pública.
- Confirmar que una licencia generada por Windows se verifica con `cryptography` en la compilación de Aetherion.
- Validar activación en el mismo equipo, rechazo en un segundo equipo, trial de siete días, custom de tres días y Unlimited.
- Ejecutar un benchmark y detenerlo durante una generación para confirmar la persistencia de resultados previos y el estado `stopped`.
- Capturar la interfaz final, calcular el hash SHA-256 del binario validado y documentar el release.

## Referencias del proyecto

- [[Proyecto Aetherion/06_Historial/07_Licenciamiento_Offline_2026-09-30]]
- [[Proyecto Aetherion/06_Historial/06_Rediseño_Interfaz_2026-09-30]]
- [[Proyecto Aetherion/00_Gobierno/00_MOC_Aetherion]]
- [[Proyecto Aetherion/00_Gobierno/02_Estado_Actual]]
- [[Proyecto Aetherion/04_Calidad/02_Incidente_Arranque_Cliente]]

> [!info] Ampliación 2026-09-30
> La fase posterior añadió el servicio central, cuentas, login/logout, renovación administrativa, importación de claves antiguas y pase offline limitado. Su documentación de referencia es [[Proyecto Aetherion/06_Historial/09_Cuentas_Servicio_Renovacion_2026-09-30]]. La nota anterior describe el hito de generador y detener benchmark; el EXE aún requiere una compilación posterior.

## Navegación documental

Volver a [[Proyecto Aetherion/06_Historial/00_Mapa_Historial]].

Desglose temático: [[Proyecto Aetherion/07_Licencias_y_Cuentas/09_Autoridad_y_Planes]] · [[Proyecto Aetherion/07_Licencias_y_Cuentas/10_Entrega_de_Clave]] · [[Proyecto Aetherion/01_Arquitectura/08_Cancelacion_Cooperativa]].
