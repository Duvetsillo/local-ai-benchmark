from local_ai_benchmark.tasks import TASKS, validate


def test_math_validator_is_deterministic():
    task = next(item for item in TASKS if item.name == "deterministic_math")
    assert validate(task, "888") is True
    assert validate(task, "889") is False


def test_json_validator_uses_real_parser():
    task = next(item for item in TASKS if item.name == "json_profile")
    assert validate(task, '{"name":"Ada","age":36,"skills":["python"]}') is True
    assert validate(task, "not json") is False
