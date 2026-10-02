# Aetherion License Service

Servicio privado para reclamar licencias, crear cuentas, iniciar/cerrar sesiones, listar usuarios y ampliar vencimientos sin volver a emitir claves. Aetherion sigue haciendo los benchmarks localmente. La API solo administra identidad y acceso.

## Recorrido de la licencia y la cuenta

1. El propietario crea una licencia en Aetherion License Manager. La herramienta firma la clave localmente y la registra en esta API con el token de administrador; la clave privada de firma no se sube al VPS.
2. Una clave sincronizada puede reclamarse una sola vez. El titular elige username y una contraseña de al menos 12 caracteres; el servidor vincula cuenta, licencia e ID del equipo.
3. Los siguientes inicios de sesión usan username/password en el mismo equipo. El servidor guarda la contraseña con Argon2id y devuelve un token de sesión revocable.
4. License Manager consulta `GET /v1/admin/users` y ofrece añadir días con `POST /v1/admin/users/{id}/renew`. Los días se suman al vencimiento futuro, o comienzan desde ahora si ya venció. No se emite otra clave.
5. El botón **SIGN OUT** revoca la sesión en el servidor y elimina la sesión cacheada del cliente.

Cada clave permanece ligada a un solo equipo y queda asociada a una sola cuenta. El servidor guarda el hash SHA-256 de la licencia, nunca la contraseña ni la clave completa. Una licencia ilimitada no se puede renovar por días.

## Despliegue en el Home Lab con Docker

Requisitos: Linux x64 con Docker Engine y Compose y el subdominio `aetherionlbs.duckdns.org`. El servicio DuckDNS actualiza la IPv4 pública desde Docker. El router/firewall debe permitir TCP 80 y 443 hacia el host Docker con una IP LAN estable; UDP 443 es opcional para HTTP/3.

1. Copia `server/` al host Docker.
2. Copia `.env.example` a `.env` y protege el archivo con permisos de propietario (`chmod 600 .env`). No incluyas el archivo real en Git ni lo compartas.
3. Conserva `AETHERION_DOMAIN=aetherionlbs.duckdns.org`; completa `AETHERION_ADMIN_TOKEN`, `AETHERION_LICENSE_PUBLIC_KEY_N` usando `PUBLIC_KEY_N` de `src/local_ai_benchmark/client/licensing.py` y `DUCKDNS_TOKEN` con el token privado de DuckDNS.
4. Confirma la IP LAN estable del host Docker y reserva esa dirección en DHCP. Reenvía solo TCP 80 y 443 a ese host. Mantén el firewall habilitado; no uses DMZ ni expongas el puerto 8000.
5. Ejecuta `docker compose --env-file .env up -d --build` desde `server/`. `aetherion-duckdns` actualizará el nombre aproximadamente cada cinco minutos y no necesita puertos entrantes.
6. Comprueba `https://aetherionlbs.duckdns.org/health` cuando DNS y los reenvíos estén listos.
7. En License Manager abre **Server settings** e introduce la URL HTTPS y el token administrativo. Configura los clientes con la misma URL.

Caddy termina TLS con certificados automáticos y reenvía al API interno. Nunca abras el puerto 8000 a internet. La imagen DuckDNS recibe el token como variable de entorno; protege el `.env`, el host y el acceso al daemon Docker.

## Variables y datos persistentes

- `AETHERION_DOMAIN`: dominio HTTPS público del servicio.
- `AETHERION_ADMIN_TOKEN`: bearer secret de 32 caracteres o más para License Manager; nunca se distribuye en Aetherion Client.
- `AETHERION_LICENSE_PUBLIC_KEY_N`: módulo público RSA que corresponde a las licencias que emite el License Manager.
- `/data/aetherion.sqlite3`: cuentas, licencias reclamadas, vencimientos y sesiones revocables.
- `/data/offline-signing-ed25519.pem`: clave privada del servidor que firma pases temporales offline.
- `caddy-data`: certificados y datos TLS.

Los dos volúmenes son persistentes y contienen datos esenciales. Respalda el volumen `aetherion-data` con un método consistente para SQLite y protege el volumen `caddy-data`. Protege el `.env`; no lo subas al repositorio ni lo distribuyas. Cambiar el token de administrador invalida la configuración local del License Manager hasta que se actualice allí.

## Periodo sin conexión

Después de un inicio de sesión correcto, el servidor emite un pase firmado por Ed25519 y válido hasta siete días desde la última validación, con el límite adicional de vencimiento de licencia más siete días. Aetherion guarda ese pase y el token de sesión cifrados con DPAPI bajo el perfil de Windows, ligados al mismo usuario de Windows y al mismo Device ID.

Si se corta internet, la sesión activa puede continuar y volver a abrir Aetherion desde el mismo perfil por un máximo de siete días. El botón **CONTINUE OFFLINE** intenta restaurar la última sesión guardada. Si el usuario cierra sesión, el cliente borra el pase local y exige conexión para volver a autenticarse. Al reconectar, el servidor vuelve a verificar estado/fecha; una cuenta bloqueada o una suscripción vencida no obtiene una autorización offline nueva.

## Seguridad operativa

- Contraseñas con Argon2id y sal aleatoria individual; nunca se registran en texto claro.
- Sesiones aleatorias almacenadas como hash SHA-256, vencen a los 30 días y se pueden revocar al cerrar sesión o desactivar una cuenta.
- El ID del equipo se compara en el servidor durante el alta y el inicio de sesión.
- El administrador usa un bearer token separado del cliente y las peticiones al VPS requieren HTTPS.
- El cliente conserva un pase de siete días firmado por la clave privada Ed25519 del servidor; el archivo solo vive en el volumen de datos del servicio.
- Los endpoints administrativos no exponen hashes de contraseña ni secretos de sesión.
- La posesión del VPS, DNS, `.env` y volúmenes equivale a controlar el servicio. Usa acceso SSH restringido y respaldos protegidos.

La API no incluye restablecimiento de contraseña por email ni cobro automatizado. La renovación se opera manualmente después de confirmar el pago. El administrador puede suspender y reactivar una cuenta.
