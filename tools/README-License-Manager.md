# Aetherion License Manager

Aplicación gráfica independiente para el propietario del proyecto. El usuario final recibe solo Aetherion Client y una clave firmada para su equipo.

## Uso

1. Ejecuta `Start-Aetherion-License-Manager.bat` desde la carpeta del Escritorio.
2. En el primer inicio, confirma que la ruta del proyecto apunta al repositorio de Aetherion y selecciona **Create authority**.
3. Desde la raíz del repositorio, reconstruye el cliente con `python build_client.py` y distribuye `downloads/Aetherion-Client.exe` para que incorpore la clave pública recién configurada. La versión que no tenga la clave pública aún no puede verificar licencias. El proyecto requiere Python con sus dependencias de compilación instaladas; la compilación existente tiene pendiente resolver el incidente de arranque descrito en la documentación del proyecto.
4. El usuario final abre Aetherion; la pantalla de activación muestra su ID de equipo de 32 caracteres.
5. Pega ese ID en el generador, selecciona Trial (7 días), duración personalizada o Unlimited y genera la licencia.
6. Copia la licencia completa al usuario para pegarla en Aetherion.

## Protección de la autoridad

La clave privada se conserva en `%LOCALAPPDATA%\Aetherion\licensing\signing_key.dpapi`, cifrada con Windows DPAPI para la cuenta y el equipo actuales. El archivo `licensing.py` del repositorio contiene solo la clave pública. Mantén protegido el perfil de Windows y no distribuyas la clave privada. El archivo DPAPI no constituye una copia portable: si se pierde el perfil/equipo o se reemplaza la autoridad, las licencias emitidas previamente no corresponderán a la nueva clave.

Trial dura siete días desde la emisión. Duration permite de 1 a 3650 días. Unlimited no tiene fecha de expiración. Todas las licencias quedan vinculadas al ID de un solo equipo.

El administrador es una ventana PowerShell/Windows Forms, no un instalador EXE. Requiere Windows PowerShell 5.1 o PowerShell para Windows con acceso a Windows Forms y DPAPI.
