from __future__ import annotations

import subprocess
import sys
import os
from shutil import copy2
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)


def sign_release(exe_file: Path) -> None:
    certificate = os.environ.get("AETHERION_CERTIFICATE")
    if not certificate:
        return
    signtool = os.environ.get("AETHERION_SIGNTOOL", "signtool")
    command = [
        signtool,
        "sign",
        "/fd",
        "SHA256",
        "/tr",
        "http://timestamp.digicert.com",
        "/td",
        "SHA256",
        "/f",
        certificate,
    ]
    password = os.environ.get("AETHERION_CERTIFICATE_PASSWORD")
    if password:
        command.extend(["/p", password])
    command.append(str(exe_file))
    subprocess.run(command, check=True, cwd=ROOT)


def build_installer() -> str:
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--distpath",
        str(DIST),
        "--workpath",
        str(ROOT / "build" / "pyinstaller"),
        str(ROOT / "Aetherion-Client.spec"),
    ]
    subprocess.run(command, check=True, cwd=ROOT)
    exe_file = DIST / "Aetherion-Client.exe"
    if not exe_file.is_file():
        raise FileNotFoundError("Aetherion client was not generated. Install PyInstaller and retry.")
    sign_release(exe_file)
    download_dir = ROOT / "downloads"
    download_dir.mkdir(exist_ok=True)
    copy2(exe_file, download_dir / exe_file.name)
    return str(exe_file)


if __name__ == "__main__":
    print(build_installer())
