---
knowledge_id: vault-20261003-proyecto-aetherion-06-historial-archivo-documental-01-resumen-ejecutivo-corte-anterior
title: "Corte anterior — 01_Resumen_Ejecutivo"
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
source_refs: ["[[Proyecto Aetherion/00_Gobierno/01_Resumen_Ejecutivo]]"]
tags: ["aetherion", "area/06-historial", "evidence"]
---

# Corte anterior — 01_Resumen_Ejecutivo
> [!abstract] Registro histórico preservado
> Copia del contenido encontrado antes de esta reorganización. Puede contener estados ya corregidos; para operar consulta [[Proyecto Aetherion/00_Gobierno/02_Estado_Actual]].

---
proyecto: Aetherion
tipo: resumen
tags: [aetherion, benchmark, modelos-locales]
---

# Aetherion — resumen ejecutivo

## En una frase

Aetherion es la marca de producto de Local AI Benchmark: combina un sitio público con un cliente de escritorio Windows, CLI y dashboard local. El cliente perfila el equipo, descubre modelos locales y ejecuta tareas repetibles para ayudar a elegir qué modelo funciona mejor para un hardware y una carga de trabajo concretos.

## Problema que resuelve

Las cifras públicas no siempre predicen el resultado de un modelo en un ordenador particular. El rendimiento depende del equipo, runtime, cuantización, memoria, parámetros y tipo de tarea. Aetherion reúne descubrimiento, perfil del sistema, pequeñas comprobaciones y resultados locales en un solo flujo.

No pretende producir un ranking universal. Su propósito es apoyar la comparación en el dispositivo donde se usarán los modelos y conservar el contexto necesario para entender cada corrida.

## Capacidades documentadas

- Descubrimiento de modelos mediante Ollama.
- Descubrimiento de archivos GGUF en una carpeta elegida.
- Ejecución mediante Ollama o llama.cpp integrado a través de llama-cpp-python.
- Perfil de sistema operativo, arquitectura, CPU, RAM y datos de GPU disponibles.
- Tareas de uso general, código, matemáticas, JSON y español.
- Validación sencilla, tiempos y telemetría expuesta por el runtime.
- Guardado local de resultados JSON.
- Evaluación heurística de compatibilidad del modelo con RAM/VRAM y orientación de runtime; no garantiza que el modelo cargue o rinda bien.
- Descarga de modelos GGUF desde el cliente, selección de carpeta propia y asistencia para instalar runtimes locales.
- Interfaz Tkinter con Dashboard, Benchmarks, Models, Results, Hardware, History y Settings; además de CLI, dashboard local y sitio público en el repositorio.
- Activación offline por licencia firmada ligada al equipo y administrador separado para el propietario, implementados en fuente.

## Límites de interpretación

Los validadores actuales son simples. Una explicación con dos frases puede ser incorrecta; que aparezca 888 no prueba que la respuesta sea completamente correcta; un programa que compila puede fallar en casos reales. Aprobar una regla no equivale a una evaluación completa de calidad ni a un benchmark académico.

## Audiencia

Personas que ejecutan modelos localmente y desean compararlos bajo el mismo equipo y parámetros, sin depender de una tabla externa ni enviar resultados a un servicio en la nube.

## Estado observado

La interfaz tiene una paleta azul pizarra con acentos menta en el código. El fuente y la función de licencias han avanzado, pero la última comprobación del ejecutable distribuible observó “Unhandled exception in script”; el build exitoso no confirma el arranque ni que las licencias estén incluidas en el binario. Véase [[Proyecto Aetherion/00_Gobierno/02_Estado_Actual]] y [[Proyecto Aetherion/04_Calidad/02_Incidente_Arranque_Cliente]].
