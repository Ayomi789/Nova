import json
from pathlib import Path


MEMORY_FILE = (
    Path(__file__).resolve().parent.parent
    / "cache"
    / "memory.json"
)


def _load():

    if not MEMORY_FILE.exists():

        return {}

    try:

        with open(MEMORY_FILE, "r", encoding="utf-8") as f:

            return json.load(f)

    except Exception:

        return {}


def _save(data):

    MEMORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
        )


def remember(key, value):

    memory = _load()

    memory[key] = value

    _save(memory)


def recall(key):

    memory = _load()

    return memory.get(key)


def forget(key):

    memory = _load()

    if key in memory:

        del memory[key]

        _save(memory)


def all_memories():

    return _load()