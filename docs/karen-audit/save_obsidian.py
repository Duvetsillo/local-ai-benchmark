from pathlib import Path
import hashlib, importlib.util, json, re, sys

HERE=Path(__file__).parent
VAULT=Path(r'C:\Obsidian\Data Base')
BASE='Karen Asistant/07_Diagnostico/'
HUB=BASE+'00_KAREN_Diagnostico_2026-10-03.md'
DATE='2026-10-03'
STAGE=HERE/'obsidian-staging'
notes={}

def link(p,label=None):return '[['+p.removesuffix('.md')+('|' +label if label else '')+']]'
def add(name,title,body,kind='reference',refs=None):
    rel=BASE+name+'.md'
    parent='Karen Asistant/01_Core/KAREN.md' if rel==HUB else HUB
    hdr={'knowledge_id':'karen-audit-20261003-'+name.split('_',1)[0], 'title':title,'project':'Karen','domain':'diagnostico',
         'note_type':kind,'version':'1.0.0','status':'current','created':DATE,'updated':DATE,'up':[link(parent)],
         'related':[],'replaces':[],'source_refs':refs or ['AUDIT-KAREN-20261003','CHAT-KAREN-20261003'], 'tags':['karen','diagnostico','sesion-2026-10-03']}
    notes[rel]='---\n'+'\n'.join(k+': '+json.dumps(v,ensure_ascii=False) for k,v in hdr.items())+'\n---\n\n# '+title+'\n\n'+body.strip()+'\n'

def prepare():
    add('00_KAREN_Diagnostico_2026-10-03','Karen — diagnóstico y continuidad del 3 de octubre',
        '''> [!summary] Resultado
> La PC y el Homelab pueden generar respuestas. El cliente actual no está conectado correctamente a ese flujo: su URL predeterminada usa el puerto 3000, el detector de micrófono rechaza DeviceList y el lanzador contiene opciones incompatibles.

## Pedido de esta sesión

El usuario pidió revisar completamente `C:\\Karen`, decir qué funciona, guardar el diagnóstico en Obsidian y dejar un mensaje al terminar para poder apagar la PC. El refinamiento y la conexión funcional se retomarán en la próxima sesión.

El objetivo acordado es una interfaz única y dinámica para Karen, con elección entre el servidor del Homelab y la PC principal de uso personal. El servidor es una opción, y la PC debe poder sostener el funcionamiento cuando el servidor no esté disponible. Se propuso mantener captura y wake word en la PC para que la activación no dependa de la conectividad. El cambio automático de nodo es una propuesta posterior a estabilizar la selección manual.

## Qué funciona, con evidencia

| Componente | Resultado observado | Alcance |
| --- | --- | --- |
| Código Python | Los cuatro módulos se pueden analizar | Sintaxis, no todo el comportamiento |
| GUI Tkinter | Se construyó a 980 × 760 en Python 3.11 y 3.14 | Comprobación de widgets; sin revisión visual completa |
| Dependencias 3.11 | Todas las dependencias importadas de la lista están disponibles | No implica compatibilidad de todas sus funciones |
| Ollama en la PC | HTTP 200, respuesta «OK», con qwen2:0.5b | Inferencia real mínima |
| Ollama en Homelab | HTTP 200, respuesta «OK.», con llama3.2:3b | Inferencia real mínima |
| API histórica de Karen | `/salud` responde HTTP 200 | No se probó `/chat` ni se revisó el servicio remoto |
| Whisper base | Transcribió el MP3 existente en CPU | No se grabó ni probó voz en vivo |
| ONNX | Carga en CPU y produce salida finita | No se probó detección real de la palabra |
| ffmpeg y ffprobe | Ejecutan y reconocen el MP3 | No se reprodujo audio |

## Navegación del diagnóstico

- '''+link(BASE+'01_Inventario_y_Entorno.md')+''': archivos, runtimes y recursos.
- '''+link(BASE+'02_Servidor_y_PC.md')+''': endpoints, modelos y generación real.
- '''+link(BASE+'03_Voz_y_Wakeword.md')+''': micrófono, Whisper, ONNX y respuesta hablada.
- '''+link(BASE+'04_Fallos_del_Cliente.md')+''': fallos reproducidos y riesgos del código.
- '''+link(BASE+'05_Plan_Proxima_Sesion.md')+''': orden de implementación y criterios de cierre.
- '''+link(BASE+'06_Fuentes_y_Limites.md')+''': fuentes, conservación y lo que no se verificó.

## Relación con el historial

Las notas de septiembre describen otro flujo: wake word ONNX → Whisper → Flask `/chat` → Ollama → Edge-TTS. El `cliente.py` actual no corresponde a esa implementación. Se conservan las notas antiguas como fuentes históricas y se registra esta diferencia, sin borrarlas ni atribuir al modelo v2 una validación inexistente.

''' +link('Karen Asistant/01_Core/KAREN_Arquitectura.md')+' · '+link('Karen Asistant/02_Roadmap/KAREN_Estado_Actual.md')+' · '+link('Karen Asistant/KAREN_Cliente_Streaming.md'), 'evidence')
    add('01_Inventario_y_Entorno','Karen — inventario y entorno de ejecución',
        '''## Carpeta inspeccionada

`C:\\Karen` contiene `cliente.py`, `config.py`, `requirements.txt`, `start_karen.ps1`, dos scripts de diagnóstico de micrófono, `karen.onnx`, `ffmpeg.exe`, `ffprobe.exe`, una muestra MP3, `.env.example`, configuración de VS Code y archivos de caché Python. La enumeración recursiva encontró 16 archivos. No se encontró `server.py`, scripts de entrenamiento, pruebas automatizadas ni un repositorio `.git` dentro de esta carpeta. Esto no demuestra que no existan en otro equipo.

| Archivo | Función observada |
| --- | --- |
| cliente.py | GUI Tkinter y cliente directo de API Ollama |
| config.py | Dataclass, valores predeterminados, variables de entorno y validación |
| start_karen.ps1 | Lanzamiento con Python 3.11; contrato desalineado con parse_args |
| diagnose_devices.py | Captura desde índices fijos 31, 33 y 41; no ejecutado |
| diagnose_mic.py | Captura de diez segundos desde índice fijo 4; no ejecutado |
| karen.onnx | Modelo con entrada de features 1 × 28 × 96; no usado por cliente.py |
| muestra_friday_dalia.mp3 | Muestra existente de 13,92 s, mono, 24 kHz; no se modificó |
| .vscode/launch.json | Perfiles de servidor y activación manual; contiene un flag rechazado |

## Runtimes comprobados

- Python 3.11.9: NumPy 2.4.6, requests 2.34.2, sounddevice 0.5.6, SpeechRecognition 3.17.0, PyAudio 0.2.14, Whisper 20250625, ONNX Runtime 1.29.0, openWakeWord 0.6.0, Edge-TTS 7.2.8, soundfile 0.14.0, pyttsx3 2.99, Torch 2.13.0 y Tk 8.6 importan.
- Python 3.14.7: GUI y mayoría de imports disponibles, pero faltan PyAudio y pyttsx3. Tk es 9.0, ONNX Runtime 1.30.0 y Torch 2.14.0.
- El launcher `py` reconoce ambas versiones; `python` en PATH apunta a 3.14. El script selecciona 3.11 explícitamente.

Para la siguiente sesión conviene usar 3.11 como base conocida de diagnóstico. Los requirements no fijan versiones y no existe un entorno virtual dentro de C:\\Karen; preparar un entorno reproducible antes de ampliar la implementación.

## PC principal observada

Windows 11 Home, AMD Ryzen 5 5500, seis núcleos y doce hilos, aproximadamente 15,87 GiB de RAM visible y GPU NVIDIA RTX 2060. También aparece el adaptador spacedesk. La lectura puntual mostró 2,71 GiB libres, no una medida de pico ni de memoria disponible permanentemente. No se confirmó VRAM ni aceleración CUDA de Whisper.

Ollama estaba ejecutándose en la PC. Los pesos Whisper `tiny.pt` y `base.pt` ya estaban en caché. No se instalaron paquetes ni se descargaron modelos durante el diagnóstico.

## Configuración

El valor efectivo era servidor `http://192.168.100.66:3000`, modelo `qwen2:0.5b`, Whisper base y dispositivo de entrada sin selección explícita. No había API key efectiva. No hay `.env` en la carpeta y el código no carga archivos dotenv: `.env.example` sirve de referencia, no se aplica automáticamente. No se copian claves ni tokens a las notas.''')
    add('02_Servidor_y_PC','Karen — servidor, PC y resultados de conexión',
        '''## Endpoints comprobados desde esta PC

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

Para alternar entre nodos, empezar con perfiles explícitos de endpoint, tipo de adaptador y modelo. La conmutación automática sigue siendo una propuesta para la próxima sesión.''', 'evidence')
    add('03_Voz_y_Wakeword','Karen — audio, Whisper y wake word',
        '''## Micrófono

Windows y sounddevice enumeran el Fifine, entradas de audio integrado y VB-Audio. El dispositivo de entrada predeterminado observado fue 1; varios dispositivos aceptan mono int16 a 16 kHz según check_input_settings. Se verificó formato, no calidad acústica ni captura en vivo.

El fallo reproducido está en detect_microphone: usa `isinstance(devices, list)`, pero query_devices devuelve DeviceList y esa comprobación es falsa. No recorre ningún dispositivo, retorna None y la GUI deshabilita «Activar micrófono». La misma condición se reprodujo en 3.11 y 3.14.

Además, la enumeración de sounddevice y la de sr.Microphone/PyAudio no deben tratarse como índices intercambiables sin comprobar el dispositivo concreto. El código mezcla ambas rutas. Los scripts diagnósticos tienen índices fijos que ya no son una selección fiable: el índice 4 ni aparece como entrada en la enumeración actual. No se ejecutaron esos scripts, porque graban audio.

## Whisper

Whisper base cargó desde el archivo de caché existente, en CPU. Transcribió el MP3 local de 13,92 s, detectando español y generando 153 caracteres en tres segmentos. La operación duró aproximadamente 5,66 s. Se conservó la medida, no el texto de la grabación. No se descargó modelo ni se capturó voz nueva.

El cliente fija `model="base"` en recognize_whisper aunque config.py permita whisper_model. La ruta de voz con sr.Microphone no se completó; faltaría ensayar el reconocimiento real usando el Fifine y el runtime elegido.

## Modelo karen.onnx

El archivo de 350.767 bytes cargó con ONNX Runtime en CPU. Entrada float de forma `[1,28,96]`, salida karen `[1,1]`. SHA-256: `9378bf0706a486bf115b01f6d027b09bae23b90babafedef52f0585fbdde1c27`.

Una entrada sintética de features completamente cero produjo aproximadamente 0,90089. Esto es una señal que merece investigar, pero **no es una prueba con silencio real**: features cero no equivalen necesariamente a la representación de audio silencioso. No prueba por sí sola falsos positivos ni identifica si el archivo es v1 o v2.

El cliente actual no importa openWakeWord u ONNX Runtime ni abre este archivo. La activación implementada consiste en transcribir una frase y buscar la subcadena “karen”, borrar sus apariciones y enviar el resto. Después desactiva la escucha. No es el pipeline ONNX continuo con warm-up y confirmaciones descrito en las notas históricas.

## Respuesta hablada

Edge-TTS y pyttsx3 están disponibles en 3.11. ffmpeg y ffprobe funcionan; la muestra MP3 es legible. Sin embargo, cliente.py no genera ni reproduce TTS. El campo «Voz» se lee al guardar, pero no conecta con un sintetizador ni se persiste.

No se probó síntesis online de Edge-TTS ni reproducción de altavoces. No llamar «asistente de voz completo» a una ventana que solo muestra texto. Para la próxima sesión se debe definir TTS principal y alternativa local, estados de audio y prevención de que Karen se reactive por su propia voz.

## Historial relevante

''' +link('Karen Asistant/KAREN_Error8_WakeWordV2.md')+''' describe falsos positivos de la v1 y negativos de habla para reentrenamiento. '''+link('Karen Asistant/KAREN_Cliente_Streaming.md')+''' describe streaming, warm-up y confirmación consecutiva. Son antecedentes útiles, pero no se confirmó que esa implementación esté en el archivo actual ni que el modelo actual haya superado su validación.''','evidence')
    add('04_Fallos_del_Cliente','Karen — fallos reproducidos y riesgos del cliente',
        '''## Bloqueos reproducidos

| Prioridad | Hallazgo | Evidencia | Acción siguiente |
| --- | --- | --- | --- |
| P0 | Configuración de endpoint incompatible | Generación en 3000 retorna 405; catálogo es HTML | Perfiles de API correctos y prueba de contrato |
| P0 | No detecta el micrófono | DeviceList no es list; GUI muestra botón disabled | Corregir selección y comprobar índice en el backend de captura |
| P0 | Lanzador no corresponde al parser | --whisper-model, --no-wake-word y --input-device rechazados con salida 2 | Alinear CLI, launcher y perfiles VS Code |
| P1 | Guardar no persiste | Cambia KarenClient, pero no actualiza la dataclass ni escribe archivo | Guardado validado y recuperación al reiniciar |
| P1 | Wake word ONNX desconectado | Sin carga o inferencia de karen.onnx en cliente.py | Reconectar pipeline y medir falsas activaciones |
| P1 | Respuesta hablada ausente | No hay llamada a TTS o reproducción | Conectar síntesis y ciclo de audio |

El contrato CLI se comprobó ejecutando la función parse_args extraída del AST, sin arrancar escucha ni el script completo. Los argumentos --server, --model y --api-key sí se aceptan. El launcher pasa --whisper-model siempre, por lo que falla antes de abrir el programa. También usa cliente.py por ruta relativa sin fijar el directorio al del script.

## Configuración desconectada

Se comprobó la validación de URL, límites positivos y overrides. Pero muchas opciones del dataclass no se usan en el flujo actual: input_device, wake_word_enabled, umbrales, sample_rate, command_seconds, voice_rate, voice_pitch, memory_dir y memory_files. Whisper base y timeout 90 aparecen fijados directamente.

El botón Guardar prepara un cliente HTTP nuevo; no escribe configuración ni modifica self.config. La prueba de widgets con una URL inicial distinta confirmó que client.server cambia y config.server conserva el valor anterior. El nombre de la acción induce a esperar persistencia que no existe.

## Hilos y estados de interfaz

test_api, send_prompt y listen_loop llaman a log o config de widgets desde hilos secundarios. El código solo usa root.after para una actualización puntual. Se observó el patrón en fuente; no se forzó una excepción ni se realizó una prueba de concurrencia. Centralizar eventos en el hilo de GUI debe formar parte de la estabilización.

La escucha no maneja completamente la apertura de sr.Microphone dentro de su try, porque el contexto se abre antes del bucle de captura. Un fallo al abrir podría finalizar el hilo dejando un estado de escucha incorrecto. Tras una detección el cliente apaga la escucha en vez de volver automáticamente a esperar el nombre.

El cliente permite múltiples envíos sin un control de solicitud activa. No hay cancelación, cambio automático de nodo ni distinción de estados de ambos nodos. Usa stream=False, por lo que no muestra respuesta token a token.

## Historial, identidad y seguridad de presentación

ask envía prompt aislado mediante /api/generate; no incorpora memoria de Obsidian, identidad, historial conversacional o herramientas del sistema. Las rutas FRIDAY declaradas en config.py no se leen. No afirmar que Karen tiene memoria o control de PC por tener esos campos.

El campo API key no está enmascarado. En la configuración observada estaba vacío; no hubo exposición de una clave real durante el diagnóstico. El código transmite Bearer si existe, pero el contrato de autenticación debe definirse por adaptador antes de cambiar entre servicios.

## Diferencia frente al historial

Las notas antiguas describen una versión con Flask /chat, Edge-TTS y openWakeWord. Los archivos actuales describen un cliente Tkinter para Ollama directo. No hay evidencia suficiente de cuándo o por quién se sustituyó aquel flujo. Conservar ambas descripciones fechadas y decidir cuál es la base que se recuperará, sin mezclarlas como si fueran el mismo programa.''')
    add('05_Plan_Proxima_Sesion','Karen — plan para la próxima sesión',
        '''## Objetivo del usuario

Refinar Karen, conectarla al Homelab y ofrecer funcionamiento con la PC principal. Poder alternar entre ambos nodos desde una interfaz dinámica. Mantener wake word lo más refinado posible. La conversación dejó propuesto que el wake word y la captura permanezcan en la PC aunque el servidor esté desconectado.

Este plan es trabajo pendiente. La sesión de diagnóstico no aplicó correcciones ni rediseños.

## 1. Congelar una base recuperable

- [ ] Respaldar C:\\Karen y registrar hashes antes de editar.
- [ ] Preparar entorno Python 3.11 con dependencias versionadas.
- [ ] Unificar punto de entrada, directorio de arranque, CLI y perfiles VS Code.

Cierre: una única forma reproducible de iniciar, sin argumentos rechazados ni dependencia del directorio desde donde se ejecute.

## 2. Conexión de dos nodos

- [ ] Perfil PC: Ollama localhost:11434 y modelo realmente instalado.
- [ ] Perfil Homelab: decidir entre Ollama directo :11434 o adaptador Flask :5000/chat según identidad, historial y capacidades requeridas.
- [ ] Comprobar contrato, catálogo y disponibilidad del modelo; mostrar el nodo y modelo activos.
- [ ] Elegir nodo manualmente y guardar configuración de forma persistente.
- [ ] Evaluar cambio automático después; no duplicar una petición en ambos nodos si ya se está ejecutando o existe historial remoto compartido.

Cierre: una pregunta real completa por cada perfil, error claro cuando un nodo falla y cambio de nodo sin reiniciar la aplicación. No abrir servicios adicionales o modificar red para resolver un contrato incorrecto.

## 3. Audio fiable

- [ ] Corregir detector DeviceList y elegir Fifine de forma consistente con el backend de captura.
- [ ] Respetar configuración Whisper y verificar captura/STT en vivo.
- [ ] Conectar TTS y probar altavoces, interrupción y recuperación.
- [ ] Estados claros: inactivo, escuchando nombre, capturando comando, transcribiendo, generando, hablando y error.

Cierre: frase hablada → texto → nodo elegido → respuesta hablada, y retorno a espera sin bloquear la ventana.

## 4. Wake word real

- [ ] Identificar procedencia y versión del ONNX actual por hash y artefactos de entrenamiento.
- [ ] Integrar frontend de audio y features apropiado antes de inferir el modelo.
- [ ] Evaluar positivos, habla negativa, ruido, silencio real y audio de la propia Karen.
- [ ] Calibrar umbral, warm-up, confirmaciones y cooldown con métricas; no validar por una sola muestra.
- [ ] Si requiere reentrenar, usar el plan de negativos de habla del historial y separar entrenamiento de inferencia.

Cierre: precisión útil en sesiones reales, tasa de falsas activaciones y latencia registradas; sin prometer fiabilidad por el antiguo 99,43 % de validación.

## 5. Interfaz y continuidad

- [ ] Separar configuración de uso diario y conversación; mostrar nodo, micrófono y estado de forma visible.
- [ ] Canalizar eventos de trabajadores al hilo principal; limitar solicitudes activas y ofrecer cancelación.
- [ ] Definir memoria por conversación y fronteras de acciones del sistema.
- [ ] Aplicar las skills de diseño pertinentes al stack elegido, luego revisar con el usuario.
- [ ] Guardar estado, evidencia y decisiones al cierre en Obsidian.

Cierre: recorrido completo con servidor disponible y no disponible, teclado, tamaños de ventana y errores. La estética se valida con el usuario, no mediante una afirmación del asistente.''','task')
    add('06_Fuentes_y_Limites','Karen — fuentes, evidencia y límites del diagnóstico',
        '''## Registro de fuentes

| ID | Fuente | Tratamiento |
| --- | --- | --- |
| CHAT-KAREN-20261003 | Conversación visible de voz sobre dos nodos y diagnóstico | Requisitos y plan conservados en índice y próxima sesión |
| CODE-KAREN-20261003 | Archivos legibles de C:\\Karen y enumeración completa | Inspección estática y hashes; código sin cambios |
| RUNTIME-KAREN-20261003 | Python 3.11/3.14, imports, CLI, GUI, dispositivos, ONNX, ffmpeg | Informes JSON locales y notas por área |
| NETWORK-KAREN-20261003 | GET de versiones, catálogos y salud; generación sintética acotada | Respuestas comprobadas sin copiar datos privados |
| STT-KAREN-20261003 | Whisper base y muestra MP3 existente | Transcripción local; solo medidas conservadas |
| LEGACY-KAREN-202609 | MOC, arquitectura, estado, cliente streaming, error wakeword, bitácora y decisiones existentes | Antecedentes fechados; no sobrescritos ni tratados como implementación actual |

## Evidencia local

Los informes quedan en `docs/karen-audit` del workspace Local_AI_Benchmark: runtime-311.json, runtime-314.json, focused-311.json, network-311.json, inference-311.json y stt-311.json. El script audit_runtime.py registra pruebas acotadas y reproduce las comprobaciones; no sirve como lanzador de Karen.

| Archivo de código | SHA-256 observado |
| --- | --- |
| cliente.py | a4d0a35e4193df59c39720f2e7daae91ae423d1f2a18945413976bd5a8cc1b43 |
| config.py | 8134eff0d8b51af141eaf4eab396b64f8c362337a300ee4849c3581eb71e4984 |
| diagnose_devices.py | 4eda5cfe6bfcb49196b778f6367da73314497d2defb41cd24a6006c9fcc57afe |
| diagnose_mic.py | 155f7d110a77041e81d002c772e6230eff9fc748098efb9327cd024229171c30 |

## Conservación y autorización

La reorganización anterior dejó intactos los archivos Karen y Friday. Esta petición posterior autoriza guardar el diagnóstico de Karen: se añaden siete notas nuevas, sin alterar las notas previas, Friday, el código C:\\Karen ni la configuración del grafo. El índice nuevo enlaza los mapas existentes para integrarse mediante backlinks.

Se mantiene la preferencia B de organización equilibrada para sintetizar la conversación. Los informes preservan el detalle técnico y las condiciones de las pruebas. No se elimina contenido histórico ni se afirma acceso a conversaciones no visibles.

## Lo que no se hizo

- No se corrigió ni rediseñó el cliente.
- No se instaló paquete, descargó modelo o reentrenó wake word.
- No se grabó voz nueva ni se reprodujo audio.
- No se validó el pipeline completo de micrófono a respuesta hablada.
- No se probó detección con positivos/negativos reales ni se confirmó que ONNX sea v2.
- No se accedió por SSH al servidor, se inspeccionó systemd ni se verificó /chat.
- No se ejecutaron acciones de control de Windows o Proxmox, se reiniciaron servicios ni se cambió red.
- No se apagó la PC ni se creó una tarea programada.

La notificación de cierre es el mensaje final de esta conversación. No implica que el asistente continúe después de apagar el equipo. Las notas permiten retomar la próxima sesión sin depender de esa continuidad.''','evidence')
    STAGE.mkdir(parents=True,exist_ok=True)
    for rel,txt in notes.items():
        assert not (VAULT/rel).exists(),rel
        p=STAGE/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(txt,encoding='utf-8')
    spec=importlib.util.spec_from_file_location('reorg',HERE.parent/'obsidian-update/reorganize_vault.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    files=list(mod.vault_files())
    old={p.relative_to(VAULT).as_posix():p.read_text(encoding='utf-8-sig') for p in files if p.suffix=='.md'}
    merged={**old,**notes};before=mod.graph_report(old);after=mod.graph_report(merged)
    new_missing=[r for r in after['unresolved'] if (r['path'],r['target']) not in {(v['path'],v['target']) for v in before['unresolved']}]
    assert not new_missing,new_missing
    inventory='| Path | Estado |\n| --- | --- |\n'+'\n'.join('| '+r+' | verificado |' for r in sorted(merged))
    inventory+='\n'+'\n'.join('| '+Path(r).name+' | referencia por nombre |' for r in sorted(merged))
    (HERE/'known-paths.md').write_text(inventory,encoding='utf-8')
    hashes={p.relative_to(VAULT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files if mod.protected(p.relative_to(VAULT).as_posix())}
    (HERE/'existing-protected-hashes.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2),encoding='utf-8')
    manifest=[{'path':r,'sha256':hashlib.sha256((STAGE/r).read_bytes()).hexdigest()} for r in notes]
    (HERE/'obsidian-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    (HERE/'graph-preview.json').write_text(json.dumps(after,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'notes_to_create':len(notes),'existing_protected_files':len(hashes),'graph':after['stats'],'new_broken_links':len(new_missing)}))

def apply():
    manifest=json.loads((HERE/'obsidian-manifest.json').read_text(encoding='utf-8'))
    hashes=json.loads((HERE/'existing-protected-hashes.json').read_text(encoding='utf-8'))
    for rel,h in hashes.items():assert hashlib.sha256((VAULT/rel).read_bytes()).hexdigest()==h,'Existing note changed: '+rel
    for entry in manifest:
        p=(VAULT/entry['path']).resolve()
        assert p.is_relative_to((VAULT/'Karen Asistant/07_Diagnostico').resolve()) and not p.exists()
        assert hashlib.sha256((STAGE/entry['path']).read_bytes()).hexdigest()==entry['sha256']
    for entry in manifest:
        p=VAULT/entry['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((STAGE/entry['path']).read_bytes())
        assert hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256']
    for rel,h in hashes.items():assert hashlib.sha256((VAULT/rel).read_bytes()).hexdigest()==h,'Existing note changed: '+rel
    runtime=json.loads((HERE/'runtime-311.json').read_text(encoding='utf-8'))
    for name,data in runtime['checks']['syntax']['data'].items():assert hashlib.sha256((Path(r'C:\Karen')/name).read_bytes()).hexdigest()==data['sha256'],'Code changed: '+name
    receipt={'created_notes':len(manifest),'existing_protected_files_unchanged':len(hashes),'code_files_hash_verified':4,'all_write_hashes_verified':True}
    (HERE/'obsidian-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt))

if __name__=='__main__':prepare() if sys.argv[1]=='prepare' else apply()
