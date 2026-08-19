import json
from datetime import datetime
from pathlib import Path

from tools.base import Tool


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TASKS_FILE = DATA_DIR / "tasks.json"


def _load():
    if not TASKS_FILE.exists():
        return []

    try:
        return json.loads(TASKS_FILE.read_text(encoding="utf-8"))

    except Exception:
        return []


def _save(tasks):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    TASKS_FILE.write_text(
        json.dumps(tasks, indent=2),
        encoding="utf-8",
    )


class TaskTool(Tool):

    name = "tasks"

    description = (
        "Persistent task tracker: create, "
        "list, complete and delete tasks."
    )

    def run(
        self,
        action,
        **kwargs,
    ):

        tasks = _load()

        if action == "create":
            text = kwargs.get("text") or kwargs.get("title")

            if not text:
                raise ValueError("Create requires a text.")

            task = {
                "id": len(tasks) + 1,
                "text": text,
                "done": False,
                "created": datetime.now().isoformat(
                    timespec="seconds"
                ),
            }

            tasks.append(task)
            _save(tasks)

            return f"Created task #{task['id']}: {text}"

        if action == "list":
            if not tasks:
                return "No tasks."

            lines = []

            for task in tasks:
                mark = "[x]" if task.get("done") else "[ ]"
                lines.append(
                    f"{mark} #{task['id']} {task['text']}"
                )

            return "\n".join(lines)

        if action == "complete":
            task_id = int(kwargs.get("id") or 0)

            for task in tasks:
                if task["id"] == task_id:
                    task["done"] = True
                    _save(tasks)
                    return f"Completed task #{task_id}."

            return f"No task #{task_id}."

        if action == "delete":
            task_id = int(kwargs.get("id") or 0)
            before = len(tasks)

            tasks = [t for t in tasks if t["id"] != task_id]

            if len(tasks) == before:
                return f"No task #{task_id}."

            _save(tasks)
            return f"Deleted task #{task_id}."

        raise ValueError(f"Unknown action: {action}")