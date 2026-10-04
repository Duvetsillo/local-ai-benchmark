"""Native desktop entrypoint (also usable as a PyInstaller script)."""

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from local_ai_benchmark.client.qt.app import launch_desktop_app

if __name__ == "__main__":
    launch_desktop_app()
