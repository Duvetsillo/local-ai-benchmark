---
knowledge_id: aetherion-20261003-04_refinamiento_visual_2026-10-03
title: Refinamiento visual del cliente — octubre 2026
project: Aetherion
domain: cliente
note_type: decision
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[00-Home/Project Home]]"]
related: []
replaces: []
source_refs: [CHAT-20261003, REPO-20261003]
tags: [aetherion, continuidad, cliente]
---

# Refinamiento visual del cliente — octubre 2026

## Objetivo y criterio de diseño

El objetivo expresado por el usuario es una experiencia visual que encante a los usuarios. Esta meta se traduce en jerarquía clara, contraste legible, uso consistente del acento, acciones fáciles de encontrar y adaptación del texto. El efecto emocional es una intención de producto, no una conclusión probada mediante estudios con usuarios.

El cliente activo se identificó mediante el README y el código: una aplicación de escritorio Tkinter, con entrada en client/desktop.py y sistema visual en client/theme.py. Hay un sitio web y otra copia del cliente, pero esta intervención se aplica al repositorio de trabajo Local_AI_Benchmark. La documentación previa ya describía una base oscura con tarjetas, navegación lateral y acentos menta.

## Sistema visual

La paleta usa fondo #090E16, superficie #111C29, superficie elevada #192838 y superficie interactiva #233B4C. Los bordes discretos usan #243445 y los más visibles #466075. El acento menta es #83E8C5 y su estado hover #B0F4DD. El texto secundario quiet pasa a #93A5B6 para mejorar su legibilidad sobre las superficies oscuras.

Se mantiene Segoe UI para texto y Consolas para información técnica. El tema incorpora roles explícitos para título, métrica y botón, además de display, section, body, small y mono. Esto permite repetir jerarquías con coherencia. No se declara una auditoría completa de accesibilidad ni una certificación de contraste.

## Jerarquía del dashboard

La cabecera aumenta de 66 a 96 píxeles e incorpora una frase contextual por sección. El dashboard presenta la idea de encontrar un modelo adecuado al hardware; modelos invita a explorar la colección; resultados orienta a decidir a partir de mediciones; hardware sitúa la máquina detrás de cada medición; historial explica la utilidad de conservar experimentos.

Las tres tarjetas de resumen conservan runtime activo, modelos locales y último benchmark. Se retiran las tres franjas de acento para reducir la competencia visual con la configuración y el botón principal. El relleno vertical aumenta y los valores pueden ocupar varias líneas según el ancho disponible.

## Acción principal siempre disponible

Antes, Run benchmark estaba dentro del bloque desplazable de configuración. En ventanas pequeñas podía quedar fuera de la zona visible. Ahora reside en un dock inferior del panel derecho, junto a Open results folder. El bloque de configuración se desplaza encima; la acción principal permanece accesible.

Download a model cambia a botón secundario en este panel, para concentrar el énfasis en ejecutar el benchmark. Se conserva Stop benchmark dentro de la configuración y su estado deshabilitado inicial. La intervención no cambia cómo se detiene la ejecución ni cómo se guardan resultados.

## Interacciones y adaptación

Los botones conservan hover y añaden un contorno de foco visible y activación con Enter. Los combobox usan borde menta al recibir foco y una flecha diferenciada en estado deshabilitado. La lista desplegable comparte fondo, texto y selección con el resto de la interfaz.

Los textos de detalles del modelo, suite, runtimes, estado y resumen de ejecución ajustan su longitud de línea al ancho real del contenedor. Las métricas del resumen también ajustan su texto. La barra de progreso usa un grosor de seis píxeles.

## Relación con el resto del producto

[[Proyecto Aetherion/01_Arquitectura/02_Flujo_del_Cliente]] describe el flujo al que sirve esta presentación. [[Proyecto Aetherion/02_Cliente/02_Sistema_Visual]] conserva la base visual anterior. Esta nota añade decisiones compatibles con aquella base y no la declara obsoleta. [[Proyecto Aetherion/04_Calidad/05_Verificacion_Visual_2026-10-03]] registra la evidencia disponible.

## Pendientes

Evaluar la apariencia con usuarios reales, comprobar distintas escalas de Windows y revisar nombres de modelos excepcionalmente largos. Las verificaciones realizadas prueban distribución y comportamiento; no demuestran por sí solas satisfacción del usuario.
