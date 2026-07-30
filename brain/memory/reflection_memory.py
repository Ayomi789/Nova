import json
from json import JSONDecodeError
from pathlib import Path
from datetime import datetime


DATA_FILE = Path("data/reflections.json")


def load():

    if not DATA_FILE.exists():
        return []

    try:

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except JSONDecodeError:
        return []


def save(data):

    DATA_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
        )


def record(
    task,
    model,
    reflection,
):

    data = load()

    data.append(
        {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "model": model,
            "score": reflection["score"],
            "feedback": reflection["feedback"],
        }
    )

    save(data)