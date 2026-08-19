import json
from pathlib import Path

from tools.base import Tool


class JsonTool(Tool):

    name = "json"

    description = (
        "Work with JSON: validate, pretty-print, minify, "
        "or query by dot-path. Accepts inline text or a "
        "file path."
    )

    def run(
        self,
        action,
        text=None,
        path=None,
        query=None,
    ):

        source = text

        if path:
            file = Path(path)

            if not file.exists():
                return f"File not found: {path}"

            source = file.read_text(encoding="utf-8")

        if not str(source or "").strip():
            return "No JSON provided (use text or path)."

        try:
            data = json.loads(source)
        except ValueError as exc:
            return f"Invalid JSON: {exc}"

        if action == "validate":
            return f"Valid JSON ({self._size_of(data)})."

        if action == "pretty":
            return json.dumps(data, indent=2, ensure_ascii=False)

        if action == "minify":
            return json.dumps(data, separators=(",", ":"), ensure_ascii=False)

        if action == "query":
            if not query:
                return json.dumps(data, indent=2, ensure_ascii=False)

            try:
                node = self._walk(data, query)
            except ValueError as exc:
                return f"Query failed: {exc}"

            return json.dumps(node, indent=2, ensure_ascii=False)

        raise ValueError(f"Unknown action: {action}")

    @staticmethod
    def _walk(node, path):
        for part in path.split("."):
            if not part:
                continue

            if isinstance(node, list):
                try:
                    node = node[int(part)]
                except (ValueError, IndexError):
                    raise ValueError(f"Bad list index: {part}")

            elif isinstance(node, dict):
                if part not in node:
                    raise ValueError(f"Missing key: {part}")

                node = node[part]

            else:
                raise ValueError(
                    f"Cannot descend into {type(node).__name__} at '{part}'"
                )

        return node

    @staticmethod
    def _size_of(data):
        if isinstance(data, list):
            return f"{len(data)} items"
        if isinstance(data, dict):
            return f"{len(data)} keys"

        return type(data).__name__
