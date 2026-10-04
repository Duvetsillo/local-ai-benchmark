---
knowledge_id: vault-20261003-proyecto-aetherion-05-roadmap-01-roadmap
title: "Aetherion — próximos pasos verificables"
project: Aetherion
domain: 05_Roadmap
note_type: task
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/05_Roadmap/00_Mapa_Roadmap]]"]
related: []
replaces: []
source_refs: ["[[Proyecto Aetherion/00_Gobierno/02_Estado_Actual]]"]
tags: ["aetherion", "area/05-roadmap", "task"]
---

# Aetherion — próximos pasos verificables
## Base ya documentada

El incidente histórico de `cryptography` tiene cierre registrado. Studio 03 tiene build y 18 pruebas aprobadas, más comprobaciones de interfaz acotadas. Esas evidencias no equivalen a aceptación visual ni validación comercial.

## 1. Aceptación del cliente

- [ ] Revisar visualmente Studio 03 con el usuario y capturas.
- [ ] Comprobar escalas DPI y lector de pantalla.
- [ ] Ejecutar un benchmark real, detenerlo y verificar el JSON y registros anteriores.

Cierre: evidencia del artefacto, entorno y recorrido completo; ver [[Proyecto Aetherion/04_Calidad/00_Mapa_Calidad]].

## 2. Servicio de cuentas

- [ ] Definir VPS/dominio y desplegar HTTPS.
- [ ] Probar alta por clave, login/logout, renovación sin nueva clave y suspensión.
- [ ] Probar recuperación, persistencia y pase offline limitado en equipos controlados.

Cierre: pruebas con cuenta de ensayo y sin secretos en las notas; ver [[Proyecto Aetherion/07_Licencias_y_Cuentas/00_Mapa_Licencias_y_Cuentas]].

## 3. Repetibilidad y evaluación

- [ ] Unificar metadatos de runtime y versión.
- [ ] Mantener lectores para los formatos del motor y cliente.
- [ ] Diseñar validadores más exigentes y casos adversariales.
- [ ] Evaluar repeticiones estadísticas y exportación revisada.

## 4. Operación e historial

- [ ] Definir retención de resultados y recuperación.
- [ ] Registrar hash, versión y evidencia en cada release.
- [ ] Actualizar estado y fuentes sin borrar los registros históricos.

El roadmap previo queda íntegro en [[Proyecto Aetherion/06_Historial/Archivo_Documental/01_Roadmap_Corte_Anterior]]. Estas listas son trabajo pendiente, no funcionalidades nuevas.
