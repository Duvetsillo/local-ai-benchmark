---
proyecto: Aetherion
tipo: troubleshooting
tags: [aetherion, debug, operaciones]
knowledge_id: vault-legacy-proyecto-aetherion-04-calidad-03-guia-de-diagnostico
title: "Guía de diagnóstico"
project: Aetherion
domain: 04_Calidad
note_type: reference
version: 1.0.0
status: current
created: 2026-10-03
updated: 2026-10-03
up: ["[[Proyecto Aetherion/04_Calidad/00_Mapa_Calidad]]"]
related: []
replaces: []
source_refs: []
---

# Guía de diagnóstico

## Error genérico de arranque

1. Capturar toda la ventana; expandir detalles si existe esa opción.
2. Guardar traceback antes de cerrar.
3. Registrar hash del exe, fecha, Windows, Python, PyInstaller y commit.
4. Comparar fuente con build empaquetado.
5. Reproducir con consola y log completo.
6. Aplicar cambio en entorno temporal.
7. Abrir y recorrer interfaz; después sustituir distribución.

## Ollama no descubierto

Confirmar servicio, ollama list y /api/tags en 127.0.0.1:11434. Capturar error HTTP/timeout antes de variar código.

## GGUF visible pero no carga

Verificar extensión, ruta, espacio, llama-cpp-python y compatibilidad GPU/CPU. El archivo visible no garantiza carga.

## Sin métricas GPU

Revisar nvidia-smi; distinguir detección de aceleración real. Aceptar unknown/null en equipo sin proveedor de telemetría.

## JSON ausente

Revisar directorio elegido, permisos, espacio, fecha y si el motor o el cliente generó el archivo. Conservar error; no borrar temporales sin revisarlos.

## Reporte de error

    Fecha:
    Commit:
    Hash del exe:
    Windows/DPI:
    Python/PyInstaller:
    Acción:
    Error exacto:
    Desde fuente también falla:
    Proveedor/modelo:
    Ruta de resultados:

## Navegación documental

Volver a [[Proyecto Aetherion/04_Calidad/00_Mapa_Calidad]].

Desglose temático: [[Proyecto Aetherion/04_Calidad/09_Diagnostico_por_Runtime]].
