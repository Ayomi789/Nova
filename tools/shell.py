import subprocess

from tools.base import Tool


class ShellTool(Tool):

    name = "shell"

    description = (
        "Run a local shell command "
        "and return its combined output."
    )

    MAX_OUTPUT = 20000

    def run(
        self,
        action="run",
        command=None,
        timeout=30,
    ):

        if action != "run":
            raise ValueError(f"Unknown action: {action}")

        if not command or not command.strip():
            raise ValueError("Run requires a command.")

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

        except subprocess.TimeoutExpired:
            return f"Command timed out after {timeout}s."

        except OSError as exc:
            return f"Failed to run command: {exc}"

        output = (result.stdout or "") + (result.stderr or "")

        if len(output) > self.MAX_OUTPUT:
            output = output[: self.MAX_OUTPUT] + "\n…[truncated]"

        if not output.strip():
            return f"exit {result.returncode}"

        return f"exit {result.returncode}\n\n{output.strip()}"