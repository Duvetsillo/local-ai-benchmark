# License Manager: planes y presencia

Actualizado el 9 de octubre de 2026. Se conservó la versión más reciente del escritorio, que ya tenía el editor de planes, las contraseñas temporales y el diseño con Inter. Esa versión ahora está mantenida en `tools`, con el lanzador y los fuentes del instalador 1.1.0.

## Diseño aplicado

Canvas `#080A0F`, superficie `#11151E`, controles `#1A2030`, texto `#F5F7FA`, conexión `#9BE0B5`, foco y selección `#8BA8FF`. Inter para la interfaz, con Segoe UI como alternativa. Emisión con proyecto a la izquierda y formulario a la derecha; cuentas con búsqueda, filtro, tabla y editor debajo. La tabla tiene filas de 40 px, encabezados claros, IDs de equipo ocultos y estados expresados con texto y color. El panel permite desplazamiento al tamaño mínimo.

| Before | After | Why |
| --- | --- | --- |
| Presencia inferida desde último login, sesiones o cadenas ambiguas | Booleano autenticado del servidor; Unknown si falta | Una sesión antigua no prueba conexión |
| Recently active se contaba como online | Online, Offline y Unknown separados | Los contadores expresan evidencia disponible |
| Panel de selección con controles superpuestos | Fila con altura fija y acciones debajo del detalle | Nombre, acceso y cambios permanecen legibles |
| Selector de planes deshabilitado incluso con una cuenta seleccionada | Selección habilita plan, duración personalizada y guardado | Permite editar planes de cuentas ya creadas |
| Filtro podía ocultar una cuenta seleccionada | Selección oculta borrada; acciones desactivadas | Evita cambiar la cuenta equivocada |
| Renovación y cambio de plan sin presencia verificable | Editor existente conservado y presencia actualizada cada 30 segundos | Se puede editar sin perder la duración escogida |
| Acción heredada de reset-key sin ruta implementada | Acción retirada; contraseña y desvinculación conservadas | La interfaz ofrece operaciones soportadas |

## Verificación

30 pruebas pasan: planes, renovación de credenciales, presencia, logout, suspensión, caducidad y migración repetible. Una prueba HTTP ASGI verifica autenticación administrativa, contacto del cliente y cambio a 45 días sin sustituir cuenta/licencia. Solo se usan bases temporales y claves de pruebas. Se comprobaron filtros combinados, eliminación de selección oculta y renderizado a 1240×780 y 960×600 desde la interfaz real. Los scripts PowerShell se cargaron sin errores; el instalador 1.1.0 se compiló correctamente.

El portfolio incorpora tres capturas con cuentas ficticias, texto español/inglés y galería de 18 imágenes. Las capturas no leen configuración DPAPI, claves privadas ni cuentas reales, y el entorno de captura bloquea la red y las mutaciones. Se verificaron carga de imágenes, navegación, Escape, restauración de foco y ausencia de overflow a 1280 px y 390 px; la consola del navegador no informó errores.

## Estado de entrega

La copia del escritorio está actualizada y dispone de un acceso directo **Aetherion License Manager (actualizado)**. La copia de Program Files no pudo reemplazarse por falta de elevación; el instalador generado permite actualizarla. Los fuentes del portfolio están actualizados localmente; no se publicó un despliegue web.

El nuevo servidor no se desplegó: la conexión SSH guardada rechazó el acceso y la consulta HTTPS administrativa no respondió correctamente. La app presenta Unknown cuando el servicio no suministra presencia. Se pidió al propietario la conexión y la carpeta del VPS. No se cambiaron planes de cuentas reales ni se emitieron claves durante la verificación.
