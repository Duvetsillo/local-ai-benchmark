---
proyecto: Aetherion
tipo: cronologia
tags: [aetherion, historial]
knowledge_id: vault-legacy-proyecto-aetherion-06-historial-01-cronologia
title: "Cronología"
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


# Cronología

## 2026-09-28 — refinamiento visual

Solicitud de pulir el cliente de escritorio sin tocar web/configuración. Se identificó el repositorio Local_AI_Benchmark. La documentación de sesión registra paleta oscura azul pizarra con acento menta en theme.py y desktop.py.

## 2026-09-28 — ejecutable

El usuario indicó que la interfaz no se veía distinta. Se recompiló; al abrir, se reportó error de script y no se consiguió confirmar pantalla funcional.

## 2026-09-26 a 2026-09-27 — sitio público y cliente distribuible

- El repositorio incorporó el sitio público Aetherion con páginas de overview, modelos, comparación y políticas; también se trabajó identidad visual, animación de entrada y enlace de descarga.
- Se preparó el primer cliente Windows con PyInstaller y se documentaron requisitos de distribución y firma Authenticode opcional.
- La historia Git registra estas entregas; no implica que los binarios históricos sigan siendo los actuales.

## 2026-09-28 a 2026-09-29 — expansión funcional del cliente

- `LocalResultStore` incorporó escritura JSON atómica con archivo temporal, `fsync` y reemplazo; la sesión reportó ocho pruebas aprobadas para ese cambio.
- Se añadió la abstracción de proveedores locales con Ollama y llama.cpp/GGUF, selección de carpeta GGUF y detalles del runtime en los resultados.
- Se incorporó orientación heurística de compatibilidad hardware/modelo, requisitos de runtimes, descarga de instalador Ollama y catálogo/descarga GGUF con progreso. La orientación no garantiza que el modelo cargue ni que su rendimiento sea adecuado.
- La sesión reportó nueve pruebas locales aprobadas tras correcciones, refinamiento del cliente y navegación con siete vistas. También se ajustó CI para no cancelar prematuramente la matriz y mostrar mejor los diagnósticos; no se registra aquí una ejecución remota posterior como aprobada.
- La misma sesión reportó que el EXE se abrió correctamente. Esta evidencia histórica no sustituye la observación posterior del 30-09, cuando el binario distribuible volvió a mostrar una excepción genérica.

Fuentes: sesiones Copilot del 2026-09-29 y commits visibles en Git del 2026-09-28. Para estado actual, consultar [[Proyecto Aetherion/00_Gobierno/02_Estado_Actual]].

## 2026-09-30 — continuación

- Rama main alineada con origin/main al inspeccionar.
- downloads/Aetherion-Client.exe modificado localmente después de recompilar.
- Build finalizada con Python 3.14.7 y PyInstaller 6.22.3.
- La ventana de error volvió a observarse.
- No se capturó traceback.
- Se creó esta documentación extensa como base de continuidad.

## Uso de cronología

Añadir evidencia verificable, commit/hash y fecha. No elevar una hipótesis a causa raíz hasta reproducirla.

## 2026-09-30 — rediseño de interfaz y nueva compilación

- Se reorganizó la experiencia del cliente Aetherion: rail lateral, cabecera de estado, tarjetas de resumen, perfil de hardware, traza y configuración desplazable.
- Se actualizó la paleta a azul pizarra y menta, guiada por los valores de identidad consignados en [[Proyecto FRIDAY/IDENTITY]] y [[Proyecto FRIDAY/SOUL]].
- Se corrigió el argumento no soportado `padx` que impedía crear una ventana canvas desde fuente.
- El análisis sintáctico del fuente y la compilación PyInstaller terminaron correctamente.
- El arranque empaquetado volvió a mostrar `Unhandled exception in script`; no se conoce el traceback. Se mantiene abierto el incidente.
- Documentación extendida: [[Proyecto Aetherion/06_Historial/06_Rediseño_Interfaz_2026-09-30]].


## 2026-09-30 — diseño e implementación de licencias offline

- Se añadió una puerta de activación previa al dashboard y una pantalla que muestra/copia el ID del equipo.
- Se incorporó validación de claves firmadas, almacenamiento local, comprobación de vencimiento y detección básica de retroceso horario.
- Se añadió utilidad administrativa para inicializar la autoridad RSA protegida con contraseña y emitir planes duration, trial y unlimited; la firma usa RSA-PSS y `cryptography` se añadió a las dependencias del cliente.
- Se documentó un trial inicial de 7 días, pendiente de confirmación.
- Los archivos Python pasaron análisis sintáctico. No se ejecutaron pruebas ni build de esta función.
- No se inicializó la clave privada ni se reemplazó el ejecutable distribuible. La función está implementada en fuente; la entrega compilada queda pendiente.
- [[Proyecto Aetherion/06_Historial/07_Licenciamiento_Offline_2026-09-30]]


## 2026-09-30 — cuentas y renovaciones mediante servidor

- Se integró registro con licencia sincronizada, cuenta por licencia y dispositivo, contraseña con hash Argon2id, sesión revocable, cierre de sesión y extensión administrativa sin clave nueva.
- Se implementó API FastAPI con SQLite, pase offline firmado con siete días de gracia y plantilla Docker Compose/Caddy HTTPS. URL pública configurable mientras falta elegir VPS/dominio.
- License Manager consulta cuentas, renueva, habilita/deshabilita, sincroniza claves nuevas y ofrece importar claves anteriores.
- Análisis AST y parser PowerShell sin errores; no se ejecutaron pruebas ni build. Despliegue y validación real permanecen pendientes.
- [[Proyecto Aetherion/06_Historial/09_Cuentas_Servicio_Renovacion_2026-09-30]]

## 2026-09-30 — diagnóstico y cierre del error de arranque

- El EXE nuevo mostró `No module named 'cryptography'`; la dependencia faltaba en el Python 3.14.7 de compilación.
- Se instaló cryptography 50.0.2, PyInstaller la incluyó con su hook y el build se completó.
- Se actualizaron `dist/Aetherion-Client.exe` y `downloads/Aetherion-Client.exe`; SHA-256 `949E8615E74EB298A3867BB454F768C2A00693AA9DF2E6DBBD85ABCC11656329`.
- Se abrió la nueva ventana en la pantalla de acceso. El incidente queda resuelto en esta compilación; VPS y aceptación end-to-end permanecen pendientes.
- [[Proyecto Aetherion/04_Calidad/02_Incidente_Arranque_Cliente]]

## Navegación documental

Volver a [[Proyecto Aetherion/06_Historial/00_Mapa_Historial]].


## 2026-10-03 — refinamiento, Atelier y Studio 03

Las primeras revisiones recibieron la crítica de conservar la misma interfaz y cambiar solo colores. Studio separa inicio y laboratorio, incorpora navegación superior y nuevas bibliotecas/resultados. Se documentaron 18 pruebas aprobadas, comprobaciones de widgets en tres tamaños y build Studio 03. La aceptación estética y el recorrido online completo siguen pendientes.

[[Proyecto Aetherion/02_Cliente/06_Studio_Estructura_2026-10-03]] · [[Proyecto Aetherion/04_Calidad/07_Verificacion_Studio_2026-10-03]]

## 2026-10-03 — skills y organización documental

Se instalaron los paquetes Emil Kowalski, Impeccable y Taste para Codex. Su instalación no representa un rediseño adicional ya aplicado. El usuario autorizó reorganizar el vault excluyendo archivos Karen y Friday: [[Proyecto Aetherion/08_Herramientas_Diseno/01_Skills_Instaladas]] · [[00_Navegacion/Registro_de_Organizacion]].
