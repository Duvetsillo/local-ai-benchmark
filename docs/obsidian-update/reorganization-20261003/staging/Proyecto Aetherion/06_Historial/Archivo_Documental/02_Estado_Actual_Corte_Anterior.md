---
knowledge_id: vault-20261003-proyecto-aetherion-06-historial-archivo-documental-02-estado-actual-corte-anterior
title: "Corte anterior — 02_Estado_Actual"
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
source_refs: ["[[Proyecto Aetherion/00_Gobierno/02_Estado_Actual]]"]
tags: ["aetherion", "area/06-historial", "evidence"]
---

# Corte anterior — 02_Estado_Actual
> [!abstract] Registro histórico preservado
> Copia del contenido encontrado antes de esta reorganización. Puede contener estados ya corregidos; para operar consulta [[Proyecto Aetherion/00_Gobierno/02_Estado_Actual]].

---
proyecto: Aetherion
tipo: estado-actual
fecha: 2026-09-30
estado: interfaz-redisenada-arranque-empaquetado-abierto
tags: [aetherion, estado, continuidad, friday]
---

# Estado actual — 30 de septiembre de 2026

## Resumen ejecutivo

El cliente de escritorio recibió una reorganización amplia de su interfaz y una actualización del tema visual. La distribución estándar en `downloads/Aetherion-Client.exe` se sustituyó por la nueva compilación. Sin embargo, al abrir esa compilación reaparece el cuadro genérico **“Unhandled exception in script”**. La tarea de diseño y compilación avanzó, pero el reemplazo funcional del cliente no se considera terminado hasta obtener y corregir el error de arranque empaquetado.

La identidad consultada para orientar el trabajo es F.R.I.D.A.Y., tal como aparece en [[Proyecto FRIDAY/IDENTITY]] y [[Proyecto FRIDAY/SOUL]]: soporte profesional, calmado, preciso y eficiente, en español. El producto conserva el nombre Aetherion y su función de benchmark local.

## Hechos observados en esta sesión

- Se trabajó en `C:/Users/Dayve/Desktop/Carpetas/Local_AI_Benchmark`.
- Se rediseñaron `src/local_ai_benchmark/client/desktop.py` y `src/local_ai_benchmark/client/theme.py`.
- El chequeo sintáctico de Python no informó errores.
- La interfaz pudo recorrer su inicialización desde fuente y permanecer en el bucle de eventos de Tkinter después de corregir una opción inválida de Canvas.
- PyInstaller 6.22.3 con Python 3.14.7 terminó la reconstrucción.
- `downloads/Aetherion-Client.exe` y `dist/Aetherion-Client.exe` coincidían en tamaño (13 976 919 bytes) y SHA-256 (`CCC88D3D9981743FD2FA812CD2EFCF6D4D42F2888F615924B663560F6B39AF37`). La copia temporal `Aetherion-Client-Redesigned.exe` también era idéntica.
- El arranque del ejecutable descargable volvió a mostrar `Unhandled exception in script`; no se obtuvo el traceback.
- El proceso informó `Responding=True`, pero se vio al menos una instancia con la excepción; el indicador por sí solo no acredita una ventana operativa.
- La captura final de la aplicación no quedó disponible y no se ejecutó la suite de pruebas.

## Cambios incluidos en la interfaz

- Navegación lateral con selección visible.
- Cabecera con contexto del producto y estado de runtime.
- Tarjetas para runtime, modelos y última ejecución.
- Perfil del equipo y traza con estado vacío orientativo.
- Panel de configuración con desplazamiento para que acciones inferiores no queden recortadas.
- Tipografía, contraste visual, estados de controles y tarjetas secundarias revisados.
- Ventana inicial 1200 × 820 y mínimo 1020 × 720.

La composición exacta y los límites de verificación están en [[Proyecto Aetherion/06_Historial/06_Rediseño_Interfaz_2026-09-30]].

## Incidente pendiente

Se corrigió un error real de la interfaz: `Canvas.create_window` recibió el argumento no soportado `padx`; el padding se trasladó a un frame contenedor. Esa corrección permitió inicializar el fuente, pero no resolvió el diálogo de excepción del ejecutable congelado. Son observaciones distintas. Mantener abierto [[Proyecto Aetherion/04_Calidad/02_Incidente_Arranque_Cliente]] y no declarar listo el EXE hasta reproducir la causa exacta y confirmar una apertura visible.

## Próximas acciones

1. Obtener el traceback completo del ejecutable empaquetado.
2. Compilar una variante diagnóstica en un directorio temporal o activar salida de consola para aislar el punto de fallo.
3. Confirmar que el arreglo funciona desde el EXE, no solo desde el fuente.
4. Revisar el diseño en ventana, scroll, navegación, tamaño mínimo y escala DPI.
5. Hacer un recorrido manual corto de benchmark y resultados.
6. Cuando la versión abra y pase la revisión visual, registrar evidencia y decidir el tratamiento del duplicado temporal.

## Referencias

- [[Proyecto Aetherion/00_Gobierno/00_MOC_Aetherion]]
- [[Proyecto Aetherion/02_Cliente/02_Sistema_Visual]]
- [[Proyecto Aetherion/04_Calidad/02_Incidente_Arranque_Cliente]]
- [[Proyecto Aetherion/06_Historial/06_Rediseño_Interfaz_2026-09-30]]

## Activación por licencia — 2026-09-30

Se implementó el control de licencia en código fuente: el cliente exige una clave antes de abrir el workspace; el ID vincula la licencia a un equipo; los planes son `duration` (días configurables), `trial` (7 días provisional) y `unlimited` (sin vencimiento, todavía vinculado al equipo). Las claves se firman offline con RSA-PSS a través de `cryptography` y el generador privado queda separado del cliente.

El código Python pasó análisis sintáctico. No se ejecutaron pruebas ni compilación para esta función. Falta inicializar la autoridad privada, reconstruir el EXE y resolver el incidente de arranque que ya está abierto; por ahora, el ejecutable distribuible no contiene esta función. Consultar [[Proyecto Aetherion/06_Historial/07_Licenciamiento_Offline_2026-09-30]].


## Herramienta de licencias y detención — 2026-09-30

Se añadió el fuente de una GUI independiente para el propietario en `tools/Aetherion-License-Manager.ps1` y se colocó el lanzador y los archivos de la herramienta en `C:\Users\Dayve\Desktop\Aetherion License Manager`. Desde esa ventana se configura una autoridad RSA, se genera la clave ligada a un ID de equipo y se elige Trial (7 días), Custom duration (1–3650) o Unlimited. La autoridad privada se cifra mediante DPAPI en el perfil del propietario; el fuente Aetherion recibe únicamente la clave pública. La inicialización de autoridad todavía es una acción pendiente del propietario y después requiere compilar un nuevo cliente.

El código fuente incorpora **Stop benchmark** con cancelación cooperativa entre fragmentos, descarte de la tarea incompleta, conservación de las tareas terminadas y registro `stopped`. El EXE distribuible no se reconstruyó ni validó: persiste el incidente `Unhandled exception in script`. La nota [[Proyecto Aetherion/06_Historial/08_Generador_Licencias_y_Detener_Benchmark_2026-09-30]] detalla los cambios, el flujo y las verificaciones ejecutadas.
## Cuentas en servicio central — 2026-09-30

Se integró en fuente el ciclo de alta de usuario mediante clave, login/logout, estado de licencia, renovación de días sin nueva clave, gestión administrativa y sesión offline limitada a siete días. Las URLs quedan editables. El código de cliente está en `client/auth.py` y `client/desktop.py`; API y despliegue en `server/`; License Manager actualizado en `tools/` y en su copia de Escritorio. Se añadió sincronización/importación de claves antiguas firmadas.

Análisis sintáctico AST de los tres módulos Python y parser de PowerShell terminaron sin errores. No se hicieron pruebas de integración ni build. No existe aún dominio/VPS configurado, así que no se ha desplegado el servicio. El EXE sigue siendo una entrega anterior y todavía debe compilarse y abrirse para resolver el incidente de arranque ya documentado. Ver [[Proyecto Aetherion/06_Historial/09_Cuentas_Servicio_Renovacion_2026-09-30]].

## Corrección posterior — build actualizada y ventana abierta

El ejecutable sí se reconstruyó después de resolver la causa concreta del incidente. El entorno Python 3.14.7 carecía de `cryptography`, requerida por el flujo de licencias; se instaló `cryptography 50.0.2` y se compiló con PyInstaller 6.22.3. La nueva copia `downloads/Aetherion-Client.exe` abrió con la pantalla de cuenta, sin diálogo de excepción. SHA-256: `949E8615E74EB298A3867BB454F768C2A00693AA9DF2E6DBBD85ABCC11656329`.

El servidor todavía no está desplegado porque falta dominio/VPS, por lo que el acceso remoto de cuentas no está listo para uso end-to-end. Mantener el trabajo de aceptación del backend pendiente; el incidente de arranque documentado en [[Proyecto Aetherion/04_Calidad/02_Incidente_Arranque_Cliente]] queda resuelto para la build actual.
