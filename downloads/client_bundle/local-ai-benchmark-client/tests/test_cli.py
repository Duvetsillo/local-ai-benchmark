import subprocess
import sys


def test_module_entrypoint_works():
    result = subprocess.run(
        [sys.executable, "-m", "local_ai_benchmark", "--help"],
        capture_output=True,
        text=True,
        cwd=".",
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()
