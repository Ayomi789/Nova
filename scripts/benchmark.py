import json
from pathlib import Path
from datetime import datetime

from clients.nvidia import NvidiaClient

from scripts.config import (
    load_models,
    load_providers,
    load_settings,
)


def benchmark(runs=3, warmup=True):

    settings = load_settings()

    provider_alias = settings["provider"]

    providers = load_providers()["providers"]
    models = load_models()["models"]

    print("\nNova Benchmark\n")
    print(f"Provider : {providers[provider_alias]['name']}")
    print(f"Runs     : {runs}")

    if warmup:
        print("Warm-up  : Enabled")

    print()

    if provider_alias != "nvidia":
        print("❌ Real benchmark currently supports only NVIDIA.")
        return

    client = NvidiaClient()

    benchmark_results = {}

    fastest_model = None
    fastest_latency = None

    for alias, info in models.items():

        print("=" * 50)
        print(f"Benchmarking {alias}")
        print("=" * 50)

        if warmup:

            print("\nWarm-up...", end=" ")

            try:
                client._request(info["id"])
                print("Done")
            except Exception:
                print("Skipped")

        result = client.benchmark(
            info["id"],
            runs=runs,
        )

        if not result["success"]:
            print("❌ Benchmark failed.\n")
            continue

        benchmark_results[alias] = result

        avg = result["average_ms"]

        print()
        print(f"Average      : {avg} ms")
        print(f"Median       : {result['median_ms']} ms")
        print(f"Best         : {result['best_ms']} ms")
        print(f"Worst        : {result['worst_ms']} ms")
        print(f"Success Rate : {result['success_rate']}%")
        print()

        if fastest_latency is None or avg < fastest_latency:
            fastest_latency = avg
            fastest_model = alias

    if not benchmark_results:
        print("❌ No successful benchmarks.")
        return

    print("=" * 50)
    print("Fastest Model")
    print("=" * 50)

    print(f"★ {fastest_model} ({fastest_latency} ms)")

    cache_dir = Path(__file__).parent.parent / "cache"
    cache_dir.mkdir(exist_ok=True)

    benchmark_file = cache_dir / "benchmark.json"

    try:
        with open(benchmark_file, "r", encoding="utf-8") as f:
            history = json.load(f)
    except Exception:
        history = []

    history.append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "provider": provider_alias,
            "runs": runs,
            "warmup": warmup,
            "results": benchmark_results,
            "fastest": fastest_model,
        }
    )

    with open(benchmark_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

    print("\n✓ Benchmark saved.")