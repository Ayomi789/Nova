from scripts import memory as mem
from tools.base import Tool


class MemoryTool(Tool):

    name = "memory"

    description = (
        "Long-term key/value memory: remember, recall, "
        "forget, or list everything Nova knows."
    )

    def run(
        self,
        action,
        key=None,
        value=None,
    ):

        if action == "remember":
            if not key or value is None:
                raise ValueError("Remember requires key and value.")

            mem.remember(key, value)

            return f"Remembered '{key}'."

        if action == "recall":
            if not key:
                raise ValueError("Recall requires a key.")

            result = mem.recall(key)

            return (
                f"'{key}' = {result}"
                if result is not None
                else f"Nothing stored under '{key}'."
            )

        if action == "forget":
            if not key:
                raise ValueError("Forget requires a key.")

            mem.forget(key)

            return f"Forgot '{key}'."

        if action == "all":
            data = mem.all_memories()

            if not data:
                return "Memory is empty."

            return (
                "Stored memories:\n\n"
                + "\n".join(
                    f"- {k} = {v}" for k, v in data.items()
                )
            )

        raise ValueError(f"Unknown action: {action}")
