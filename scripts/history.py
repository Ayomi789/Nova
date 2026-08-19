import json
from pathlib import Path


HISTORY_FILE = (
    Path(__file__).resolve().parent.parent
    / "cache"
    / "history.json"
)


def _load():

    if not HISTORY_FILE.exists():

        return []

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8",
        ) as f:

            return json.load(f)

    except Exception:

        return []


def _save(history):

    HISTORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            history,
            f,
            indent=4,
            ensure_ascii=False,
        )


def add(role, content):

    history = _load()

    history.append(
        {
            "role": role,
            "content": content,
        }
    )

    _save(history)


def all():

    return _load()


def clear():

    _save([])


def last(limit=20):

    history = _load()

    return history[-limit:]