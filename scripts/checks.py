import shutil
import subprocess
from scripts.config import load_secrets


def check_python():
    try:
        subprocess.run(
            ["python", "--version"],
            check=True,
            capture_output=True,
        )
        return True
    except Exception:
        return False


def check_claude():
    return (
        shutil.which("claude")
        or shutil.which("claude.cmd")
    ) is not None


def check_api_key():

    try:
        secrets = load_secrets()

        nvidia = secrets.get("nvidia", {})
        key = nvidia.get("api_key", "").strip()

        return key.startswith("nvapi-")

    except Exception:
        return False