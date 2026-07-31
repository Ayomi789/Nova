from pathlib import Path

from tools.base import Tool


class FilesystemTool(Tool):

    name = "filesystem"

    description = (
        "Read, write and inspect files"
    )

    def run(
        self,
        action,
        path,
        content=None,
    ):

        path = Path(path)

        if action == "read":
            return path.read_text(
                encoding="utf-8"
            )

        if action == "write":
            path.write_text(
                content,
                encoding="utf-8",
            )
            return "File saved."

        if action == "exists":
            return path.exists()

        if action == "list":
            return [
                file.name
                for file in path.iterdir()
            ]

        raise ValueError(
            f"Unknown action: {action}"
        )