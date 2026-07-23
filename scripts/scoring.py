from scripts.config import load_models

from scripts.benchmark_stats import (
    average_latency,
    success_rate,
)


def speed_score(alias):

    latency = average_latency(alias)

    if latency is None:
        return 50

    if latency <= 500:
        return 100

    if latency <= 1000:
        return 95

    if latency <= 2500:
        return 85

    if latency <= 5000:
        return 70

    if latency <= 10000:
        return 50

    return 30



def capability_score(model):

    return round(
        (
            model.get("coding", 0)
            +
            model.get("reasoning", 0)
            +
            model.get("vision", 0)
        )
        /
        3
    )



def nova_score(alias):

    models = load_models()["models"]

    model = models[alias]


    strength = model.get(
        "strength",
        0
    )

    capability = capability_score(
        model
    )

    reliability = success_rate(
        alias
    )

    speed = speed_score(
        alias
    )


    score = (
        strength * 0.35
        +
        capability * 0.25
        +
        reliability * 0.20
        +
        speed * 0.20
    )


    return round(
        score,
        1
    )