from pathlib import Path

from tools.base import Tool


class FilesystemTool(Tool):

    name = "filesystem"

    description = (
        "Read, write and inspect files."
    )

    def run(
        self,
        action,
        path=".",
        content=None,
        query=None,
    ):

        path = Path(path)

        if action == "read":

            if not path.exists():
                return f"File not found: {path}"

            if path.is_dir():
                return f"{path} is a directory."

            text = path.read_text(
                encoding="utf-8"
            )

            return (
                f"Contents of {path}:\n\n"
                f"{text}"
            )

        if action == "write":

            if path.is_dir():
                return (
                    "Cannot write to a directory. "
                    "Provide a file path."
                )

            path.write_text(
                content or "",
                encoding="utf-8",
            )

            return (
                f"Successfully wrote to {path}."
            )

        if action == "exists":

            if path.exists():
                return f"{path} exists."

            return f"{path} does not exist."

        if action == "list":

            if not path.exists():
                return f"Directory not found: {path}"

            files = sorted(
                file.name
                for file in path.iterdir()
            )

            if not files:
                return f"{path} is empty."

            return (
                f"Contents of {path}:\n\n"
                + "\n".join(files)
            )

        if action == "tree":

            if not path.exists():
                return f"Directory not found: {path}"

            files = sorted(
                str(file.relative_to(path))
                for file in path.rglob("*")
            )

            if not files:
                return f"{path} is empty."

            return (
                f"Tree for {path}:\n\n"
                + "\n".join(files)
            )

        if action == "search":

            if query is None:
                raise ValueError(
                    "Search requires query."
                )

            results = []

            for file in path.rglob("*"):

                if query.lower() in file.name.lower():

                    results.append(str(file))

            if not results:

                return (
                    f'No matches found for "{query}".'
                )

            return (
                f'Found {len(results)} match(es) for "{query}":\n\n'
                + "\n".join(results)
            )

        raise ValueError(
            f"Unknown action: {action}"
        )