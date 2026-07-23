from scripts.config import load_models

from scripts.brain import rank_models


TASKS = {
    "coding": "coding",
    "reasoning": "reasoning",
    "vision": "vision",
    "speed": "speed",
    "general": "general",
    "quality": "quality",
}


def recommend_model(task="general"):

    task = task.lower()

    if task not in TASKS:
        return None

    models = load_models()["models"]

    ranking = rank_models()

    candidates = []

    for item in ranking:

        alias = item["alias"]

        model = models.get(alias, {})

        recommended = model.get(
            "recommended_for",
            []
        )

        speed = model.get(
            "speed_class",
            ""
        )

        match = False


        if task in recommended:
            match = True


        if task == "speed":

            if speed in (
                "flash",
                "fast",
            ):
                match = True


        if task == "quality":

            if item["score"] >= 80:
                match = True


        if task == "general":

            if item["score"] >= 85:
                match = True


        if match:

            candidates.append(item)


    if not candidates:

        candidates = ranking


    if not candidates:

        return None


    return candidates[0]



def recommend(task="general"):

    task = task.lower()


    if task not in TASKS:

        print(f"❌ Unknown task: {task}")

        print("\nAvailable:\n")

        for item in TASKS:

            print(f"• {item}")

        return



    best = recommend_model(task)


    if best is None:

        print("❌ No recommendation available.")

        return



    models = load_models()["models"]

    info = models.get(
        best["alias"],
        {}
    )



    print("\n🧠 Nova Recommendation\n")


    print(
        f"Task        : {task}"
    )


    print(
        "\n🏆 Best Model\n"
    )


    print(
        f"Alias       : {best['alias']}"
    )


    print(
        f"Provider    : {best['provider']}"
    )


    print(
        f"Model ID    : {best['id']}"
    )


    print(
        f"Description : {info.get('description','')}"
    )


    print(
        "\nPerformance\n"
    )


    print(
        f"Nova Score  : {best['score']}"
    )


    if best.get("latency") is not None:

        print(
            f"Latency     : {best['latency']} ms"
        )

    else:

        print(
            "Latency     : No benchmark data"
        )


    print(
        f"Reliability : {best['reliability']}%"
    )


    print(
        f"Context     : {info.get('context',0):,}"
    )


    print(
        f"Speed Class : {info.get('speed_class','unknown')}"
    )


    print(
        "\nWhy this model?\n"
    )


    for reason in info.get(
        "recommended_for",
        []
    ):

        print(
            f"• {reason}"
        )


    print()