import os
import subprocess
import sys


def launch(model):
    env = os.environ.copy()

    env["PYTHONUTF8"] = "1"
    env["DEFAULT_NVIDIA_MODEL"] = model

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "nim_code",
                "code",
                "--model",
                model,
            ],
            env=env,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Nova failed to launch Claude Code (exit code {e.returncode})")