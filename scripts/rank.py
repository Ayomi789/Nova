from scripts.brain import rank_models
from scripts.config import get_preference


def rank(args=None):

    ranking = rank_models()

    print("\nNova Rankings\n")

    print(f"Preference : {get_preference()}")

    print()

    print(
        f"{'Rank':<6}"
        f"{'Model':<12}"
        f"{'Score':<8}"
        f"{'Avg(ms)':<10}"
        f"{'Success'}"
    )

    print("-" * 52)

    medals = ["🥇", "🥈", "🥉"]

    for index, model in enumerate(ranking, start=1):

        place = medals[index - 1] if index <= 3 else str(index)

        latency = (
            "-"
            if model["latency"] is None
            else model["latency"]
        )

        print(
            f"{place:<6}"
            f"{model['alias']:<12}"
            f"{model['score']:<8}"
            f"{str(latency):<10}"
            f"{model['reliability']}%"
        )