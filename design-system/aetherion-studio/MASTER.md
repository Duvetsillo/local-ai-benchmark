# Aetherion Studio — diseño de la experiencia

## Requisito del usuario

La revisión debe cambiar la estructura y la experiencia. Dos entregas anteriores se percibieron como la misma interfaz con otros colores. El objetivo es una aplicación con presencia, pero útil como herramienta de decisión local. La paleta por sí sola no satisface ese requisito.

## Fuente y límites de la guía

Se ejecutó el comando solicitado de `ui-ux-pro-max` y se leyó su salida completa. Los archivos de apoyo se resolvieron desde la carpeta temporal proporcionada. Se revisaron las referencias de calidad y las reglas de accesibilidad, interacción y rendimiento.

La primera búsqueda de sistema visual mezcló una propuesta comercial Enterprise Gateway y Brutalism, inadecuadas para el cliente. Tras una búsqueda más precisa, Data-Dense Dashboard sí encajó para la presentación de información, pero el patrón comercial siguió sin encajar. No se adoptaron Contact Sales, testimonios, logotipos rotativos ni vídeo. La arquitectura de pantallas se deriva de las tareas reales de Aetherion y de las reglas generales de jerarquía y navegación. No existe un resultado específico para Tkinter entre los stacks soportados; no se presenta una guía web o móvil como si fuese nativa de Tkinter.

La búsqueda de gráficos devolvió Compare Categories: barras para magnitudes discretas, etiquetas directas, orden descendente y tabla de datos accesible. Se aplica a velocidades medidas, con un máximo de cuatro modelos en el gráfico y todas las ejecuciones en la tabla.

## Arquitectura

- Workspace: modelo sugerido según estimación de hardware, resumen del equipo, experimentos recientes y próximos pasos. No contiene el registro técnico ni el formulario completo del benchmark.
- Models: colección en tarjetas, búsqueda por nombre o proveedor, tamaño y compatibilidad estimada. Cada tarjeta permite preparar ese modelo en el laboratorio.
- Benchmark: configuración, suite, ejecución, parada, progreso y registro técnico. Conserva el motor y el almacenamiento existentes.
- Results: comparación de velocidades reales, tabla navegable por teclado, ordenación y apertura de registros guardados. Las suites pueden diferir; el gráfico no expresa calidad universal.
- Hardware, History y Settings: utilidades separadas y visibles en el segundo nivel de navegación.

## Composición y jerarquía

Navegación superior en lugar de la barra lateral anterior. El inicio aprovecha todo el ancho y prioriza la siguiente acción útil. Título editorial grande, tarjeta destacada asimétrica, franja de equipo y paneles de actividad. La marca Studio 03 distingue la entrega estructural de Atelier.

Cada pantalla tiene un propósito y una acción principal. El acceso mantiene el sistema de cuentas existente; no se sustituye por una portada ficticia ni se crean datos de muestra en el usuario. Los estados vacíos explican cómo empezar.

## Estilo e interacción

Tokens de color y tipografía centralizados en el tema. Oro sobre superficies oscuras; la paleta se conserva para que la diferencia evaluada sea la estructura. Tipografía nativa Segoe UI y Consolas, disponibles sin llamadas a servicios de fuentes. No hay iconos emoji en la nueva navegación.

Controles nativos con foco visible, Enter para activar botones y tabla operable por teclado. Búsqueda con etiqueta persistente. Ordenación accesible mediante combobox. La configuración técnica permanece en el laboratorio. El inicio usa un único desplazamiento vertical y revela los controles al recibir foco. Las nuevas vistas no añaden animación ornamental y permanecen estáticas con movimiento reducido.

## Datos y verificación

No inventar puntuaciones, actividad o velocidades. La sugerencia expresa compatibilidad estimada, no una recomendación validada por benchmarks. Las barras muestran el último dato disponible por modelo; una tabla conserva las cifras y permite abrir el registro completo.

Verificar ventanas de 1020×720, 1200×820 y 1600×1000; recorridos de búsqueda, selección, navegación, foco, registro y ordenación. Evaluar las reglas desktop aplicables; las pruebas de móvil y safe areas no corresponden a esta aplicación Windows. No afirmar una certificación completa de accesibilidad ni un flujo de autenticación online que no se haya probado.
