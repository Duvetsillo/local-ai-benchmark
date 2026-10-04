---
proyecto: Aetherion
tipo: sistema-visual
fecha: 2026-09-30
tags: [aetherion, interfaz, visual, friday]
knowledge_id: vault-legacy-proyecto-aetherion-02-cliente-02-sistema-visual
title: "Sistema visual del cliente"
project: Aetherion
domain: 02_Cliente
note_type: reference
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/02_Cliente/00_Mapa_Cliente]]"]
related: []
replaces: []
source_refs: []
---

> [!info] Lectura al 3 de octubre de 2026
> La paleta pizarra y menta describe una revisión histórica; Studio 03 y Atelier se documentan en sus notas fechadas. Consultar [[Proyecto Aetherion/02_Cliente/06_Studio_Estructura_2026-10-03]].


# Sistema visual del cliente

## Dirección

Tema oscuro de azul pizarra con paneles en distintos niveles y acento menta. La aplicación debe leerse como una herramienta técnica fiable: navegación reconocible, estado del sistema separado de la configuración, datos con jerarquía y acciones principales fáciles de localizar.

La orientación de trato y personalidad procede de [[Proyecto FRIDAY/IDENTITY]] y [[Proyecto FRIDAY/SOUL]]: calma, precisión, eficiencia y claridad profesional. F.R.I.D.A.Y. orienta la identidad de la experiencia; Aetherion conserva su nombre, alcance y contenido de benchmark.

## Paleta implementada en `theme.py`

| Token | Hex | Uso conceptual |
|---|---|---|
| canvas | `#090D13` | fondo exterior |
| shell | `#0D141D` | marco y área de trabajo |
| surface | `#121C27` | tarjetas y bloques |
| surface_elevated | `#182533` | controles y superficies elevadas |
| surface_interactive | `#223547` | selección e interacción |
| line | `#263746` | bordes sutiles |
| line_strong | `#344B5D` | separación reforzada |
| text | `#F4F7FA` | texto principal |
| text_soft | `#C4CFD9` | texto secundario |
| muted | `#94A6B5` | etiquetas y ayudas |
| quiet | `#728393` | información secundaria |
| accent | `#6DE5C1` | acento y acciones destacadas |
| success | `#9BE0B5` | estado correcto |
| error | `#FF9292` | error |

## Tipografía y controles

- Segoe UI: título, sección, texto de interfaz y etiquetas pequeñas.
- Consolas: registros y valores técnicos monoespaciados.
- Se elevaron los tamaños de cuerpo, microtexto y salida técnica frente a la versión anterior.
- ttk usa `clam` con variantes Aetherion para combobox, scrollbar vertical y progressbar.
- La scrollbar tiene ancho definido, pista de superficie y flecha de tono secundario.
- El progreso hereda el acento menta y usa una pista elevada.

## Estructura de la pantalla

El dashboard reorganizado separa siete regiones: navegación, cabecera, resumen rápido, perfil de hardware, traza de ejecución, configuración y estado de progreso/resultados. La configuración vive en una región desplazable. El patrón se mantiene en las páginas secundarias mediante tarjetas, evitando que cada vista se sienta como una aplicación distinta.

La ventana abre a 1200 × 820 y admite 1020 × 720 como mínimo. Estos valores son objetivos de composición del código, no una garantía de buena presentación en todos los DPI, traducciones o configuraciones del sistema.

## Nota de implementación

La nueva región desplazable usa un `Canvas` con frame hijo. El tamaño y scroll se enlazan a los eventos de configuración. Tkinter no acepta `padx` como argumento de `Canvas.create_window`; el padding se aplica al frame que contiene los controles. La primera excepción por esta opción fue corregida.

## Límites de verificación

- No se hizo una evaluación WCAG formal ni una prueba instrumental de contraste.
- No se comparó una captura final con la captura de referencia.
- No se verificó la escala DPI ni todos los tamaños posibles.
- El fuente llegó al bucle principal de Tkinter, pero el EXE reconstruido mostró `Unhandled exception in script`; la excepción de arranque empaquetado sigue abierta.
- La pantalla rediseñada debe revisarse visualmente desde la versión empaquetada después de corregir el incidente.

## Registro de cambios

La sesión y decisiones detalladas constan en [[Proyecto Aetherion/06_Historial/06_Rediseño_Interfaz_2026-09-30]]. El estado general se mantiene en [[Proyecto Aetherion/00_Gobierno/02_Estado_Actual]].

## Navegación documental

Volver a [[Proyecto Aetherion/02_Cliente/00_Mapa_Cliente]].
