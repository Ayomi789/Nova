from scripts.config import load_models
from scripts.scoring import nova_score
from scripts.benchmark_stats import (
    average_latency,
    success_rate,
)


def rank_models():
    """
    Return all models ranked by Nova Score.
    """

    models = load_models()["models"]

    ranking = []

    for alias, model in models.items():

        ranking.append(
            {
                   "alias": alias,
                   "id": model["id"],
                   "provider": model["provider"],
                   "description": model["description"],
                   "strength": model["strength"],
                   "coding": model["coding"],
                   "reasoning": model["reasoning"],
                   "vision": model["vision"],
                   "speed_class": model["speed_class"],
                   "context": model["context"],
                   "recommended_for": model["recommended_for"],
                   "score": nova_score(alias),
                   "latency": average_latency(alias),
                   "reliability": success_rate(alias),
            }
)
    ranking.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return ranking


def best_model():
    """
    Return Nova's highest-ranked model.
    """

    ranking = rank_models()

    if not ranking:
        return None

    return ranking[0]


def model_rank(alias):
    """
    Return a model's position in the rankings.
    """

    ranking = rank_models()

    for index, model in enumerate(ranking, start=1):

        if model["alias"] == alias:
            return index

    return None


def explain(alias):
    """
    Return a simple explanation for the model.
    """

    ranking = rank_models()

    for model in ranking:

        if model["alias"] == alias:

            return {
                "rank": model_rank(alias),
                "score": model["score"],
                "latency": model["latency"],
                "reliability": model["reliability"],
                "description": model["description"],
            }

    return None