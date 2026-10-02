# Aetherion License Manager

Aplicación gráfica administrativa para Windows. Mantiene la clave privada de firma en el perfil Windows del propietario y administra licencias/cuentas mediante el servicio del VPS.

## Abrir

Ejecuta `Start-Aetherion-License-Manager.bat` en la carpeta `C:\Users\Dayve\Desktop\Aetherion License Manager`. El fuente mantenible está en `tools/Aetherion-License-Manager.ps1`.

## Configurar el servicio

Pulsa **Server settings** y escribe la URL HTTPS y el token administrativo de `server/.env`. La aplicación comprueba `/health`; guarda la URL/token cifrados con Windows DPAPI para la cuenta local. No uses la cuenta del License Manager en los clientes finales y no compartas el token.

## Firmar y emitir una clave

1. Verifica la ruta del repositorio Aetherion.
2. La autoridad se prepara una única vez con **Create authority**. La clave privada RSA se almacena cifrada en `%LOCALAPPDATA%\Aetherion\licensing\signing_key.dpapi`.
3. Copia el Device ID desde Aetherion Client.
4. Elige Trial (7 días), duración de 1 a 3650 días o Unlimited.
5. **Generate license key** firma en este equipo y sincroniza con el servicio usando HTTPS. El control solo muestra la clave si la sincronización fue exitosa.
6. Entrega la clave por un canal seguro. Cada licencia se liga a un equipo y se reclama una vez para crear una cuenta.

Las claves creadas con versiones anteriores pueden sincronizarse desde **Sync existing key** pegando la clave completa. El servidor valida su firma antes de registrarla. No se transmite la clave privada.

## Usuarios y renovaciones

En **Manage accounts** consulta username, estado, plan, vencimiento, días restantes, Device ID e inicio de sesión más reciente. **Extend selected account** añade los días ingresados a la misma cuenta/licencia. Confirma el pago fuera de la app antes de ampliar el acceso. No se entrega una nueva clave.

El control **Disable / enable** bloquea o reactiva la cuenta. La suspensión revoca sesiones activas y se aplica al próximo contacto del cliente; la sesión offline ya firmada puede durar hasta siete días desde su última validación.

## Despliegue y seguridad

El propietario debe configurar un dominio y VPS antes de usar el modo central. Sigue `server/README.md`. No compartas ni subas `.env`, el bearer token, la autoridad privada, los datos SQLite o el volumen de llaves offline. Conserva copias de seguridad cifradas del volumen de datos del servicio.

El administrador requiere Windows PowerShell 5.1 o PowerShell para Windows con Windows Forms y DPAPI.
