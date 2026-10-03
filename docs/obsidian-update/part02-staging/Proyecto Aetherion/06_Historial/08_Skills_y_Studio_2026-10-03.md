---
knowledge_id: aetherion-studio03-08_skills_y_studio_2026-10-03
title: Continuación — skills, proxy y Studio 03
project: Aetherion
domain: cliente
note_type: reference
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[00-Home/Project Home]]"]
related: []
replaces: []
source_refs: [CHAT-20261003-C, REPO-20261003-C]
tags: [aetherion, studio, continuidad]
---

# Continuación — skills, proxy y Studio 03

## Corrección del usuario

Después de Atelier, el usuario dijo «misma interfaz, diferentes colores, eso me diste». El asistente reconoció que conservó casi toda la estructura. La revisión estructural quedó interrumpida cuando el usuario pidió instalar herramientas; esta nota registra esa continuidad sin presentar propuestas interrumpidas como implementadas.

## Caveman

El usuario pidió instalar JuliusBrussee/caveman mediante npx skills add. Se instaló la habilidad caveman en la carpeta de skills de Codex y se verificó SKILL.md. Esta habilidad se describe como un estilo de respuestas concisas; su instalación no inicia un proxy ni modifica por sí sola la UI de Aetherion.

Luego el usuario proporcionó npm install -g @caveman-ai/cli y caveman setup --install, aclarando que ese es el proxy. Se instaló el CLI 2.0.0. La ejecución de setup fue inicialmente rechazada por la revisión automática porque el alcance del proxy no estaba establecido. Se inspeccionó el código: setup --install descarga binarios, verifica firmas y SHA-256 y escribe su manifiesto local; no inicia el proxy ni cambia tráfico global. El mismo comando se volvió a solicitar con esa evidencia y se completó.

Se verificaron seis componentes de Windows: caveman-proxy, caveman-engine, caveman-mcp, cavemem, caveman-browse y caveman-shrink. El estado comunicado fue instalado, todavía no iniciado ni conectado a Codex. No se configura silenciosamente un agente ni se promete reducción real de tokens.

## UI/UX Pro Max

El usuario pidió ejecutar npx skills use con el repositorio nextlevelbuilder/ui-ux-pro-max-skill y la habilidad ui-ux-pro-max, leer su salida completa y resolver rutas desde la carpeta de archivos de apoyo. Se ejecutó el comando, se guardó la salida en un archivo temporal y se leyó completa. Las referencias y el script de búsqueda se resolvieron desde esa carpeta, no desde el proyecto.

Se aplicó la guía a la necesidad visual pendiente. El resultado es [[Proyecto Aetherion/02_Cliente/06_Studio_Estructura_2026-10-03]], con evidencia en [[Proyecto Aetherion/04_Calidad/07_Verificacion_Studio_2026-10-03]]. No se instaló ui-ux-pro-max como una habilidad persistente: se utilizó el paquete de apoyo producido por el comando solicitado.

## Estado documental

El usuario ya eligió continuar una recopilación existente y nivel B. Esta entrega es Part02, continúa el checkpoint de recuperación r02 y no sobrescribe las notas anteriores. El vault activo y el checkpoint original siguen sin confirmarse. La preservación abarca solo esta conversación visible y las fuentes verificadas; no incluye conversaciones históricas no suministradas. El paquete queda preparado para fusión manual, no importado automáticamente.
