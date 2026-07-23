import json
from pathlib import Path
from datetime import datetime

from clients.nvidia import NvidiaClient

from scripts.config import (
    load_models,
    load_providers,
    load_settings,
)


CACHE_DIR = Path(__file__).parent.parent / "cache"
BENCHMARK_FILE = CACHE_DIR / "benchmark.json"


def save_benchmark(data):

    CACHE_DIR.mkdir(exist_ok=True)

    history = []

    if BENCHMARK_FILE.exists():

        try:
            with open(
                BENCHMARK_FILE,
                "r",
                encoding="utf-8",
            ) as f:
                history = json.load(f)

        except Exception:
            history = []

    history.append(data)

    with open(
        BENCHMARK_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            history,
            f,
            indent=4,
        )


def benchmark(runs=3, warmup=True):

    settings = load_settings()

    provider_alias = settings["provider"]

    providers = load_providers()["providers"]
    models = load_models()["models"]

    print("\nNova Benchmark\n")

    print(
        f"Provider : {providers[provider_alias]['name']}"
    )

    print(
        f"Models   : {len(models)}"
    )

    print(
        f"Runs     : {runs}"
    )

    if warmup:
        print("Warm-up  : Enabled")

    print()

    if provider_alias != "nvidia":

        print(
            "Only NVIDIA provider is currently supported."
        )

        return

    # __init__ already loads provider configuration
    client = NvidiaClient()

    results = {}

    for alias, model in models.items():

        print("\n================================")
        print(f"Testing: {alias}")
        print(f"Model  : {model['id']}")
        print("================================")

        if warmup:

            try:

                client._request(model["id"])

                print("Warm-up completed")

            except Exception:

                print("Warm-up failed")

        result = client.benchmark(
            model["id"],
            runs=runs,
        )

        results[alias] = result

    fastest = None
    fastest_time = None

    for alias, result in results.items():

        latency = result.get("average_ms")

        if latency is None:
            continue

        if fastest_time is None or latency < fastest_time:

            fastest = alias
            fastest_time = latency

    record = {
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),
        "provider": provider_alias,
        "runs": runs,
        "warmup": warmup,
        "results": results,
        "fastest": fastest,
    }

    save_benchmark(record)

    print("\n\nBenchmark Complete\n")

    print("🏆 Fastest Model:")

    if fastest:

        print(
            f"{fastest} ({fastest_time} ms)"
        )

    else:

        print("No successful models")