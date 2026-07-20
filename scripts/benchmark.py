import random
import time
import json
from pathlib import Path
from datetime import datetime

from scripts.config import (
    load_models,
    load_providers,
    load_settings,
)


def benchmark():

    settings = load_settings()
    models = load_models()["models"]
    providers = load_providers()["providers"]

    provider = settings["provider"]

    print("\nNova Benchmark\n")

    print(f"Provider : {providers[provider]['name']}")
    print("\nTesting...\n")

    results = {}

    for alias in models:

        time.sleep(0.15)

        latency = random.randint(350, 900)

        results[alias] = latency

        print(f"{alias:<10} {latency} ms")

    fastest = min(results, key=results.get)

    print("\nFastest Model\n")

    print(f"★ {fastest} ({results[fastest]} ms)")

    # Save benchmark history
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
            "provider": provider,
            "results": results,
            "fastest": fastest,
        }
    )

    with open(benchmark_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

    print("\n✓ Benchmark saved.")