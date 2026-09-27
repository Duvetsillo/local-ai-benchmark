from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)


def build_installer() -> str:
    spec = ROOT / "aetherion_client.spec"
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        "Aetherion-Client",
        "--onefile",
        "--windowed",
        "--distpath",
        str(DIST),
        "--workpath",
        str(ROOT / "build" / "pyinstaller"),
        "--specpath",
        str(ROOT),
        "--add-data",
        str(ROOT / "src" / "local_ai_benchmark" / "web" / "index.html"),
        ".",
        str(ROOT / "src" / "local_ai_benchmark" / "client" / "desktop.py"),
    ]
    subprocess.run(command, check=False)
    exe_file = DIST / "Aetherion-Client.exe"
    if exe_file.exists():
        return str(exe_file)
    raise FileNotFoundError("Aetherion installer was not generated. The PyInstaller tool is required.")


if __name__ == "__main__":
    print(build_installer())
