"""AETHERION desktop client package."""

from .core import ClientRunRecord, generate_run_id
from .hardware import detect_hardware
from .storage import LocalResultStore

__version__ = "0.1.0"

__all__ = [
    "ClientRunRecord",
    "LocalResultStore",
    "__version__",
    "detect_hardware",
    "generate_run_id",
]
