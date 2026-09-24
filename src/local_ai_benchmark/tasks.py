import json
import re

from .models import Task


TASKS = [
    Task("dns_explanation", "general", "Explain DNS in exactly two short sentences.", "two_sentences"),
    Task("duplicate_files", "coding", "Write only a Python function named find_duplicate_files that accepts a list of paths and returns duplicate SHA256 groups.", "python_code"),
    Task("deterministic_math", "math", "What is 37 * 24? Answer with the number only.", "exact_888"),
    Task("json_profile", "json", 'Return only valid JSON matching this schema: {"name": string, "age": integer, "skills": array}. Use name "Ada", age 36, and skills ["python"].', "json_profile"),
    Task("spanish_summary", "spanish", "En español y en una sola frase, resume que la memoria RAM guarda datos temporalmente para que la CPU acceda a ellos rápidamente.", "spanish"),
]


def tasks_for(category: str | None = None) -> list[Task]:
    return [task for task in TASKS if category is None or task.category == category]


def validate(task: Task, output: str) -> bool | None:
    if task.validator == "exact_888":
        return re.search(r"\b888\b", output) is not None
    if task.validator == "two_sentences":
        return len([part for part in re.split(r"[.!?]+", output) if part.strip()]) == 2
    if task.validator == "json_profile":
        try:
            value = json.loads(output)
            return (value.get("name") == "Ada" and value.get("age") == 36
                    and value.get("skills") == ["python"])
        except (json.JSONDecodeError, AttributeError):
            return False
    if task.validator == "python_code":
        try:
            compile(output, "<model-output>", "exec")
            return "find_duplicate_files" in output
        except SyntaxError:
            return False
    if task.validator == "spanish":
        return any(word in output.lower() for word in ("memoria", "datos", "cpu"))
    return None
