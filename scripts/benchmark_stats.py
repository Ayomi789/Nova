import json
from pathlib import Path


CACHE_DIR = Path(__file__).parent.parent / "cache"
BENCHMARK_FILE = CACHE_DIR / "benchmark.json"


def load_history():

    if not BENCHMARK_FILE.exists():
        return []

    try:
        with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def model_history(alias):

    history = load_history()

    results = []

    for benchmark in history:

        models = benchmark.get("results", {})

        if alias not in models:
            continue

        value = models[alias]

        # Old benchmark format
        if isinstance(value, int):
            value = {
                "average_ms": value,
                "median_ms": value,
                "best_ms": value,
                "worst_ms": value,
                "success_rate": 100,
            }

        results.append(value)

    return results


def _collect(alias, key):

    values = []

    for item in model_history(alias):

        value = item.get(key)

        if value is not None:
            values.append(value)

    return values


def average_latency(alias):

    values = _collect(alias, "average_ms")

    if not values:
        return None

    return round(sum(values) / len(values))


def median_latency(alias):

    values = _collect(alias, "median_ms")

    if not values:
        return None

    return round(sum(values) / len(values))


def best_latency(alias):

    values = _collect(alias, "best_ms")

    if not values:
        return None

    return min(values)


def worst_latency(alias):

    values = _collect(alias, "worst_ms")

    if not values:
        return None

    return max(values)


def success_rate(alias):

    values = _collect(alias, "success_rate")

    if not values:
        return 0

    return round(sum(values) / len(values))