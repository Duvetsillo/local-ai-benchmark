---
proyecto: Aetherion
tipo: hardware
tags: [aetherion, hardware, telemetria]
knowledge_id: vault-legacy-proyecto-aetherion-01-arquitectura-06-perfil-de-hardware
title: "Perfil de hardware y métricas"
project: Aetherion
domain: 01_Arquitectura
note_type: reference
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/01_Arquitectura/00_Mapa_Arquitectura]]"]
related: []
replaces: []
source_refs: []
---

# Perfil de hardware y métricas

## Campos visibles en el código

Sistema operativo/versión, arquitectura, procesador, núcleos e hilos cuando psutil lo permite, RAM total/disponible y GPUs identificadas. nvidia-smi puede devolver nombre, memoria total y versión de driver. Se exponen detectores para CUDA, ROCm, DirectML o Metal según plataforma.

Un detector binario como la presencia de nvidia-smi no prueba que el runtime esté acelerando inferencia.

## Dependencias y ausencias

psutil es opcional y amplía telemetría. Los datos ausentes se devuelven como UNKNOWN o null según el campo. Los perfiles del motor común y del cliente tienen estructuras que pueden diferir; no intercambiar claves sin normalizar.

## Métricas de corrida

Pueden incluir tiempo hasta primer token, tokens/segundo cuando hay conteo y duración, CPU, RAM, VRAM aproximada desde perfil y temperatura GPU si está disponible. Algunas lecturas son puntuales y otras vienen del proveedor.

## Comparación responsable

1. Mantener iguales modelo, formato y cuantización.
2. Registrar runtime, driver, parámetros y backend.
3. Cerrar cargas competidoras.
4. Repetir si la variabilidad importa.
5. Separar latencia, velocidad y calidad.
6. Informar campos ausentes.

Una lectura instantánea no describe todos los picos. GPU presente no significa que el modelo se ejecutó en GPU.

## Navegación documental

Volver a [[Proyecto Aetherion/01_Arquitectura/00_Mapa_Arquitectura]].
