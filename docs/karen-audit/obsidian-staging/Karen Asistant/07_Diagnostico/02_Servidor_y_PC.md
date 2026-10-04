---
knowledge_id: "karen-audit-20261003-02"
title: "Karen — servidor, PC y resultados de conexión"
project: "Karen"
domain: "diagnostico"
note_type: "evidence"
version: "1.0.0"
status: "current"
created: "2026-10-03"
updated: "2026-10-03"
up: ["[[Karen Asistant/07_Diagnostico/00_KAREN_Diagnostico_2026-10-03]]"]
related: []
replaces: []
source_refs: ["AUDIT-KAREN-20261003", "CHAT-KAREN-20261003"]
tags: ["karen", "diagnostico", "sesion-2026-10-03"]
---

# Karen — servidor, PC y resultados de conexión

## Endpoints comprobados desde esta PC

| Destino | Prueba | Resultado |
| --- | --- | --- |
| 192.168.100.66:3000 | GET `/api/version` | 200 JSON, version 0.9.6 y deployment_id |
| 192.168.100.66:3000 | GET `/api/tags` | 200 HTML, no catálogo JSON de Ollama |
| 192.168.100.66:3000 | POST `/api/generate` | 405; no respuesta válida de generación |
| 127.0.0.1:11434 | GET version/tags | 200 JSON, Ollama 0.35.1 y catálogo |
| 192.168.100.66:11434 | GET version/tags | 200 JSON, Ollama 0.30.6 y catálogo |
| 192.168.100.66:5000 | GET `/salud` | 200 JSON con campo estado |
| 192.168.100.66:5000 | GET `/health` | 404; la ruta de salud documentada es `/salud` |

El endpoint 3000 no cumple el contrato que espera KarenClient. La forma de sus respuestas sugiere una capa web distinta, pero no se inspeccionó su despliegue: no atribuir un producto concreto como hecho confirmado.

## Generación real acotada

Se envió únicamente el prompt sintético «Responde solamente OK.», con ocho tokens máximos, temperatura cero, sin streaming y residencia del modelo limitada a 30 s. No se enviaron conversaciones, memoria de Obsidian ni audio del usuario.

| Nodo | Modelo existente | Respuesta | Tiempo observado |
| --- | --- | --- | --- |
| PC | qwen2:0.5b | OK | 2,75 s |
| Homelab Ollama | llama3.2:3b | OK. | 21,53 s |

Estos tiempos incluyen carga y condiciones de esa petición. Los modelos son diferentes; la prueba no permite concluir que la PC sea cierta cantidad de veces más rápida ni determinar la mejor calidad. No se midieron repeticiones, primer token, GPU o concurrencia.

## Modelos visibles

- PC: gemma3:1b, llama3.2:3b, qwen2.5-coder:3b, qwen3:4b y qwen2:0.5b.
- Homelab: llama3.2:3b, qwen2.5:7b y gemma3:1b.

El modelo predeterminado `qwen2:0.5b` no apareció en el catálogo del Homelab. Cambiar solo el puerto manteniendo ese modelo no asegura que la petición funcione: configurar un modelo realmente instalado en cada nodo.

## Falso éxito de la prueba de conexión

KarenClient.test_connection acepta la primera respuesta JSON exitosa de `/api/version`; no valida catálogo ni generación. En el puerto 3000 devuelve éxito, aunque `/api/generate` da 405. La siguiente implementación debe separar transporte, contrato de API, catálogo, modelo disponible y generación.

## Servicio Flask histórico

La documentación antigua usa POST `/chat` con `mensaje` y devuelve `respuesta`. El cliente actual usa `/api/generate` con `prompt` y espera `response`. Son contratos distintos. `/salud` respondió, pero no se ejecutó `/chat` para no insertar mensajes en un historial remoto posiblemente compartido; tampoco se accedió por SSH ni se inspeccionó systemd o el código remoto.

Para alternar entre nodos, empezar con perfiles explícitos de endpoint, tipo de adaptador y modelo. La conmutación automática sigue siendo una propuesta para la próxima sesión.
