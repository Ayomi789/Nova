import os
import subprocess
import sys
import time



def launch(model,api_key):
    env = os.environ.copy()

    env["PYTHONUTF8"] = "1"
    env["DEFAULT_NVIDIA_MODEL"] = model
    env["NVIDIA_API_KEY"] = api_key
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
    except Exception as e:
        elapsed_ms = round(
            (time.perf_counter() - start) * 1000
        )
        return {
            "success": False,
            "model": model,
            "elapsed_ms": elapsed_ms,
            "error": str(e),
        }