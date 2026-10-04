---
knowledge_id: aetherion-atelier-06_verificacion_atelier_2026-10-03
title: Verificación de la revisión Atelier
project: Aetherion
domain: cliente
note_type: evidence
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/04_Calidad/00_Mapa_Calidad]]"]
related: []
replaces: []
source_refs: [CHAT-20261003-B, REPO-20261003-B]
tags: [aetherion, atelier, continuidad]
---

> [!info] Lectura al 3 de octubre de 2026
> Nota del paquete incremental anterior, ahora incorporada al vault activo. Las menciones a fusión pendiente describen el estado al preparar aquel paquete; consultar el registro de organización actual.


# Verificación de la revisión Atelier

## Evidencia de esta revisión

Las 18 pruebas del repositorio pasaron después de los cambios. La comprobación de distribución recorrió todas las vistas a 1200×820, 1020×720 y 1600×1000, verificando altura útil del área de configuración, contención del botón principal dentro del dock y foco de teclado.

Una segunda comprobación construyó la pantalla de acceso sin restaurar una sesión real. En cada tamaño se revisaron los modos login y register. Login conserva username y password; register conserva además confirm y license_key. Se verificó que la URL configurada permanece disponible, que Connection settings muestra y oculta los controles y que el botón de enviar queda accesible al desplazar el panel al final.

No se enviaron credenciales ni se contactó el servicio de autenticación durante estas comprobaciones. La ejecución de código de UI no sustituye una inspección visual completa ni una prueba de satisfacción. Tampoco valida un benchmark con modelos reales.

## Construcción

Se recompiló el cliente con el runtime local de Python y PyInstaller, utilizando las dependencias aisladas que se prepararon en la sesión anterior. Se verificó en el paquete final la inclusión de Tcl, Tk y la identidad ATELIER. Windows impidió sustituir el archivo previo de downloads porque seguía en uso. Se entregó el nuevo binario como Aetherion-Atelier.exe; su barra de título también distingue Atelier. El ejecutable previo no se da por actualizado.

La falta de apertura indicada por el usuario tras el primer intento se conserva como observación en [[Proyecto Aetherion/06_Historial/07_Correccion_Visual_2026-10-03]]. No hay un traceback suficiente para atribuirla a un fallo concreto. No se declara resuelto un incidente de arranque histórico por estas pruebas.

## Límites

Quedan pendientes una autenticación completa en el ejecutable distribuible, una ejecución de benchmark real y revisión de la apariencia en distintas escalas DPI. La prueba de accesibilidad del botón es geométrica y funcional; no certifica que cada elemento de la UI cumpla una norma de accesibilidad.

Comparar con [[Proyecto Aetherion/04_Calidad/05_Verificacion_Visual_2026-10-03]] para entender qué comprobaciones se hicieron en cada intervención. La prueba de formulario corresponde a esta revisión.

## Navegación documental

Volver a [[Proyecto Aetherion/04_Calidad/00_Mapa_Calidad]].
