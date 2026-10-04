---
knowledge_id: vault-20261003-proyecto-aetherion-06-historial-archivo-documental-00-moc-aetherion-corte-anterior
title: "Corte anterior — 00_MOC_Aetherion"
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
source_refs: ["[[Proyecto Aetherion/00_Gobierno/00_MOC_Aetherion]]"]
tags: ["aetherion", "area/06-historial", "evidence"]
---

# Corte anterior — 00_MOC_Aetherion
> [!abstract] Registro histórico preservado
> Copia del contenido encontrado antes de esta reorganización. Puede contener estados ya corregidos; para operar consulta [[Proyecto Aetherion/00_Gobierno/02_Estado_Actual]].

---
proyecto: Aetherion
tipo: mapa-de-contenido
fecha_revision: 2026-09-30
estado: documentacion-inicial
tags: [aetherion, local-ai, indice]
---

# Aetherion — mapa del proyecto

Índice del proyecto Local AI Benchmark y su cliente de escritorio Aetherion. Las notas distinguen hechos del repositorio, observaciones de sesión, hipótesis y tareas pendientes.

## Lectura rápida

- [[Proyecto Aetherion/00_Gobierno/01_Resumen_Ejecutivo]] — propósito, usuario y propuesta de valor.
- [[Proyecto Aetherion/00_Gobierno/02_Estado_Actual]] — corte observado al 30 de septiembre de 2026.
- [[Proyecto Aetherion/00_Gobierno/03_Alcance_y_Principios]] — límites del producto.
- [[Proyecto Aetherion/00_Gobierno/04_Vinculacion_Core]] — relación con Ultron y F.R.I.D.A.Y.
- [[Proyecto Aetherion/00_Gobierno/05_Referencias_Rapidas]] — rutas y referencias prácticas.

## Arquitectura y producto

- [[Proyecto Aetherion/01_Arquitectura/01_Arquitectura_General]]
- [[Proyecto Aetherion/01_Arquitectura/02_Flujo_del_Cliente]]
- [[Proyecto Aetherion/01_Arquitectura/03_Mapa_del_Codigo]]
- [[Proyecto Aetherion/01_Arquitectura/04_Proveedores_Locales]]
- [[Proyecto Aetherion/01_Arquitectura/05_Suite_de_Benchmarks]]
- [[Proyecto Aetherion/01_Arquitectura/06_Perfil_de_Hardware]]
- [[Proyecto Aetherion/01_Arquitectura/07_Formato_de_Resultados]]

## Cliente de escritorio

- [[Proyecto Aetherion/02_Cliente/01_Experiencia_y_Pantallas]]
- [[Proyecto Aetherion/02_Cliente/02_Sistema_Visual]]
- [[Proyecto Aetherion/02_Cliente/03_Guia_de_Uso]]

## Datos, calidad y planificación

- [[Proyecto Aetherion/03_Datos_y_Operaciones/01_Privacidad_y_Almacenamiento]]
- [[Proyecto Aetherion/03_Datos_y_Operaciones/02_Instalacion_y_Uso_Local]]
- [[Proyecto Aetherion/03_Datos_y_Operaciones/03_Compilacion_Windows]]
- [[Proyecto Aetherion/04_Calidad/01_Estrategia_de_Verificacion]]
- [[Proyecto Aetherion/04_Calidad/02_Incidente_Arranque_Cliente]]
- [[Proyecto Aetherion/04_Calidad/03_Guia_de_Diagnostico]]
- [[Proyecto Aetherion/04_Calidad/04_Riesgos_y_Controles]]
- [[Proyecto Aetherion/05_Roadmap/01_Roadmap]]
- [[Proyecto Aetherion/05_Roadmap/02_Decisiones_Tecnicas]]
- [[Proyecto Aetherion/06_Historial/01_Cronologia]]
- [[Proyecto Aetherion/06_Historial/02_Fuentes_y_Certeza]]
- [[Proyecto Aetherion/06_Historial/03_Glosario]]
- [[Proyecto Aetherion/06_Historial/04_Mapa_de_Artefactos]]
- [[Proyecto Aetherion/06_Historial/05_Plantilla_de_Sesion]]

## Estado de confianza

La documentación se contrastó con README, código fuente, configuración PyInstaller, script de build, pruebas listadas e historial Git. No certifica que las pruebas se ejecutaron ni que el cliente empaquetado funcione. El incidente de arranque permanece abierto sin traceback confirmado.

## Mantenimiento

Actualizar estado y cronología al cerrar cada hito; registrar decisiones con fecha y motivo; mantener los vínculos. Nunca copiar secretos, certificados privados o resultados locales sensibles aquí.

## Interfaz de escritorio — revisión 2026-09-30

- [[Proyecto Aetherion/06_Historial/06_Rediseño_Interfaz_2026-09-30]] — alcance del rediseño, decisiones visuales, archivos, compilación, corrección de Tkinter y límites de verificación.
- [[Proyecto Aetherion/02_Cliente/02_Sistema_Visual]] — paleta actual, tipografía, composición y límites de revisión.
- [[Proyecto Aetherion/04_Calidad/02_Incidente_Arranque_Cliente]] — excepción persistente del ejecutable empaquetado y plan de diagnóstico.

El cliente fue reorganizado y recompilado; la compilación de la descarga aún presenta un diálogo de excepción. Consultar [[Proyecto Aetherion/00_Gobierno/02_Estado_Actual]] antes de considerar la distribución lista.


## Acceso y licenciamiento

- [[Proyecto Aetherion/06_Historial/07_Licenciamiento_Offline_2026-09-30]] — activación obligatoria, planes, generación y firma offline, archivos, estado y continuidad.
- [[Proyecto Aetherion/04_Calidad/02_Incidente_Arranque_Cliente]] — incidente de arranque del EXE que bloquea la validación y publicación de la función.


## Cliente licenciado y cancelación

- [[Proyecto Aetherion/06_Historial/08_Generador_Licencias_y_Detener_Benchmark_2026-09-30]] — administrador gráfico separado, custodia DPAPI, planes de licencia, bloqueo de activación, detención cooperativa, estado de distribución y continuidad.
- Administrador del propietario en el Escritorio: `C:\Users\Dayve\Desktop\Aetherion License Manager\Start-Aetherion-License-Manager.bat`.
## Cuentas, renovaciones y servicio central — 2026-09-30

- [[Proyecto Aetherion/06_Historial/09_Cuentas_Servicio_Renovacion_2026-09-30]] — diseño e integración detallada del alta por clave, cuenta ligada a dispositivo, acceso por contraseña, panel administrativo, renovación sin segunda clave, VPS configurable, almacenamiento, seguridad, pase offline de siete días y checklist de despliegue/build.
- Servicio de referencia en `server/`; License Manager en `tools/Aetherion-License-Manager.ps1` y `C:\Users\Dayve\Desktop\Aetherion License Manager\`.
- La URL pública no está elegida, el servidor no está desplegado y el EXE no se ha reconstruido con esta integración. El estado es fuente implementada con despliegue y validación manual pendientes.
- Las claves generadas antes del backend se pueden importar desde el control **Sync existing key**; no es necesario emitirlas otra vez para darlas de alta en el servidor.


> [!success] Build del cliente — 2026-09-30
> El error de PyInstaller se identificó como dependencia ausente `cryptography`, se corrigió y la build nueva quedó abierta en la pantalla de cuenta. Ver [[Proyecto Aetherion/04_Calidad/02_Incidente_Arranque_Cliente]] y [[Proyecto Aetherion/06_Historial/09_Cuentas_Servicio_Renovacion_2026-09-30]]. El VPS sigue pendiente de dominio.
