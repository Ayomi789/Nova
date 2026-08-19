import subprocess

from tools.base import Tool


class RepoInspectorTool(Tool):

    name = "repo"

    description = (
        "Inspect the current git repository: "
        "status, recent log, diff stats or branches."
    )

    def run(
        self,
        action="status",
        n=5,
        path=".",
    ):

        if action == "status":
            return self._git(["status", "--short"])

        if action == "log":
            return self._git(
                ["log", "--oneline", f"-{max(1, min(int(n), 50))}"]
            )

        if action == "diff":
            return self._git(["diff", "--stat"])

        if action == "branch":
            return self._git(["branch", "-a"])

        raise ValueError(f"Unknown action: {action}")

    @staticmethod
    def _git(args):
        try:
            result = subprocess.run(
                ["git", *args],
                capture_output=True,
                text=True,
                timeout=20,
            )

        except (subprocess.TimeoutExpired, OSError) as exc:
            return f"Git failed: {exc}"

        output = (
            (result.stdout or "").strip()
            or (result.stderr or "").strip()
        )

        return output or "(no output)"