import json
from json import JSONDecodeError
from pathlib import Path

DATA_FILE = Path("data/router_stats.json")


def load():

    if not DATA_FILE.exists():
        return {}

    try:

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except JSONDecodeError:
        return {}


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


def record(task, model_alias):

    data = load()

    task_stats = data.setdefault(task, {})

    task_stats[model_alias] = (
        task_stats.get(model_alias, 0) + 1
    )

    save(data)


def get_score(task, model_alias):

    data = load()

    task_stats = data.get(task, {})

    if not task_stats:
        return 0

    total = sum(task_stats.values())

    if total == 0:
        return 0

    wins = task_stats.get(model_alias, 0)

    return round(
        (wins / total) * 100,
        2,
    )