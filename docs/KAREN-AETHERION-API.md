# Contrato local Karen → Aetherion, v1

Base: `http://127.0.0.1:8766`. Servicio nuevo del paquete Aetherion; no es el dashboard `:8765` ni el servidor de cuentas. Solo escucha en loopback. Karen no debe usar `/api/run` del dashboard para esta integración.

## Acceso

Todas las rutas requieren `Authorization: Bearer <integration_token>`. El servicio crea un secreto local protegido con DPAPI para el usuario Windows; el helper `local_ai_benchmark.integration.load_integration_token()` lo lee sin imprimirlo. Karen puede importar el helper/cliente del paquete instalado en su entorno. No copiar el token a Obsidian, logs, Git ni parámetros de URL.

La credencial local NO concede una licencia. El servicio reutiliza y comprueba la sesión guardada de Aetherion mediante `AccountService.restore_cached(machine_fingerprint())`, con sus validaciones online/offline existentes. El usuario inicia sesión en Studio una vez; Karen no pide de nuevo la contraseña. Sin esa autorización, las operaciones reciben `403 license_required`. Cancelar un trabajo propio sigue permitido con el Bearer para poder detener consumo si vence el acceso.

## Rutas estables

| Método/ruta | Respuesta |
| --- | --- |
| `GET /v1/nodes` | `{"nodes":[{"id":"pc","provider":"ollama"}],"categories":["general","coding","math","json","spanish"]}` |
| `GET /v1/models?node=pc` | `{"node":"pc","models":[{"name":"qwen2:0.5b","provider":"ollama","size_bytes":352164041,"details":{}}]}` |
| `POST /v1/benchmarks` | `202` con snapshot de trabajo; no espera el benchmark |
| `GET /v1/benchmarks/{id}` | `200` con snapshot de estado/progreso |
| `GET /v1/benchmarks/{id}/results` | `200` con resultados parciales o completos del motor |
| `POST /v1/benchmarks/{id}/cancel` | `200` con snapshot; cancelación cooperativa e idempotente |

El operador registra nodos al iniciar; por defecto `pc` apunta a Ollama localhost. El ID `homelab` existe solo si se configura `--node homelab=http://192.168.100.66:11434`. La petición no acepta URL, ruta de archivo, código o prompt arbitrario. Los modelos son los instalados en el nodo; no hay descarga automática.

## Inicio explícito

```json
{
  "request_id": "UUID-generado-por-Karen",
  "node": "pc",
  "model": "qwen2:0.5b",
  "category": "math",
  "temperature": 0.0,
  "context": 4096,
  "max_seconds": 180,
  "confirm": true
}
```

`request_id` debe ser UUID, creado al pulsar el botón; reutilizarlo al reintentar esa misma petición. El mismo ID y parámetros devuelven el mismo trabajo (`200` en reintento); cambiar parámetros con el mismo ID da `409 request_id_conflict`. `confirm` debe ser el booleano `true`. Categoría obligatoria y válida: evita iniciar toda la suite por defecto. Contexto entero 256–8192; temperatura finita 0–2; duración entera 10–300 segundos. La duración y la cancelación señalan stop: no garantizan interrupción instantánea de un proveedor bloqueado. Un solo trabajo activo en este servicio; otro inicio devuelve `409 busy`.

## Snapshot

```json
{
  "id": "UUID-del-trabajo",
  "request_id": "UUID-del-cliente",
  "node": "pc",
  "model": "qwen2:0.5b",
  "category": "math",
  "status": "running",
  "completed": 0,
  "total": 1,
  "cancel_requested": false,
  "stop_reason": null,
  "created_at": "ISO-8601-UTC",
  "finished_at": null,
  "error": null,
  "result_url": "/v1/benchmarks/UUID-del-trabajo/results",
  "hardware_scope": "api_host"
}
```

Estados: `queued`, `running`, `stopping`, `completed`, `stopped`, `failed`. Terminales: los tres últimos. `completed` cuenta tareas terminadas, no porcentaje de tokens. Consultar cada 1–2 segundos. El progreso se actualiza al cerrar cada tarea, igual que el motor existente. Un trabajo puede terminar `completed` con errores del proveedor en sus resultados: revisar `error` de cada elemento y no presentar checks aprobados si hay errores.

Resultados: `{"id":"…","status":"…","hardware_scope":"api_host","results":[<BenchmarkResult.to_dict()>]}`. Conservar el JSON de Aetherion como fuente. La tarea interrumpida se descarta y se conservan las terminadas. El perfil/CPU/RAM/GPU que mide el motor son de la PC donde corre la API, incluso si el runtime está en Homelab; no etiquetarlos como hardware remoto. No duplicar puntuaciones o mediciones en Karen.

## Errores

Formato `{"error":{"code":"…","message":"…"}}`. Códigos: `401 unauthorized`, `403 license_required`, `404 not_found`/`unknown_node`, `400 invalid_request`/`model_not_installed`, `409 busy`/`request_id_conflict`, `413 payload_too_large`, `503 provider_unavailable`, `500 internal_error`. JSON máximo 16 KiB. No hay CORS para navegador ni autenticación por query. El token de integración no es el token administrativo del servidor.

## Inicio

Desde el repositorio, con Python y dependencias del paquete disponibles:

```powershell
$env:PYTHONPATH = "$PWD\src"
py -3.11 -m local_ai_benchmark integration-api --node homelab=http://192.168.100.66:11434
```

No arranca benchmarks al iniciar el servicio o listar modelos. Guarda resultados en la carpeta de Aetherion del perfil local. IDs y consulta son de esta instancia; tras reinicio los trabajos antiguos no se sirven desde memoria. Los JSON permanecen en disco. Al cerrar la API se solicita cancelación y se espera al trabajador; no cerrar a la fuerza si se quiere preservar resultados.
