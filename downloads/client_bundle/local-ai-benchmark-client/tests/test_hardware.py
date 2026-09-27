from local_ai_benchmark.hardware import profile_hardware


def test_hardware_profile_is_serializable():
    profile = profile_hardware().to_dict()
    assert profile["os"]
    assert profile["architecture"]
    assert "cpu" in profile
    assert "ram" in profile
    assert isinstance(profile["gpus"], list)
