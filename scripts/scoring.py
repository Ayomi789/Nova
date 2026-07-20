from scripts.config import (
    load_models,
    get_preference,
)

from scripts.benchmark_stats import (
    average_latency,
    success_rate,
)


def capability_score(alias):
    """
    Returns a capability score based on the user's preference.
    """

    models = load_models()["models"]
    model = models[alias]

    preference = get_preference()

    if preference == "coding":
        return model["coding"]

    if preference == "reasoning":
        return model["reasoning"]

    if preference == "vision":
        return model["vision"]

    if preference == "speed":

        mapping = {
            "flash": 100,
            "fast": 90,
            "medium": 70,
            "slow": 50,
        }

        return mapping.get(
            model["speed_class"],
            70,
        )

    # balanced / quality
    return round(
        (
            model["coding"]
            + model["reasoning"]
            + model["vision"]
        ) / 3
    )


def speed_score(alias):

    latency = average_latency(alias)

    if latency is None:
        return 0

    if latency <= 500:
        return 100

    if latency <= 1000:
        return 95

    if latency <= 1500:
        return 90

    if latency <= 2500:
        return 80

    if latency <= 4000:
        return 70

    if latency <= 7000:
        return 60

    if latency <= 10000:
        return 45

    return 20


def nova_score(alias):

    models = load_models()["models"]

    model = models[alias]

    preference = get_preference()

    strength = model["strength"]

    capability = capability_score(alias)

    reliability = success_rate(alias)

    speed = speed_score(alias)

    if preference == "speed":

        score = (
            speed * 0.45
            + reliability * 0.20
            + strength * 0.20
            + capability * 0.15
        )

    elif preference == "quality":

        score = (
            strength * 0.45
            + capability * 0.30
            + reliability * 0.15
            + speed * 0.10
        )

    else:

        score = (
            strength * 0.35
            + capability * 0.25
            + reliability * 0.20
            + speed * 0.20
        )

    return round(score, 1)