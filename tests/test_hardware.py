from types import SimpleNamespace

import pytest

from local_ai_benchmark import hardware
from local_ai_benchmark.hardware import profile_hardware


def test_hardware_profile_is_serializable():
    profile = profile_hardware().to_dict()
    assert profile["os"]
    assert profile["architecture"]
    assert "cpu" in profile
    assert "ram" in profile
    assert isinstance(profile["gpus"], list)


@pytest.mark.parametrize("availability", ["missing", "empty", "unsupported", "os_error", "available"])
def test_hardware_profile_with_optional_cpu_frequency(monkeypatch, availability):
    psutil = pytest.importorskip("psutil")
    monkeypatch.setattr(psutil, "cpu_count", lambda logical: 8 if logical else 4)
    monkeypatch.setattr(hardware, "_nvidia_gpus", lambda: [])
    calls = []

    def read_frequency():
        calls.append(True)
        if availability == "unsupported":
            raise NotImplementedError("CPU frequency is not supported")
        if availability == "os_error":
            raise OSError("CPU frequency is unavailable")
        return SimpleNamespace(current=2400.0) if availability == "available" else None

    if availability == "missing":
        monkeypatch.delattr(psutil, "cpu_freq", raising=False)
    else:
        monkeypatch.setattr(psutil, "cpu_freq", read_frequency, raising=False)

    profile = profile_hardware().to_dict()
    assert profile["cpu"]["cores"] == 4
    assert profile["cpu"]["threads"] == 8
    assert profile["cpu"]["frequency_mhz"] == (2400.0 if availability == "available" else None)
    assert len(calls) == (0 if availability == "missing" else 1)
    assert profile["ram"]["total_bytes"] is not None
