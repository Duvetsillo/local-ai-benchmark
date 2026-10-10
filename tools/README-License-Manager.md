# Aetherion License Manager

Aplicación gráfica administrativa para Windows. Mantiene la clave privada de firma en el perfil Windows del propietario y administra licencias/cuentas mediante el servicio del VPS.

La interfaz comparte el lenguaje visual nativo de Aetherion Studio y su fuente Inter. El archivo de licencia SIL Open Font License se instala junto con la fuente en `Assets`.

## Abrir

Ejecuta `Start-Aetherion-License-Manager.bat` en la carpeta `C:\Users\Dayve\Desktop\Aetherion License Manager`. El fuente mantenible está en `tools/Aetherion-License-Manager.ps1` y `tools/Aetherion-License-Manager.UI.ps1`. La copia del escritorio incluye el acceso directo **Aetherion License Manager (actualizado)**; el acceso directo anterior sigue apuntando a Program Files hasta ejecutar el instalador actualizado con permisos de administrador.

## Instalar

El instalador de Windows se genera como `dist\Aetherion-License-Manager-Setup.exe`. Para reconstruirlo, instala Inno Setup 6 o 7 y el SDK de .NET 8, y ejecuta `Installer\Build-Installer.ps1`. El instalador agrega accesos directos al menú Inicio y permite crear uno en el escritorio; también comprueba que esté instalado .NET 8 Desktop Runtime (x64) y abre la página oficial si falta. Requiere Windows x64 y Windows PowerShell 5.1.

## Configurar el servicio

Pulsa **Service settings** y escribe la URL HTTPS y el token administrativo de `server/.env`. La aplicación verifica el token consultando el endpoint administrativo y guarda la URL/token cifrados con Windows DPAPI para la cuenta local. No uses la cuenta del License Manager en los clientes finales y no compartas el token.

## Firmar y emitir una clave

1. Verifica la ruta del repositorio Aetherion.
2. La autoridad se prepara una única vez con **Create authority**. La clave privada RSA se almacena cifrada en `%LOCALAPPDATA%\Aetherion\licensing\signing_key.dpapi`.
3. Copia el Device ID desde Aetherion Client.
4. Elige Trial (7 días), duración de 1 a 3650 días o Unlimited.
5. El formulario indica los requisitos pendientes para emitir una clave. **Generate and sync** señala qué configuración falta si aún no se puede emitir; **Copy key** se activa después de firmar y sincronizar correctamente. La clave solo aparece tras sincronizarse con HTTPS. Si cambias los datos de emisión, la clave anterior se borra y debe generarse otra antes de copiarla.
6. Entrega la clave por un canal seguro. Cada licencia se liga a un equipo y se reclama una vez para crear una cuenta.

Las claves creadas con versiones anteriores pueden sincronizarse desde **Sync existing key** pegando la clave completa. El servidor valida su firma antes de registrarla. No se transmite la clave privada.

## Usuarios y renovaciones

En **Manage accounts** consulta cuenta, acceso, conexión, plan, vencimiento, días restantes y último contacto. El Device ID queda oculto, pero puedes buscar por username o Device ID. Filtra por Online, Offline o Unknown. En **New plan**, Trial reemplaza el plazo con 7 días desde hoy; Custom lo reemplaza por 1 a 3650 días desde hoy; Unlimited quita el vencimiento. Cambiar el plan conserva la cuenta y su estado de habilitación/suspensión; no crea otra clave.

**Extend and reactivate** es una acción distinta: suma los días al vencimiento futuro, o comienza desde hoy si ya venció, y reactiva la cuenta. Confirma el pago fuera de la app antes de cambiar de plan o ampliar el acceso.

El control **Disable / enable** bloquea o reactiva la cuenta. La suspensión revoca sesiones activas y se aplica al próximo contacto del cliente; la sesión offline ya firmada puede durar hasta siete días desde su última validación.

**Reset password** permite establecer una contraseña nueva o generar una temporal. Las contraseñas existentes no se pueden consultar: el servicio solo conserva hashes Argon2id. Toda contraseña asignada por el administrador requiere que el usuario la cambie en su siguiente inicio de sesión online. La temporal se muestra una sola vez; compártela por un canal seguro.

**Unlink device** revoca sesiones online y borra el Device ID asociado. El próximo inicio de sesión correcto enlaza la cuenta con el equipo que se autentique primero. Una sesión offline ya emitida en el dispositivo anterior puede seguir válida hasta siete días desde la última comprobación online.

Para activar estas funciones en el VPS, despliega también la versión actualizada de `server/app.py` con `docker compose --env-file .env up -d --build` desde la carpeta `server` del proyecto Aetherion. Publica además una versión recompilada de Aetherion Client para que acepte el cambio obligatorio de contraseña temporal; las versiones anteriores no implementan ese flujo. El instalador de Windows no actualiza el servicio remoto.

## Despliegue y seguridad

El propietario debe configurar un dominio y VPS antes de usar el modo central. Sigue `server/README.md`. No compartas ni subas `.env`, el bearer token, la autoridad privada, los datos SQLite o el volumen de llaves offline. Conserva copias de seguridad cifradas del volumen de datos del servicio.

El administrador requiere Windows PowerShell 5.1 o PowerShell para Windows con Windows Forms y DPAPI.

## Presencia de cuentas

Online significa contacto autenticado en los últimos seis minutos con una sesión vigente, sin suspensión ni vencimiento. Un inicio de sesión correcto registra contacto; la comprobación periódica del cliente Qt lo actualiza cada cinco minutos. Logout revoca la sesión y elimina su presencia online. Cerrar la app o perder conexión se refleja al vencer la ventana de seis minutos. Una sesión antigua de treinta días no prueba conexión. Offline puede incluir clientes usando el pase local; Unknown indica falta de datos o servicio antiguo.

**Live status (30s)** actualiza solo conexión y último contacto mientras el panel tiene foco. Conserva la selección y la duración que estás editando. **Refresh list** vuelve a cargar la cuenta completa; las acciones guardadas recargan el estado. Los filtros borran una selección que dejan oculta para evitar aplicar cambios a una cuenta invisible.

El VPS debe usar el nuevo `server/app.py`. La migración SQLite añade `sessions.last_seen_at`, sin alterar licencias ni contraseñas. La comprobación remota no pudo completarse en esta sesión; no se modificaron cuentas reales.

## Capturas seguras

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/Preview-License-Manager.ps1` genera capturas desde la interfaz real con cuentas ficticias. No lee las credenciales guardadas, no abre claves privadas y bloquea peticiones de red y cambios de cuentas. Las tres imágenes públicas del portfolio muestran emisión vacía, gestión de cuentas y edición de un plan.
