---
proyecto: Aetherion
tipo: historial-de-sesion
fecha: 2026-09-30
estado: interfaz-implementada-arranque-pendiente
tags: [aetherion, friday, cliente, interfaz, release, historial]
knowledge_id: vault-legacy-proyecto-aetherion-06-historial-06-rediseno-interfaz-2026-09-30
title: "Rediseño del cliente de escritorio — 2026-09-30"
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


# Rediseño del cliente de escritorio — 2026-09-30

## Propósito de la intervención

Se renovó la interfaz del cliente de escritorio Aetherion a partir de la captura proporcionada por el Jefe. El objetivo fue que el programa se perciba como una herramienta de escritorio profesional, legible y coherente con la identidad operativa de F.R.I.D.A.Y., y dejar como versión principal el ejecutable reconstruido.

La identidad se consultó en `Proyecto FRIDAY/IDENTITY.md` y `Proyecto FRIDAY/SOUL.md`: F.R.I.D.A.Y. se define como soporte técnico y operativo de alto nivel, con una presencia calmada, precisa, eficiente, profesional y directa, en español. La identidad se aplicó al criterio visual y a la redacción de la documentación. Aetherion mantiene su nombre y función de benchmark local.

## Diagnóstico de la interfaz de referencia

La captura mostraba una ventana oscura con navegación lateral, información de sistema, traza de benchmark y un panel de configuración. El lenguaje técnico y la paleta ya apuntaban a una aplicación local, pero la distribución presentaba varios problemas de acabado:

- El panel de configuración era estrecho y tenía muchos controles verticales.
- El botón de actualización de modelos quedaba parcialmente recortado al final de la ventana.
- Los bloques competían por atención y los títulos, ayudas y acciones tenían jerarquías débiles.
- La traza de ejecución ocupaba una gran región sin un estado vacío que orientara al usuario.
- La navegación y el área de trabajo necesitaban una separación más consistente.

La referencia sirve como evidencia visual de partida; no se generó una captura final automatizada en esta sesión.

## Dirección visual aplicada

La interfaz conserva el carácter técnico oscuro de Aetherion, con una paleta más consistente de azul pizarra, superficies elevadas y acento menta. La identidad F.R.I.D.A.Y. se expresa mediante sobriedad, previsibilidad, mensajes de estado claros y una jerarquía visual calmada, no mediante decoración temática que distraiga de las mediciones.

### Composición de la pantalla principal

1. **Rail de navegación:** presenta las áreas de trabajo con una selección visible y un pie de versión.
2. **Cabecera de aplicación:** agrupa identidad Aetherion, contexto de benchmark y estado del runtime.
3. **Tarjetas de resumen:** muestran runtime, modelos y última ejecución en un vistazo.
4. **Perfil de hardware:** separa las medidas del dispositivo de las acciones de configuración.
5. **Traza de benchmark:** dispone un estado vacío legible y un panel para resultados locales.
6. **Configuración de ejecución:** reúne modelo, suite de tareas, requisitos del entorno, carpeta GGUF, progreso y acciones.
7. **Panel con desplazamiento:** permite llegar a controles inferiores sin que queden cortados por el tamaño de ventana.

Las páginas secundarias también se reorganizaron en paneles y tarjetas para mantener la lectura de la ventana coherente fuera del dashboard.

### Ventana y accesibilidad práctica

- Tamaño inicial: 1200 × 820.
- Tamaño mínimo: 1020 × 720.
- Área de configuración desplazable mediante canvas y scrollbar.
- Texto de cuerpo y etiquetas aumentado respecto de la interfaz previa; Consolas se conserva para salida técnica.
- Estados de selección, progreso y scroll usan la misma familia visual que las tarjetas.

Estas decisiones mejoran la lectura y evitan depender de una altura fija, pero no equivalen a una auditoría WCAG, una comprobación de alto contraste o una validación de todos los factores de escala DPI.

## Cambios de implementación

### `src/local_ai_benchmark/client/desktop.py`

Se reconstruyeron los métodos de composición visual del cliente para introducir el rail, cabecera, tarjetas, áreas de estado y panel de configuración desplazable. Se conservaron las referencias que esperan los callbacks y manejadores ya existentes. El cambio se limitó a presentación y composición de widgets: no se modificaron providers, cálculos de benchmark, formato de resultados, página web ni preferencias.

### `src/local_ai_benchmark/client/theme.py`

Se actualizaron los colores base, tamaños tipográficos y estilos ttk de combobox, scrollbar vertical y progressbar. La nueva paleta incluye, entre otros, canvas `#090D13`, superficie `#121C27`, texto `#F4F7FA`, texto secundario `#C4CFD9` y acento menta `#6DE5C1`.

| Token | Nuevo valor | Uso |
|---|---|---|
| canvas | `#090D13` | fondo exterior |
| shell | `#0D141D` | marco y áreas de trabajo |
| surface | `#121C27` | tarjetas y bloques |
| surface_elevated | `#182533` | controles elevados |
| surface_interactive | `#223547` | interacción y selección |
| line | `#263746` | bordes sutiles |
| line_strong | `#344B5D` | separación reforzada |
| text | `#F4F7FA` | texto principal |
| text_soft | `#C4CFD9` | texto secundario |
| muted | `#94A6B5` | ayudas y etiquetas |
| quiet | `#728393` | baja prioridad |
| accent | `#6DE5C1` | acento y acción primaria |
| success | `#9BE0B5` | estado correcto |
| error | `#FF9292` | error |

### Artefacto de distribución

El ejecutable oficial `downloads/Aetherion-Client.exe` se reemplazó por la compilación nueva. También se comparó con `dist/Aetherion-Client.exe` y con la copia temporal con sufijo Redesigned: las tres copias medían 13 976 919 bytes y compartían el SHA-256 completo `CCC88D3D9981743FD2FA812CD2EFCF6D4D42F2888F615924B663560F6B39AF37`.

La compilación se produjo con PyInstaller 6.22.3 y Python 3.14.7 mediante el flujo existente del proyecto. No se cambió el formato de distribución ni la especificación PyInstaller.

## Incidente encontrado y corrección

En la primera inicialización de la nueva pantalla, Tkinter devolvió `TclError: unknown option "-padx"` porque se pasó `padx` directamente a `Canvas.create_window`, una llamada que no acepta esa opción. Se corrigió envolviendo el contenido del panel desplazable en un frame con padding propio y quitando la opción inválida de `create_window`.

Esta es la causa reproducida y corregida durante la sesión para el fallo de inicialización del cambio nuevo. Sustituye la anotación anterior que dejaba el mensaje genérico de excepción sin diagnóstico. No se obtuvo una captura de traceback del primer lanzamiento histórico; por eso no se atribuye retrospectivamente a esta causa cualquier fallo anterior que no se haya reproducido.

## Verificación realizada

- El fuente Python se analizó sintácticamente sin errores.
- Se inició la aplicación desde el fuente; la creación de la interfaz llegó a la espera principal de Tkinter después de corregir la opción inválida.
- PyInstaller finalizó la reconstrucción de `Aetherion-Client.exe`.
- Se comprobó que `downloads/Aetherion-Client.exe`, `dist/Aetherion-Client.exe` y la copia temporal coincidían en hash y tamaño.
- Se inició el ejecutable desde `downloads` dos veces, con y sin el directorio del repositorio como directorio de trabajo. En ambas comprobaciones se observó una instancia con el título `Unhandled exception in script`; otra instancia del mismo arranque no presentó título. El proceso reportó `Responding=True`, lo cual solo indica que Windows lo consideraba receptivo y no acredita que la aplicación haya abierto correctamente.
- Por tanto, la interfaz reorganizada y la reconstrucción del EXE sí están hechas, pero la entrega empaquetada aún no está lista para considerarse sustituida funcionalmente. El diálogo de excepción sigue abierto como incidente independiente.
- No se ejecutó la suite de pruebas ni se hizo una revisión visual comparativa con captura de pantalla. Por tanto, compilación y creación inicial de widgets están verificadas; apariencia pixel a pixel, todas las rutas interactivas, tamaños DPI y recorrido de benchmark requieren una revisión visual/manual posterior.

## Alcance y límites

No se alteraron el motor de benchmarks, providers, persistencia de resultados, telemetría, instaladores, web ni configuración del usuario. La carpeta temporal `downloads/Aetherion-Client-Redesigned.exe` quedó presente al terminar esta sesión y es idéntica al ejecutable estándar según la comprobación registrada. Se puede retirar en una limpieza de distribución futura después de confirmar que nadie la utiliza.

El repositorio conserva los cambios de fuente y el ejecutable principal como modificaciones locales sin commit. `dist/` y la carpeta de build corresponden a artefactos locales del proceso.

## Continuidad recomendada

1. Capturar el texto completo del diálogo empaquetado, habilitar consola o registrar la excepción para obtener el traceback.
2. Comparar el entrypoint congelado con el arranque desde fuente y aislar la diferencia con una compilación diagnóstica.
3. Aplicar una corrección mínima, reconstruir en carpeta temporal y confirmar que desaparece el diálogo antes de reemplazar otra vez la descarga principal.
4. Abrir la ventana, revisar scroll, navegación, resoluciones y escala de Windows.
5. Ejecutar un benchmark pequeño y confirmar progreso, resultado y apertura de carpeta.
6. Retirar el duplicado Redesigned después de verificar que ya no se usa; actualizar esta nota con captura y hash de la versión aceptada.

## Enlaces relacionados

- [[Proyecto Aetherion/00_Gobierno/00_MOC_Aetherion]]
- [[Proyecto Aetherion/00_Gobierno/02_Estado_Actual]]
- [[Proyecto Aetherion/02_Cliente/01_Experiencia_y_Pantallas]]
- [[Proyecto Aetherion/02_Cliente/02_Sistema_Visual]]
- [[Proyecto Aetherion/04_Calidad/02_Incidente_Arranque_Cliente]]
- [[Proyecto Aetherion/06_Historial/01_Cronologia]]
- [[Proyecto FRIDAY/IDENTITY]]
- [[Proyecto FRIDAY/SOUL]]

## Navegación documental

Volver a [[Proyecto Aetherion/06_Historial/00_Mapa_Historial]].
