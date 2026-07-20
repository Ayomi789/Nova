import json
from pathlib import Path

from scripts.config import (
    load_models,
    load_providers,
)


def average_latency(alias):

    benchmark_file = (
        Path(__file__).parent.parent
        / "cache"
        / "benchmark.json"
    )

    if not benchmark_file.exists():
        return None

    try:
        with open(benchmark_file, "r", encoding="utf-8") as f:
            history = json.load(f)
    except Exception:
        return None

    values = []

    for run in history:

        if alias in run["results"]:
            values.append(run["results"][alias])

    if not values:
        return None

    return sum(values) / len(values)


def recommend(task="general"):

    models = load_models()["models"]
    providers = load_providers()["providers"]

    candidates = []

    for alias, info in models.items():

        score = 0

        # Category
        if info["category"] == task:
            score += 50

        # Coding
        if task == "coding" and info["coding"]:
            score += 25

        # Vision
        if task == "vision" and info["vision"]:
            score += 25

        # Speed metadata
        if info["speed"] == "fast":
            score += 15
        elif info["speed"] == "medium":
            score += 8

        latency = average_latency(alias)

        if latency is not None:

            # Faster models earn more points
            score += max(0, 30 - latency / 30)

        candidates.append(
            {
                "alias": alias,
                "score": score,
                "latency": latency,
                "info": info,
            }
        )

    candidates.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    best = candidates[0]

    provider = providers[best["info"]["provider"]]["name"]

    print("\nRecommendation\n")

    print(f"Task        : {task}")
    print(f"Model       : {best['alias']}")
    print(f"Description : {best['info']['description']}")
    print(f"Provider    : {provider}")

    if best["latency"] is not None:
        print(f"Avg Latency : {best['latency']:.0f} ms")

    print(f"Score       : {best['score']:.1f}")