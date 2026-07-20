from scripts.config import load_models

from scripts.brain import (
    rank_models,
)


TASKS = {
    "coding": "coding",
    "reasoning": "reasoning",
    "vision": "vision",
    "speed": "speed",
    "general": "general",
    "quality": "quality",
}


def recommend(task="general"):

    task = task.lower()

    if task not in TASKS:

        print(f"❌ Unknown task: {task}")

        print("\nAvailable:")

        for item in TASKS:
            print(f"• {item}")

        return


    models = load_models()["models"]

    ranking = rank_models()


    candidates = []


    for item in ranking:

        alias = item["alias"]

        model = models[alias]


        recommended = model.get(
            "recommended_for",
            []
        )


        capabilities = model.get(
            "capabilities",
            []
        )


        speed = model.get(
            "speed",
            ""
        )


        match = False


        if task in recommended:

            match = True


        if task in capabilities:

            match = True


        if task == "speed" and speed == "fast":

            match = True


        if task == "quality":

            if item["score"] >= 80:

                match = True



        if match:

            candidates.append(
                item
            )


    if not candidates:

        candidates = ranking



    best = candidates[0]


    info = models[best["alias"]]


    print("\nRecommendation\n")


    print(
        f"Task         : {task}"
    )


    print(
        f"Model        : {best['alias']}"
    )


    print(
        f"Description  : {info.get('description','')}"
    )


    print(
        f"Provider     : {info.get('provider','unknown')}"
    )


    if best["latency"]:

        print(
            f"Avg Latency  : {best['latency']} ms"
        )


    print(
        f"Reliability  : {best['reliability']}%"
    )


    print(
        f"Nova Score   : {best['score']}"
    )