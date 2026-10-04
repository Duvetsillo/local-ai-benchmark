from pathlib import Path
import argparse, hashlib, json, re, unicodedata, zipfile, os
from collections import defaultdict, deque

VAULT = Path(r'C:\Obsidian\Data Base')
OUT = Path(__file__).parent / 'reorganization-20261003'
STAGE = OUT / 'staging'
DATE = '2026-10-03'
changes = {}
orig = {}
sources = {}

def vault_files():
    # Ignore linked tool directories and never traverse a junction outside the vault.
    for root, dirs, files in os.walk(VAULT, followlinks=False):
        dirs[:] = [d for d in dirs if not (Path(root)/d).is_symlink() and d not in ('.agents','.git','node_modules')]
        for name in files:
            p=Path(root)/name
            if p.is_file() and not p.is_symlink():
                yield p

def sha(data):
    return hashlib.sha256(data).hexdigest()

def protected(rel):
    s = rel.casefold()
    return 'karen' in s or 'friday' in s

def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')

def read(rel):
    if rel not in orig:
        p = VAULT / rel
        orig[rel] = p.read_bytes() if p.exists() else None
    return (orig[rel] or b'').decode('utf-8-sig').replace('\r\n', '\n')

def put(rel, txt):
    assert not protected(rel), rel
    assert rel == '00_MOC_Obsidian.md' or rel.startswith(('00_Navegacion/', 'Proyecto Aetherion/', 'Proyecto Ultron/')), rel
    read(rel)
    changes[rel] = txt.rstrip() + '\n'

def link(path, label=None):
    path = path.removesuffix('.md')
    return '[[' + path + ('|' + label if label else '') + ']]'

def note(rel, title, parent, body, kind='concept', status='current', refs=None, project='Aetherion', domain=None):
    domain = domain or rel.split('/')[1]
    header = '\n'.join([
        '---', 'knowledge_id: vault-20261003-' + slug(rel.removesuffix('.md')),
        'title: ' + json.dumps(title, ensure_ascii=False), 'project: ' + project,
        'domain: ' + domain, 'note_type: ' + kind, 'version: 1.0.0', 'status: ' + status,
        'created: ' + DATE, 'updated: ' + DATE,
        'up: ' + json.dumps([link(parent)] if parent else [], ensure_ascii=False),
        'related: []', 'replaces: []',
        'source_refs: ' + json.dumps([link(x) for x in (refs or [])], ensure_ascii=False),
        'tags: ' + json.dumps([slug(project), 'area/' + slug(domain), 'mapa' if kind == 'project' else kind]), '---', '',
        '# ' + title, '',
    ])
    put(rel, header + body)

def sections(txt, level=2):
    chunks = {}
    current = None
    fenced = False
    for line in txt.splitlines():
        if line.lstrip().startswith('```'):
            fenced = not fenced
        match = re.match(r'^' + '#' * level + r' (.+)$', line) if not fenced else None
        if match:
            current = match.group(1)
            chunks[current] = []
        elif current:
            chunks[current].append(line)
    return {k: '\n'.join(v).strip() for k, v in chunks.items()}

def extract(rel, title, parent, source, keys, intro, lateral=None, level=2, status='current', kind='process'):
    chunks = sections(read(source), level)
    for key in keys:
        assert key in chunks, (source, key, list(chunks))
    body = intro + '\n\n' + '\n\n'.join('## ' + key + '\n\n' + chunks[key] for key in keys)
    body += '\n\n## Procedencia y contexto\n\nEl contenido procede de ' + link(source) + '. Conserva las condiciones de ese registro; no acredita una ejecución nueva durante la organización del vault.'
    if lateral:
        body += '\n\n' + lateral
    note(rel, title, parent, body, kind, status, [source])
    sources.setdefault(source, []).append(rel)

def append_nav(rel, parent, extra=None, notice=None):
    txt = changes.get(rel, read(rel))
    nav = '\n\n## Navegación documental\n\nVolver a ' + link(parent) + '.'
    if extra:
        nav += '\n\n' + extra
    if notice:
        # Insert after YAML, including one legacy note whose YAML follows a callout.
        m = re.search(r'(?m)^---\n.*?\n---\n', txt, re.S)
        if m and m.start() > 0:
            lead = txt[:m.start()]
            txt = txt[m.start():m.end()] + '\n' + lead + txt[m.end():]
            m = re.match(r'^---\n.*?\n---\n', txt, re.S)
        pos = m.end() if m and m.start() == 0 else 0
        txt = txt[:pos] + '\n> [!info] Lectura al 3 de octubre de 2026\n> ' + notice + '\n\n' + txt[pos:]
    put(rel, txt.rstrip() + nav)

A = 'Proyecto Aetherion/'
U = 'Proyecto Ultron/'
ROOT = '00_MOC_Obsidian.md'
AH = A + '00_Gobierno/00_MOC_Aetherion.md'
UH = U + '00_Mapa_Ultron.md'
branches = {
    '00_Gobierno': ('Gobierno y estado', 'Propósito, alcance, estado verificable y referencias del producto.'),
    '01_Arquitectura': ('Arquitectura y evaluación', 'Motor, proveedores, hardware, validadores y contratos de resultados.'),
    '02_Cliente': ('Cliente y experiencia', 'Pantallas, interacción, Studio 03 y evolución del sistema visual.'),
    '03_Datos_y_Operaciones': ('Datos y operaciones', 'Privacidad, instalación, compilación y distribución Windows.'),
    '04_Calidad': ('Calidad y evidencia', 'Pruebas, diagnóstico, incidentes y límites de aceptación.'),
    '05_Roadmap': ('Decisiones y próximos pasos', 'Decisiones implementadas y trabajo pendiente con criterios de cierre.'),
    '06_Historial': ('Historial y fuentes', 'Sesiones fechadas y procedencia: evidencia histórica, no instrucciones actuales por defecto.'),
    '07_Licencias_y_Cuentas': ('Licencias y cuentas', 'Autoridad de firma, alta, renovación, servicio propio y continuidad offline.'),
    '08_Herramientas_Diseno': ('Herramientas de diseño', 'Skills instaladas, uso documentado y alcance de las herramientas.'),
}
hub = {folder: A + folder + '/00_Mapa_' + folder.split('_', 1)[1] + '.md' for folder in branches}

def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    all_files = list(vault_files())
    protected_before = {p.relative_to(VAULT).as_posix(): sha(p.read_bytes()) for p in all_files if protected(p.relative_to(VAULT).as_posix())}
    (OUT / 'protected-before.json').write_text(json.dumps(protected_before, ensure_ascii=False, indent=2), encoding='utf-8')
    existing = [p.relative_to(VAULT).as_posix() for p in all_files if p.suffix == '.md' and not protected(p.relative_to(VAULT).as_posix()) and p.relative_to(VAULT).parts[0] in ('Proyecto Aetherion', 'Proyecto Ultron')]
    # Integrate the previously delivered, validated bounded batches. Root guides stay outside the active vault.
    for directory in ('staging', 'part01-staging', 'part02-staging'):
        for p in (Path(__file__).parent / directory / 'Proyecto Aetherion').rglob('*.md'):
            rel = p.relative_to(Path(__file__).parent / directory).as_posix()
            assert not (VAULT / rel).exists(), 'Import collision: ' + rel
            txt = p.read_text(encoding='utf-8').replace('up: ["[[00-Home/Project Home]]"]', 'up: ' + json.dumps([link(hub[rel.split('/')[1]])], ensure_ascii=False))
            txt = txt.replace('[[00-Home/Project Home]]', link(AH)).replace('[[00-Home/Source Register]]', link('00_Navegacion/Registro_de_Organizacion.md')).replace('[[00-Home/Forge Progress]]', link('00_Navegacion/Registro_de_Organizacion.md'))
            put(rel, txt)
    # Keep exact original prose for the pages whose main reading entry is replaced.
    snapshot = A + '06_Historial/Archivo_Documental/'
    replaced = ['00_Gobierno/00_MOC_Aetherion.md', '00_Gobierno/01_Resumen_Ejecutivo.md', '00_Gobierno/02_Estado_Actual.md', '05_Roadmap/01_Roadmap.md']
    for path in replaced:
        original = A + path
        dest = snapshot + Path(path).stem + '_Corte_Anterior.md'
        note(dest, 'Corte anterior — ' + Path(path).stem, hub['06_Historial'],
             '> [!abstract] Registro histórico preservado\n> Copia del contenido encontrado antes de esta reorganización. Puede contener estados ya corregidos; para operar consulta ' + link(A + '00_Gobierno/02_Estado_Actual.md') + '.\n\n' + read(original),
             'evidence', 'archived', [original])
    note(ROOT, 'Mapa general del conocimiento', '',
         'Este es el punto de entrada del vault. Cada proyecto mantiene sus fuentes y su ciclo de trabajo; los enlaces expresan una relación documental y no una integración técnica automática.\n\n'
         '## Proyectos\n\n'
         '- ' + link(AH, 'Aetherion — producto y benchmarking local') + ': entra por nueve áreas de conocimiento.\n'
         '- ' + link(UH, 'Ultron — identidad, memoria y ejecución') + ': entra por integración, inteligencia, infraestructura y control.\n'
         '- [[Proyecto FRIDAY/FRIDAY_Blueprint|Friday — documentación original]]: carpeta preservada íntegramente.\n'
         '- [[Karen Asistant/00_MOC_Vault 1|Karen — documentación original]]: carpeta preservada íntegramente.\n\n'
         '## Recorridos\n\n'
         '- ' + link('00_Navegacion/Rutas_de_Lectura.md', 'Rutas de lectura') + ': secuencias según la tarea.\n'
         '- ' + link('00_Navegacion/Guia_del_Grafo.md', 'Guía del grafo') + ': grupos, filtro y profundidad.\n'
         '- ' + link('00_Navegacion/Documentos_Preservados.md', 'Documentos de asistentes preservados') + ': enlaces externos a sus notas originales, sin modificarlas.\n'
         '- ' + link('00_Navegacion/Registro_de_Organizacion.md', 'Registro de organización') + ': fuentes, protección y alcance.', 'project', project='Ecosistema', domain='navegacion')
    current = A + '00_Gobierno/02_Estado_Actual.md'
    note(current, 'Aetherion — estado al 3 de octubre de 2026', hub['00_Gobierno'],
         '## Estado de producto\n\nLa última revisión documentada del cliente es **Studio 03**, entregada como `Aetherion-Studio-03.exe`. Cambia la estructura: navegación superior, inicio separado del laboratorio, biblioteca de modelos y resultados con gráfica y tabla. La autenticación existente y el motor de benchmarks se mantienen. La aceptación estética del usuario sigue pendiente.\n\n'
         '## Hechos comprobados en la sesión anterior\n\n- 18 pruebas automatizadas aprobadas.\n- Comprobaciones de widgets en 1020 × 720, 1200 × 820 y 1600 × 1000.\n- Separación de Workspace y Benchmark, búsqueda y selección de modelos, ordenación de resultados y controles deshabilitados durante operaciones.\n- 12 combinaciones de texto y superficie superaron 4,5:1; mínimo 5,71:1.\n- Compilación completada; inspección del archivo confirmó STUDIO 03, el módulo Studio y Tcl. Se inició el proceso del EXE.\n\n'
         'La evidencia detallada y sus límites están en ' + link(A + '04_Calidad/07_Verificacion_Studio_2026-10-03.md') + '. Esta reorganización documental no volvió a ejecutar las pruebas del cliente.\n\n'
         '## Incidente histórico\n\nEl fallo del 30 de septiembre por ausencia de `cryptography` está registrado como resuelto en una build posterior de ese día. No mantenerlo como bloqueo actual solo porque las primeras notas lo describen abierto. El cierre no valida todos los equipos ni todo el servicio: ' + link(A + '04_Calidad/02_Incidente_Arranque_Cliente.md') + '.\n\n'
         '## Pendientes reales\n\n- Confirmar satisfacción visual con Studio 03 y revisar capturas.\n- Ensayar todas las escalas DPI relevantes y accesibilidad con lector de pantalla.\n- Desplegar y validar el servicio de cuentas contra VPS/dominio; no hay una nueva evidencia de despliegue en esta sesión.\n- Completar autenticación online, renovación, suspensión y benchmark real de punta a punta.\n\n'
         '## Continuidad\n\n' + link(A + '05_Roadmap/01_Roadmap.md') + ' ordena los siguientes pasos. El texto anterior completo se conserva en ' + link(snapshot + '02_Estado_Actual_Corte_Anterior.md') + '.', 'reference', refs=[A + '02_Cliente/06_Studio_Estructura_2026-10-03.md', A + '04_Calidad/07_Verificacion_Studio_2026-10-03.md'])
    note(A + '00_Gobierno/01_Resumen_Ejecutivo.md', 'Aetherion — propósito y propuesta', hub['00_Gobierno'],
         'Aetherion es el producto de Local AI Benchmark: un cliente Windows y herramientas locales para perfilar el equipo, descubrir modelos y comparar tareas bajo un contexto registrado. El repositorio también contiene CLI, dashboard local y sitio público; son superficies distintas.\n\n'
         '## Qué aporta\n\nDescubrimiento Ollama y GGUF, ejecución mediante Ollama o llama.cpp, perfil de CPU/RAM/GPU disponible, suite de tareas y validadores simples, telemetría expuesta por el runtime y persistencia JSON local. El acceso de cuentas y licencias se documenta separadamente en ' + link(hub['07_Licencias_y_Cuentas']) + '.\n\n'
         '## Cliente actual documentado\n\nStudio 03 organiza inicio, modelos, laboratorio y resultados en destinos diferenciados. Las herramientas instaladas posteriormente no implican otro rediseño ya aplicado. Consulta ' + link(current) + ' para saber qué se comprobó y qué falta.\n\n'
         '## Interpretación responsable\n\nUna orientación de compatibilidad no garantiza carga; un validador aprobado no prueba calidad global. Las métricas requieren hardware, runtime, modelo, parámetros y suite comparables. Un endpoint remoto cambia el destino de los prompts. No se promete un ranking universal.\n\n'
         'El registro ejecutivo anterior completo está en ' + link(snapshot + '01_Resumen_Ejecutivo_Corte_Anterior.md') + '.', 'reference', refs=[A + '01_Arquitectura/05_Suite_de_Benchmarks.md', current])
    note(A + '05_Roadmap/01_Roadmap.md', 'Aetherion — próximos pasos verificables', hub['05_Roadmap'],
         '## Base ya documentada\n\nEl incidente histórico de `cryptography` tiene cierre registrado. Studio 03 tiene build y 18 pruebas aprobadas, más comprobaciones de interfaz acotadas. Esas evidencias no equivalen a aceptación visual ni validación comercial.\n\n'
         '## 1. Aceptación del cliente\n\n- [ ] Revisar visualmente Studio 03 con el usuario y capturas.\n- [ ] Comprobar escalas DPI y lector de pantalla.\n- [ ] Ejecutar un benchmark real, detenerlo y verificar el JSON y registros anteriores.\n\nCierre: evidencia del artefacto, entorno y recorrido completo; ver ' + link(hub['04_Calidad']) + '.\n\n'
         '## 2. Servicio de cuentas\n\n- [ ] Definir VPS/dominio y desplegar HTTPS.\n- [ ] Probar alta por clave, login/logout, renovación sin nueva clave y suspensión.\n- [ ] Probar recuperación, persistencia y pase offline limitado en equipos controlados.\n\nCierre: pruebas con cuenta de ensayo y sin secretos en las notas; ver ' + link(hub['07_Licencias_y_Cuentas']) + '.\n\n'
         '## 3. Repetibilidad y evaluación\n\n- [ ] Unificar metadatos de runtime y versión.\n- [ ] Mantener lectores para los formatos del motor y cliente.\n- [ ] Diseñar validadores más exigentes y casos adversariales.\n- [ ] Evaluar repeticiones estadísticas y exportación revisada.\n\n## 4. Operación e historial\n\n- [ ] Definir retención de resultados y recuperación.\n- [ ] Registrar hash, versión y evidencia en cada release.\n- [ ] Actualizar estado y fuentes sin borrar los registros históricos.\n\nEl roadmap previo queda íntegro en ' + link(snapshot + '01_Roadmap_Corte_Anterior.md') + '. Estas listas son trabajo pendiente, no funcionalidades nuevas.', 'task', refs=[current])

    # Detailed licensing nodes preserve the original clauses rather than reducing them to titles.
    account_src = A + '06_Historial/09_Cuentas_Servicio_Renovacion_2026-09-30.md'
    owner_src = A + '06_Historial/08_Generador_Licencias_y_Detener_Benchmark_2026-09-30.md'
    L = A + '07_Licencias_y_Cuentas/'
    extract(L + '01_Contrato_Cuenta_y_Dispositivo.md', 'Cuenta, licencia y dispositivo', hub['07_Licencias_y_Cuentas'], account_src,
            ['Requisitos acordados', 'Componentes', 'Decisiones registradas'], 'Esta nota reúne el contrato funcional registrado para el servicio central. El servicio no recopila los resultados del benchmark.')
    for file, title, key, intro in [
        ('02_Preparar_Servicio.md', 'Preparación del servicio propio', '1. Preparar el servicio del propietario', 'Procedimiento documentado, pendiente de evidencia de despliegue real.'),
        ('03_Emitir_y_Sincronizar.md', 'Emisión y sincronización de licencias', '2. Emitir una licencia nueva', 'La emisión del esquema central exige sincronización del servidor antes de entregar la clave.'),
        ('04_Alta_y_Acceso.md', 'Alta y acceso de cuenta', '3. Reclamar e iniciar sesión', 'El primer alta reclama la licencia; los accesos siguientes usan la cuenta ligada a ese dispositivo.'),
        ('05_Renovacion_y_Suspension.md', 'Renovación y suspensión', '4. Renovar y administrar', 'La renovación cambia la fecha central sin emitir otra clave. La suspensión y el offline tienen ventanas de aplicación distintas.'),
        ('06_Pase_Offline.md', 'Pase offline y límites temporales', 'Modelo y límites offline', 'El pase firmado ofrece continuidad limitada; no garantiza revocación instantánea de un dispositivo desconectado.'),
    ]:
        extract(L + file, title, hub['07_Licencias_y_Cuentas'], account_src, [key], intro, level=3)
    extract(L + '07_Datos_y_Seguridad.md', 'Datos de cuenta y controles documentados', hub['07_Licencias_y_Cuentas'], account_src,
            ['Datos y seguridad'], 'Distingue contraseña, token administrativo, sesión, pase offline y resultados locales. Los controles registrados no sustituyen una auditoría de seguridad.')
    extract(L + '08_Despliegue_y_Aceptacion.md', 'Despliegue y aceptación del servicio', hub['07_Licencias_y_Cuentas'], account_src,
            ['Despliegue reproducible', 'Verificación y estado de entrega'], 'Runbook del servicio y pendientes históricos. La build del cliente sí tiene corrección posterior; el despliegue y recorrido completo permanecen sin evidencia nueva.',
            'Consulta ' + link(current) + ' para el corte vigente y ' + link(A + '04_Calidad/02_Incidente_Arranque_Cliente.md') + ' para el cierre del fallo empaquetado.')
    extract(L + '09_Autoridad_y_Planes.md', 'Autoridad de firma y planes', hub['07_Licencias_y_Cuentas'], owner_src,
            ['Administrador de licencias', 'Formato y validación'], 'La autoridad privada pertenece al propietario. Esta nota conserva el esquema de firma y planes del administrador; el flujo central posterior se desarrolla en ' + link(L + '03_Emitir_y_Sincronizar.md') + '.')
    extract(L + '10_Entrega_de_Clave.md', 'Entrega de la clave al titular', hub['07_Licencias_y_Cuentas'], owner_src,
            ['Ruta operativa de emisión'], 'Secuencia del hito de administrador offline. Al operar con servicio central, añadir la sincronización y reclamación descritas en ' + link(L + '03_Emitir_y_Sincronizar.md') + ' y ' + link(L + '04_Alta_y_Acceso.md') + '.', status='archived')
    extract(A + '01_Arquitectura/08_Cancelacion_Cooperativa.md', 'Cancelación cooperativa del benchmark', hub['01_Arquitectura'], owner_src,
            ['Botón Stop benchmark'], 'La acción Stop conserva las tareas terminadas y descarta la respuesta incompleta. La cancelación depende de que el proveedor avance o libere la lectura; no es instantánea.')
    # Split the client into actual, meaningful working destinations.
    C = A + '02_Cliente/Studio/'
    studio_src = A + '02_Cliente/06_Studio_Estructura_2026-10-03.md'
    studio_text = changes[studio_src]
    def studio_note(filename, title, body):
        note(C + filename, title, hub['02_Cliente'], body + '\n\nEl cambio y su motivo están en ' + link(studio_src) + '; las comprobaciones y límites en ' + link(A + '04_Calidad/07_Verificacion_Studio_2026-10-03.md') + '.', refs=[studio_src])
    studio_note('01_Navegacion.md', 'Studio — navegación y destinos',
        'Studio sustituye el rail lateral por navegación superior. Los destinos principales son **Workspace, Models, Benchmark y Results**. Hardware, History y Settings permanecen como utilidades visibles; SIGN OUT corresponde a la sesión autenticada.\n\nCada destino tiene una tarea: iniciar, elegir modelo, ejecutar o revisar. No se introdujo otro framework; la GUI sigue en Tkinter. La autenticación y el motor existentes se conservan.\n\nLa separación responde a la crítica de que Atelier solo cambió colores. La aceptación estética todavía no está confirmada.')
    studio_note('02_Workspace.md', 'Studio — inicio del trabajo',
        'Workspace concentra introducción, modelo sugerido por compatibilidad estimada, resumen del equipo, experimentos recientes y próximos pasos. La consola de ejecución y el formulario completo están en el laboratorio.\n\nLa tarjeta sugerida prepara el modelo en Benchmark; no ejecuta una medición automáticamente. Sin modelos se ofrece una ruta para obtenerlos. La recomendación expresa ajuste estimado a hardware, no una victoria medida.\n\nContinuar en ' + link(C + '03_Biblioteca.md') + ' o ' + link(C + '04_Laboratorio.md') + '.')
    studio_note('03_Biblioteca.md', 'Studio — biblioteca y búsqueda',
        'Models muestra tarjetas con nombre, proveedor, tamaño, precisión disponible y compatibilidad estimada. La búsqueda filtra nombre o proveedor; limpiar el filtro restaura la colección. El estado sin coincidencias se distingue de la ausencia de modelos.\n\nElegir una tarjeta prepara ese modelo en ' + link(C + '04_Laboratorio.md') + '. Durante operaciones se deshabilitan selección y actualización para evitar cambios incompatibles. Ver un modelo en el catálogo no demuestra que cargue ni que use GPU.\n\nEl contrato de runtimes se desarrolla en ' + link(A + '01_Arquitectura/04_Proveedores_Locales.md') + '.')
    studio_note('04_Laboratorio.md', 'Studio — laboratorio de benchmark',
        'Benchmark reúne modelo, suite y parámetros, acción de inicio, parada, progreso y registro técnico. El dock conserva la acción principal mientras la configuración se desplaza. La consola aparece aquí, separada del inicio.\n\nUna operación activa bloquea controles que puedan cambiar su configuración; se restauran al terminar. La cancelación se detalla en ' + link(A + '01_Arquitectura/08_Cancelacion_Cooperativa.md') + '. Los estados y validadores siguen correspondiendo al motor existente.\n\nTras la ejecución revisar ' + link(C + '05_Resultados.md') + '. Un PASS representa la regla de esa tarea, no calidad universal.')
    studio_note('05_Resultados.md', 'Studio — gráfica y registros',
        'Results presenta hasta cuatro modelos en barras descendentes de velocidad, usando el último dato disponible por modelo. No inventa actividad ni velocidades. La advertencia de que las suites pueden diferir limita la interpretación: la gráfica no constituye por sí sola una comparación controlada.\n\nLa tabla nativa Treeview permite ordenar por fecha, velocidad, checks aprobados o nombre. Enter, doble clic y la acción de apertura consultan el JSON local. Los registros guardados constituyen la evidencia; la gráfica es una lectura rápida.\n\nEl esquema está en ' + link(A + '01_Arquitectura/07_Formato_de_Resultados.md') + ' y las condiciones de comparación en ' + link(A + '01_Arquitectura/05_Suite_de_Benchmarks.md') + '.')
    # Extract reusable architectural details from their complete parent notes.
    extract(A + '01_Arquitectura/Proveedores/01_Ollama.md', 'Proveedor Ollama', hub['01_Arquitectura'], A + '01_Arquitectura/04_Proveedores_Locales.md',
            ['Interfaz común', 'Ollama', 'Privacidad'], 'Ollama es un runtime externo al proceso Python, configurado localmente por defecto. Confirmar servicio y modelo antes de atribuir un fallo a la GUI.')
    extract(A + '01_Arquitectura/Proveedores/02_LlamaCpp_GGUF.md', 'Proveedor llama.cpp y GGUF', hub['01_Arquitectura'], A + '01_Arquitectura/04_Proveedores_Locales.md',
            ['llama.cpp y GGUF', 'Fallos comunes', 'Privacidad'], 'La carpeta contiene archivos de modelo; el backend y sus dependencias determinan si pueden ejecutarse. La presencia de un archivo no acredita carga ni aceleración.')
    extract(A + '01_Arquitectura/Resultados/01_JSON_del_Motor.md', 'JSON del motor de evaluación', hub['01_Arquitectura'], A + '01_Arquitectura/07_Formato_de_Resultados.md',
            ['Resultado del motor', 'Ejemplo conceptual', 'Compatibilidad y manejo'], 'Distingue el formato de salida del motor del registro usado por el cliente. El ejemplo conservado es conceptual, no una corrida real.')
    extract(A + '03_Datos_y_Operaciones/04_Persistencia_Atomica.md', 'Persistencia atómica y lectura del historial', hub['03_Datos_y_Operaciones'], A + '01_Arquitectura/07_Formato_de_Resultados.md',
            ['Persistencia del cliente', 'Compatibilidad y manejo'], 'Escritura atómica evita exponer un JSON parcialmente escrito. Ignorar un archivo ilegible al listar no significa que se haya reparado; conservarlo para diagnóstico.')
    extract(A + '04_Calidad/08_Cierre_Cryptography.md', 'Cierre del fallo de cryptography en el EXE', hub['04_Calidad'], A + '04_Calidad/02_Incidente_Arranque_Cliente.md',
            ['Causa raíz y resolución — 2026-09-30'], 'Evidencia histórica de cierre. La corrección pertenece al entorno de build y a esa compilación; no demuestra autenticación online ni compatibilidad universal.', kind='evidence')
    extract(A + '04_Calidad/09_Diagnostico_por_Runtime.md', 'Diagnóstico de runtimes y resultados', hub['04_Calidad'], A + '04_Calidad/03_Guia_de_Diagnostico.md',
            ['Ollama no descubierto', 'GGUF visible pero no carga', 'Sin métricas GPU', 'JSON ausente', 'Reporte de error'], 'Recorrido de diagnóstico por síntoma. Registrar el mensaje exacto, productor del archivo y entorno antes de cambiar configuración.')
    T = A + '08_Herramientas_Diseno/'
    note(T + '01_Skills_Instaladas.md', 'Skills de diseño instaladas para Codex', hub['08_Herramientas_Diseno'],
         '## Instalación solicitada y completada\n\nEl usuario solicitó los paquetes de Emil Kowalski, Impeccable y Leonxlnx/taste-skill. Se instalaron globalmente para Codex y se verificaron los archivos y su detección.\n\n'
         '| Paquete | Resultado registrado |\n| --- | --- |\n| Emil Kowalski | 14 skills de diseño, UI y animación |\n| Impeccable | Skill, scripts y motor Windows instalados |\n| Taste | 13 skills de diseño visual y frontend |\n\n'
         '## Uso y alcance\n\nLa instalación posterior no significa que esas guías se hayan aplicado ya a Studio 03. Varias están orientadas a web, CSS o React; antes de usarlas en Tkinter hay que adaptar lo pertinente al stack real. No forzar una migración de framework por una recomendación de skill.\n\n'
         'Impeccable quedó instalado sin hooks de ciclo de vida. Su inicialización de contexto no se ejecutó en esta sesión. Caveman y UI/UX Pro Max tienen estados distintos, desarrollados en ' + link(T + '02_Caveman_y_UIUX.md') + '.', 'reference')
    note(T + '02_Caveman_y_UIUX.md', 'Caveman y UI/UX Pro Max — alcance real', hub['08_Herramientas_Diseno'],
         'Caveman tiene una skill de estilo conciso instalada. El CLI 2.0.0 y seis binarios se instalaron y verificaron; el proxy no fue iniciado ni conectado a Codex. No se atribuye reducción real de tokens a esa instalación.\n\n'
         'UI/UX Pro Max se usó mediante el comando solicitado y su paquete temporal de apoyo. La salida se leyó completa. No quedó instalada como skill persistente. La dirección de dashboard de datos y comparación con barras se adaptó a Tkinter; se descartó el patrón comercial que no correspondía al producto.\n\n'
         'El registro detallado, incluido el rechazo inicial resuelto del setup de Caveman, está en ' + link(A + '06_Historial/08_Skills_y_Studio_2026-10-03.md') + '.', 'reference', refs=[A + '06_Historial/08_Skills_y_Studio_2026-10-03.md'])
    # Ultron: retain every original source and give the roadmap explicit thematic parents.
    ur = U + 'Roadmap/'
    ui = U + '01_Identidad/00_Mapa_Identidad.md'
    uo = U + '02_Integracion/00_Mapa_Integracion.md'
    for filename, title, keys, intro in [
        ('01_Carga_y_Recuperacion.md', 'Ultron — carga y recuperación', ['🛠️ Archivos Núcleo y Protocolo de Carga'], 'Especificación documental de recuperación, no una instrucción ejecutada durante esta reorganización. Los nombres de archivos citados no prueban su presencia actual.'),
        ('02_Comunicacion.md', 'Ultron — personalidad y comunicación', ['🎭 Definición de Personalidad', '📜 Directivas Operativas (USER.md)'], 'Conserva los criterios de identidad del blueprint como documentación del proyecto.'),
        ('03_Ejecucion_y_Limites.md', 'Ultron — ejecución y límites', ['⚙️ Protocolos de Ejecución y Superación de Bloqueos', '⚠️ Líneas Rojas y Seguridad'], 'Las capacidades descritas son la especificación de Ultron. No convierten esta organización documental en acceso operativo a servidores o aplicaciones.'),
    ]:
        chunks = sections(read(U + 'Ultron_Blueprint.md'))
        body = intro + '\n\n' + '\n\n'.join('## ' + k + '\n\n' + chunks[k] for k in keys)
        note(U + '01_Identidad/' + filename, title, ui, body, 'reference', refs=[U + 'Ultron_Blueprint.md'], project='Ultron')
    note(U + '02_Integracion/01_Obsidian_y_Memoria.md', 'Ultron — integración con Obsidian', uo,
         '## Estado documentado\n\nEl README del 6 de septiembre registra acceso directo a archivos, sincronización de memoria en proceso y API REST pendiente. En esta sesión se comprobó la ubicación del vault activo; eso no acredita que Ultron tenga una API instalada ni sincronización automática operativa.\n\n'
         '## Objetivos del registro\n\nLectura y escritura de notas, búsqueda y resumen, clasificación por etiquetas, índices automáticos y una futura integración REST. Las casillas originales permanecen sin cerrar: no convertir una tarea de prueba en implementación.\n\n'
         '## Memoria histórica\n\n' + link(U + 'Memory_Backups/Backup_2026-09-12.md') + ' es una captura fechada. Sus estados de modelos, infraestructura y asistentes no son una comprobación actual de servicios.\n\n'
         '## Relación entre proyectos\n\nLa integración documental de Aetherion está en ' + link(A + '00_Gobierno/04_Vinculacion_Core.md') + '. Compartir el vault no establece por sí solo control de voz, RAG o contratos API.', 'reference', refs=[U + 'README.md'], project='Ultron')
    # The missing Karen-voice roadmap is resolved by pointing at existing protected sources, without creating or editing Karen files.
    master = ur + 'Roadmap_Maestro.md'
    txt = read(master).replace('[[Roadmap_Karen_Voz]]', '[[Karen Asistant/02_Roadmap/KAREN_Roadmap|Roadmap de Karen]]')
    put(master, txt)
    for path, parent in [(U+'README.md', uo), (U+'Ultron_Blueprint.md', ui), (U+'Memory_Backups/Backup_2026-09-12.md', uo), (master, UH), (ur+'Roadmap_Infraestructura.md', UH), (ur+'Roadmap_Inteligencia.md', UH), (ur+'Roadmap_Ultron_Ejecucion.md', UH)]:
        append_nav(path, parent, notice='Documento histórico: sus tareas y estados se conservan sin declarar servicios verificados hoy.' if 'Backup_' in path else None)
    note(ui, 'Ultron — identidad y recuperación', UH,
         'El blueprint original sigue conservado. Estas notas separan los procedimientos de restauración, comunicación y ejecución para navegar sin recorrer toda la especificación.\n\n'
         '- ' + link(U+'01_Identidad/01_Carga_y_Recuperacion.md') + '\n- ' + link(U+'01_Identidad/02_Comunicacion.md') + '\n- ' + link(U+'01_Identidad/03_Ejecucion_y_Limites.md') + '\n- ' + link(U+'Ultron_Blueprint.md', 'Blueprint completo') + '.', 'project', project='Ultron')
    note(uo, 'Ultron — integración y memoria', UH,
         'Distingue objetivos de integración, acceso comprobado a archivos y memoria histórica. La API local y la sincronización tienen que acreditarse por separado.\n\n'
         '- ' + link(U+'02_Integracion/01_Obsidian_y_Memoria.md') + '\n- ' + link(U+'README.md', 'Registro original de integración') + '\n- ' + link(U+'Memory_Backups/Backup_2026-09-12.md', 'Memoria histórica del 12 de septiembre') + '.', 'project', project='Ultron')
    note(UH, 'Ultron — mapa del proyecto', ROOT,
         'Ultron agrupa especificación de identidad, integración de conocimiento y planes de ejecución. Las tareas del roadmap se mantienen como propuestas; no se marcan completadas por haber organizado sus notas.\n\n'
         '## Áreas\n\n- ' + link(ui) + '\n- ' + link(uo) + '\n- ' + link(ur+'Roadmap_Infraestructura.md', 'Infraestructura y transporte') + '\n- ' + link(ur+'Roadmap_Inteligencia.md', 'Inteligencia, memoria y RAG') + '\n- ' + link(ur+'Roadmap_Ultron_Ejecucion.md', 'Ejecución y automatización') + '\n- ' + link(master, 'Roadmap maestro original') + '\n\n'
         '## Contexto\n\n' + link(A+'00_Gobierno/04_Vinculacion_Core.md') + ' explica la relación conceptual con Aetherion. Karen y Friday permanecen en sus carpetas originales.', 'project', project='Ultron')
    # Add parent links to every retained Aetherion source. Older status language is explicitly historical.
    notices = {
        '02_Cliente/01_Experiencia_y_Pantallas.md': 'Esta composición corresponde al corte anterior. La revisión estructural posterior es ' + link(studio_src) + '.',
        '02_Cliente/02_Sistema_Visual.md': 'La paleta pizarra y menta describe una revisión histórica; Studio 03 y Atelier se documentan en sus notas fechadas. Consultar ' + link(studio_src) + '.',
        '02_Cliente/03_Guia_de_Uso.md': 'Las advertencias de arranque pertenecen al corte histórico. El estado vigente está en ' + link(current) + '.',
        '03_Datos_y_Operaciones/02_Instalacion_y_Uso_Local.md': 'El texto anterior conserva una advertencia de arranque ya cerrada para una build. La entrega Studio 03 y sus límites se registran en ' + link(current) + '.',
        '04_Calidad/04_Riesgos_y_Controles.md': 'El fallo histórico de cryptography tiene cierre registrado. Los riesgos de DPI, autenticación online y benchmark real siguen pendientes; ver ' + link(current) + '.',
        '04_Calidad/02_Incidente_Arranque_Cliente.md': 'Leer primero la sección «Causa raíz y resolución». Las hipótesis previas se conservan como historia del diagnóstico, no como estado actual.',
        '06_Historial/02_Fuentes_y_Certeza.md': 'Las observaciones de error sin diagnóstico corresponden al inicio del registro. El cierre posterior está documentado en ' + link(A+'04_Calidad/08_Cierre_Cryptography.md') + '.',
    }
    for rel in existing:
        if not rel.startswith(A) or rel in [A+x for x in replaced]:
            continue
        branch = rel.split('/')[1]
        extra = None
        if rel in sources:
            extra = 'Desglose temático: ' + ' · '.join(link(x) for x in sources[rel]) + '.'
        notice = notices.get(rel[len(A):])
        if branch == '06_Historial' and not notice:
            notice = 'Registro de sesión fechado. Para decidir qué está vigente, consultar ' + link(current) + '; no ejecutar los procedimientos preliminares sin leer sus ampliaciones posteriores.'
        append_nav(rel, hub[branch], extra, notice)
    for rel in list(changes):
        if rel.startswith(A) and rel not in existing and '/Archivo_Documental/' not in rel and rel.split('/')[1] in ('02_Cliente','04_Calidad','06_Historial'):
            if rel.endswith(('04_Refinamiento_Visual_2026-10-03.md','05_Presencia_Atelier_2026-10-03.md','05_Verificacion_Visual_2026-10-03.md','06_Verificacion_Atelier_2026-10-03.md','06_Sesion_2026-10-03.md','07_Correccion_Visual_2026-10-03.md','08_Skills_y_Studio_2026-10-03.md')):
                append_nav(rel, hub[rel.split('/')[1]], notice='Nota del paquete incremental anterior, ahora incorporada al vault activo. Las menciones a fusión pendiente describen el estado al preparar aquel paquete; consultar el registro de organización actual.')
    # Normalize properties on editable legacy notes while keeping their existing properties and prose.
    for rel in existing:
        if rel not in changes:
            continue
        txt=changes[rel]
        match=re.match(r'^---\n(.*?)\n---\n',txt,re.S)
        props=match.group(1) if match else ''
        if re.search(r'^knowledge_id:',props,re.M):
            continue
        title_match=re.search(r'^# (.+)$',txt,re.M)
        title=title_match.group(1) if title_match else Path(rel).stem
        project='Aetherion' if rel.startswith(A) else 'Ultron'
        parent=hub[rel.split('/')[1]] if project=='Aetherion' else (ui if 'Blueprint' in rel else uo if '/Roadmap/' not in rel else UH)
        fields={'knowledge_id':'vault-legacy-'+slug(rel.removesuffix('.md')),'title':json.dumps(title,ensure_ascii=False),'project':project,
                'domain':rel.split('/')[1],'note_type':'evidence' if '/06_Historial/' in rel or '/Memory_Backups/' in rel else 'reference',
                'version':'1.0.0','status':'archived' if '/06_Historial/' in rel or '/Memory_Backups/' in rel else 'current',
                'created':DATE,'updated':DATE,'up':json.dumps([link(parent)],ensure_ascii=False),'related':'[]','replaces':'[]','source_refs':'[]',
                'tags':json.dumps([slug(project)],ensure_ascii=False)}
        additions='\n'.join(k+': '+v for k,v in fields.items() if not re.search(r'^'+re.escape(k)+':',props,re.M))
        content=txt[match.end():] if match else txt
        put(rel,'---\n'+(props+'\n' if props else '')+additions+'\n---\n'+content)
    chronology = A+'06_Historial/01_Cronologia.md'
    put(chronology, changes[chronology] + '\n\n## 2026-10-03 — refinamiento, Atelier y Studio 03\n\nLas primeras revisiones recibieron la crítica de conservar la misma interfaz y cambiar solo colores. Studio separa inicio y laboratorio, incorpora navegación superior y nuevas bibliotecas/resultados. Se documentaron 18 pruebas aprobadas, comprobaciones de widgets en tres tamaños y build Studio 03. La aceptación estética y el recorrido online completo siguen pendientes.\n\n' + link(studio_src) + ' · ' + link(A+'04_Calidad/07_Verificacion_Studio_2026-10-03.md') + '\n\n## 2026-10-03 — skills y organización documental\n\nSe instalaron los paquetes Emil Kowalski, Impeccable y Taste para Codex. Su instalación no representa un rediseño adicional ya aplicado. El usuario autorizó reorganizar el vault excluyendo archivos Karen y Friday: ' + link(T+'01_Skills_Instaladas.md') + ' · ' + link('00_Navegacion/Registro_de_Organizacion.md') + '.')
    # Hubs list their own area, keeping the project hub at branch granularity.
    for folder, (title, desc) in branches.items():
        paths = sorted(set([r for r in existing if r.startswith(A+folder+'/')] + [r for r in changes if r.startswith(A+folder+'/')]))
        paths = [r for r in paths if r != hub[folder] and r != AH]
        body = desc + '\n\n'
        if folder == '06_Historial':
            body += '> [!info] Fecha y autoridad\n> Un registro antiguo conserva cómo se entendía el sistema en ese momento. El corte vigente está en ' + link(current) + '.\n\n'
        groups = defaultdict(list)
        for r in paths:
            part = Path(r).relative_to(A+folder).parts
            groups[part[0] if len(part)>1 else 'Notas del área'].append(r)
        for group, items in groups.items():
            body += '## ' + group.replace('_',' ') + '\n\n'
            body += '\n'.join('- ' + link(r, re.sub(r'^\d+_', '', Path(r).stem).replace('_',' ')) for r in items) + '\n\n'
        note(hub[folder], 'Aetherion — ' + title, AH, body, 'project')
    note(AH, 'Aetherion — mapa del proyecto', ROOT,
         'Aetherion compara modelos locales bajo contexto de equipo y ejecución. La revisión de cliente documentada más reciente es Studio 03. Este mapa organiza el conocimiento por áreas; cada área contiene procesos, evidencia y fuentes.\n\n'
         '## Empezar\n\n' + link(current, 'Estado vigente y límites') + ' · ' + link(A+'00_Gobierno/01_Resumen_Ejecutivo.md', 'Propósito del producto') + '\n\n'
         '## Áreas del proyecto\n\n' + '\n'.join('- ' + link(hub[f], title) + ' — ' + desc for f,(title,desc) in branches.items()) + '\n\n'
         '## Relación con el ecosistema\n\n' + link(A+'00_Gobierno/04_Vinculacion_Core.md') + ' conserva las fronteras entre proyectos. Un enlace en Obsidian no acredita integración técnica.\n\n'
         'La versión anterior de este mapa queda preservada en ' + link(snapshot+'00_MOC_Aetherion_Corte_Anterior.md') + '.', 'project')
    note('00_Navegacion/Rutas_de_Lectura.md', 'Rutas de lectura por tarea', ROOT,
         '## Entender Aetherion\n\n' + link(AH) + ' → ' + link(current) + ' → ' + link(hub['01_Arquitectura']) + '. La arquitectura explica qué produce cada medición; el estado limita lo que puede afirmarse de la entrega.\n\n'
         '## Usar o revisar el cliente\n\n' + link(hub['02_Cliente']) + ' → ' + link(C+'02_Workspace.md') + ' → ' + link(C+'03_Biblioteca.md') + ' → ' + link(C+'04_Laboratorio.md') + ' → ' + link(C+'05_Resultados.md') + '.\n\n'
         '## Administrar una cuenta\n\n' + link(hub['07_Licencias_y_Cuentas']) + ' → ' + link(L+'02_Preparar_Servicio.md') + ' → ' + link(L+'03_Emitir_y_Sincronizar.md') + ' → ' + link(L+'04_Alta_y_Acceso.md') + ' → ' + link(L+'05_Renovacion_y_Suspension.md') + '. Revisar el pase offline antes de interpretar una suspensión.\n\n'
         '## Resolver un fallo\n\n' + link(hub['04_Calidad']) + ' → ' + link(A+'04_Calidad/09_Diagnostico_por_Runtime.md') + '. Si es empaquetado, distinguir el incidente cerrado de cryptography de un error nuevo.\n\n'
         '## Retomar Ultron\n\n' + link(UH) + ' → ' + link(ui) + ' → ' + link(uo) + ' → ' + link(master) + '. Sus roadmaps son planes documentados y no pruebas actuales de servicios.', 'reference', project='Ecosistema', domain='navegacion')
    note('00_Navegacion/Guia_del_Grafo.md', 'Cómo recorrer el grafo', ROOT,
         '## Estructura\n\nMapa general → proyecto → mapa de área → notas específicas. Los enlaces laterales unen conceptos que comparten un procedimiento o una condición; no se enlaza cada nota con todas las demás para aumentar artificialmente el número de líneas.\n\n'
         '## Lectura visual\n\nEl grafo utiliza grupos por ruta: navegación, Aetherion, Ultron, Karen y Friday. Las carpetas de los dos últimos permanecen intactas. Aetherion tiene colores por área para identificar arquitectura, cliente, operaciones, evidencia, licencias y herramientas.\n\n'
         'Se ocultan adjuntos y etiquetas como nodos; se mantienen visibles notas huérfanas y referencias no resueltas para no esconder defectos del contenido preservado. La distancia de enlaces se reduce y la repulsión aumenta respecto al ajuste anterior.\n\n'
         '## Recorrido práctico\n\n1. Abrir el grafo local de una nota de área.\n2. Usar profundidad 1 para su familia y 2 para ver contexto.\n3. En el grafo global filtrar por `path:"Proyecto Aetherion"` o `path:"Proyecto Ultron"` cuando se quiera revisar un proyecto.\n4. Volver al mapa general para cambiar de rama.\n\n'
         'La disposición exacta depende de la simulación de fuerzas y el tamaño de ventana. No es un diagrama con coordenadas fijas. No se requiere otro plugin.', 'reference', project='Ecosistema', domain='navegacion')
    preserved_body='Este índice añade referencias desde una nota nueva. Todos los documentos enlazados permanecen en su ubicación original, con los mismos bytes. No se reorganiza el contenido interno de los proyectos protegidos.\n\n'
    preserved_groups=defaultdict(list)
    for p in all_files:
        rel=p.relative_to(VAULT).as_posix()
        if p.suffix=='.md' and protected(rel):
            preserved_groups[str(Path(rel).parent).replace('\\','/')].append(rel)
    for group,items in sorted(preserved_groups.items()):
        preserved_body+='## '+group.replace('_',' ')+'\n\n'+'\n'.join('- '+link(r,Path(r).stem.replace('_',' ')) for r in sorted(items))+'\n\n'
    note('00_Navegacion/Documentos_Preservados.md','Referencias a documentos preservados',ROOT,preserved_body,'reference',project='Ecosistema',domain='navegacion')
    note('00_Navegacion/Registro_de_Organizacion.md', 'Registro de organización del vault — 3 de octubre', ROOT,
         '## Autorización y protección\n\nEl usuario pidió reorganizar todo excepto archivos Karen y Friday, y confirmó que la vista objetivo es el grafo. Se conserva su ubicación y contenido; los cambios de navegación los referencian sin editar sus archivos. La aplicación utiliza una lista explícita de archivos permitidos y comprueba hashes antes y después.\n\n'
         '## Fuentes utilizadas\n\n- Notas existentes de Aetherion y Ultron: originales preservados; ampliados con navegación.\n- Tres paquetes incrementales Aetherion preparados en esta conversación: notas sustantivas incorporadas sin reemplazar notas existentes.\n- Conversación visible: Studio 03, evidencias y la instalación posterior de skills.\n- Configuración existente del grafo: ajustes por grupos y fuerzas; sin cambios a plugins, temas, snippets o carpetas de asistentes protegidos.\n\n'
         '## Criterio de conservación\n\nSe mantiene el nivel B elegido anteriormente para la síntesis de conversación. Para esta reorganización el contenido original se conserva íntegro; no se busca reducirlo un 20–35 %, porque el usuario solicitó desglosar y conectar. Las páginas de estado, resumen, roadmap y mapa reemplazadas conservan el corte anterior completo en Archivo Documental. Los procesos extraídos mantienen las condiciones y la nota fuente.\n\n'
         '## Cambios sustantivos\n\nMapas por área, cinco notas de flujo Studio, procesos de licencias separados, providers, persistencia, diagnóstico, herramientas de diseño y áreas de Ultron. La referencia de roadmap de voz inexistente en Ultron apunta al roadmap de Karen ya existente; Karen no se modifica.\n\n'
         '## Límites\n\nNo se examina ni modifica el contenido interno de Karen o Friday. Los enlaces rotos preexistentes de esas carpetas no se reparan. No se recuperan conversaciones históricas no suministradas. No se certifican servicios, benchmarks o integraciones durante esta operación documental. La copia de seguridad y el informe de validación quedan fuera del vault.', 'evidence', project='Ecosistema', domain='navegacion')
    # Save a concrete, reviewable write set. Nothing in the active vault has been changed yet.
    manifest = []
    for rel, txt in changes.items():
        p = STAGE / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(txt, encoding='utf-8')
        manifest.append({'path': rel, 'before_sha256': sha(orig[rel]) if orig[rel] is not None else None, 'after_sha256': sha(p.read_bytes()), 'action': 'update' if orig[rel] is not None else 'create'})
    graph = json.loads((VAULT/'.obsidian/graph.json').read_text(encoding='utf-8'))
    colors = [('path:"00_Navegacion" OR file:"00_MOC_Obsidian"', '#F0EFEA'),
              ('path:"Proyecto Aetherion/00_Gobierno"', '#E8BC69'), ('path:"Proyecto Aetherion/01_Arquitectura"', '#6BA9EA'),
              ('path:"Proyecto Aetherion/02_Cliente"', '#A88BEB'), ('path:"Proyecto Aetherion/03_Datos_y_Operaciones"', '#5EC7B4'),
              ('path:"Proyecto Aetherion/04_Calidad"', '#ED9A70'), ('path:"Proyecto Aetherion/05_Roadmap"', '#C6CF75'),
              ('path:"Proyecto Aetherion/06_Historial"', '#8C99AB'), ('path:"Proyecto Aetherion/07_Licencias_y_Cuentas"', '#E8809D'),
              ('path:"Proyecto Aetherion/08_Herramientas_Diseno"', '#C3A7E2'), ('path:"Proyecto Ultron"', '#50BECC'),
              ('path:"Karen Asistant"', '#7CB779'), ('path:"Proyecto FRIDAY"', '#DA80BA')]
    graph.update({'colorGroups': [{'query': q, 'color': {'a':1,'rgb':int(c[1:],16)}} for q,c in colors],
                  'search': '', 'showTags':False, 'showAttachments':False, 'hideUnresolved':False, 'showOrphans':True,
                  'textFadeMultiplier':0, 'nodeSizeMultiplier':1.1, 'lineSizeMultiplier':0.8,
                  'centerStrength':0.35, 'repelStrength':16, 'linkStrength':0.65, 'linkDistance':140})
    graphfile = OUT/'graph-settings.json'
    graphfile.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding='utf-8')
    manifest.append({'path':'.obsidian/graph.json','before_sha256':sha((VAULT/'.obsidian/graph.json').read_bytes()),'after_sha256':sha(graphfile.read_bytes()),'action':'update'})
    (OUT/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT/'source-map.json').write_text(json.dumps(sources, ensure_ascii=False, indent=2), encoding='utf-8')
    baseline = graph_report({p.relative_to(VAULT).as_posix():p.read_text(encoding='utf-8-sig') for p in all_files if p.suffix=='.md'})
    (OUT/'graph-before.json').write_text(json.dumps(baseline, ensure_ascii=False, indent=2), encoding='utf-8')
    merged = {p.relative_to(VAULT).as_posix():p.read_text(encoding='utf-8-sig') for p in all_files if p.suffix=='.md'}
    merged.update(changes)
    inventory = '| Path | Estado |\n| --- | --- |\n' + '\n'.join('| '+r+' | verificado |' for r in sorted(merged))
    inventory += '\n' + '\n'.join('| '+Path(r).name+' | referencia por nombre |' for r in sorted(merged))
    (OUT/'known-paths.md').write_text(inventory,encoding='utf-8')
    after = graph_report(merged)
    (OUT/'graph-preview.json').write_text(json.dumps(after, ensure_ascii=False, indent=2), encoding='utf-8')
    new_missing = [x for x in after['unresolved'] if (x['path'],x['target']) not in {(a['path'],a['target']) for a in baseline['unresolved']}]
    assert not new_missing, new_missing
    print(json.dumps({'creates':sum(m['action']=='create' for m in manifest),'updates':sum(m['action']=='update' for m in manifest),'protected_files':len(protected_before),'before':baseline['stats'],'preview':after['stats']}, ensure_ascii=False))

def graph_report(notes):
    by_stem = defaultdict(list)
    for rel in notes:
        by_stem[Path(rel).stem].append(rel)
    adj = {r:set() for r in notes}
    missing = []
    for rel, text in notes.items():
        for m in re.finditer(r'!?\[\[([^\]|]+)(?:\|[^\]]*)?\]\]', text):
            target = m.group(1).split('#',1)[0].strip()
            if not target: continue
            exact = target if target.endswith('.md') else target+'.md'
            candidates = [exact] if exact in notes else by_stem.get(Path(target).stem, [])
            if not candidates:
                missing.append({'path':rel,'target':target,'protected':protected(rel)})
            elif len(candidates)==1:
                dest = candidates[0]
                if dest != rel:
                    adj[rel].add(dest); adj[dest].add(rel)
    seen = set(); comps = []
    for r in adj:
        if r in seen: continue
        component=set(); queue=deque([r]); seen.add(r)
        while queue:
            node=queue.popleft(); component.add(node)
            for dest in adj[node]-seen: seen.add(dest); queue.append(dest)
        comps.append(component)
    return {'stats':{'notes':len(notes),'edges':sum(map(len,adj.values()))//2,'components':len(comps),'orphans':sum(not x for x in adj.values()),'unresolved':len(missing)},
            'unresolved':missing,'orphans':[r for r,v in adj.items() if not v],
            'managed_disconnected':[r for r in adj if r.startswith(('Proyecto Aetherion/','Proyecto Ultron/','00_Navegacion/')) and r not in next((c for c in comps if ROOT in c),set())]}

def apply():
    manifest = json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
    protected_before = json.loads((OUT/'protected-before.json').read_text(encoding='utf-8'))
    # Verify the complete transaction before touching any file.
    for m in manifest:
        rel = m['path']; p = (VAULT/rel).resolve()
        assert p.is_relative_to(VAULT.resolve()) and not protected(rel), rel
        assert rel == '.obsidian/graph.json' or rel == ROOT or rel.startswith(('00_Navegacion/','Proyecto Aetherion/','Proyecto Ultron/')),rel
        got = sha(p.read_bytes()) if p.exists() else None
        assert got==m['before_sha256'], 'Concurrent modification: '+rel
        source = OUT/'graph-settings.json' if rel=='.obsidian/graph.json' else STAGE/rel
        assert sha(source.read_bytes())==m['after_sha256']
    for rel,h in protected_before.items():
        assert sha((VAULT/rel).read_bytes())==h, 'Protected change detected: '+rel
    backup = OUT/'backup-before.zip'
    assert not backup.exists(), 'Backup already exists; refuse repeat apply'
    with zipfile.ZipFile(backup,'w',zipfile.ZIP_DEFLATED) as z:
        for m in manifest:
            p=VAULT/m['path']
            if p.exists(): z.write(p,m['path'])
    with zipfile.ZipFile(backup) as z: assert z.testzip() is None
    applied=[]
    try:
        for m in manifest:
            rel=m['path']; p=VAULT/rel
            source=OUT/'graph-settings.json' if rel=='.obsidian/graph.json' else STAGE/rel
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(source.read_bytes()); applied.append(m)
            assert sha(p.read_bytes())==m['after_sha256']
    except Exception:
        # Restore only this explicit transaction, never recursively remove directories.
        with zipfile.ZipFile(backup) as z:
            for m in reversed(applied):
                p=(VAULT/m['path']).resolve()
                assert p.is_relative_to(VAULT.resolve()) and not protected(m['path'])
                if m['before_sha256'] is None: p.unlink()
                else: p.write_bytes(z.read(m['path']))
        raise
    protected_after={p.relative_to(VAULT).as_posix():sha(p.read_bytes()) for p in vault_files() if protected(p.relative_to(VAULT).as_posix())}
    assert protected_after==protected_before, 'Protected inventory mismatch'
    report=graph_report({p.relative_to(VAULT).as_posix():p.read_text(encoding='utf-8-sig') for p in vault_files() if p.suffix=='.md'})
    report.update({'protected_files_verified':len(protected_after),'creates':sum(m['action']=='create' for m in manifest),'updates':sum(m['action']=='update' for m in manifest),'backup_integrity':'passed'})
    assert not report['managed_disconnected'],report['managed_disconnected']
    (OUT/'validation-after.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('unresolved','orphans')},ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('mode',choices=['prepare','apply']); args=parser.parse_args()
    prepare() if args.mode=='prepare' else apply()
