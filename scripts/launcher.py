import os
import subprocess
import sys
import time


def launch(model):
    env = os.environ.copy()

    env["PYTHONUTF8"] = "1"
    env["DEFAULT_NVIDIA_MODEL"] = model

    start = time.perf_counter()

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

        elapsed_ms = round(
            (time.perf_counter() - start) * 1000
        )

        return {
            "success": True,
            "model": model,
            "elapsed_ms": elapsed_ms,
        }

    except subprocess.CalledProcessError as e:

        elapsed_ms = round(
            (time.perf_counter() - start) * 1000
        )

        print(
            f"\n❌ Nova failed to launch Claude Code "
            f"(exit code {e.returncode})"
        )

        return {
            "success": False,
            "model": model,
            "elapsed_ms": elapsed_ms,
            "exit_code": e.returncode,
        }