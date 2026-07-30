from scripts.memory_detector import detect
from scripts.memory import remember


def process(prompt):

    result = detect(prompt)

    if not result["remember"]:
        return None

    remember(
        result["key"],
        result["value"],
    )

    return result