from scripts.config import (
    load_models,
    load_settings,
)

from scripts.benchmark_stats import (
    average_latency,
    success_rate,
)

from scripts.scoring import nova_score


def advisor(args=None):

    settings = load_settings()
    models = load_models()["models"]

    current_model = settings.get("default_model")

    alias = None
    model = None


    # Resolve alias
    for name, info in models.items():

        if (
            name == current_model
            or info.get("id") == current_model
        ):

            alias = name
            model = info
            break


    if model is None:

        print("\nCurrent model not found.")

        return


    latency = average_latency(alias)

    reliability = success_rate(alias)

    score = nova_score(alias)



    print("\nNova Advisor\n")


    print("=" * 50)
    print("Current Setup")
    print("=" * 50)


    print(
        f"Provider      : {model.get('provider','unknown')}"
    )

    print(
        f"Model         : {alias}"
    )

    print(
        f"Preference    : {settings.get('preference','balanced')}"
    )


    print("\n" + "=" * 50)
    print("Performance")
    print("=" * 50)


    print(
        f"Nova Score    : {score}"
    )

    print(
        f"Average       : {latency} ms"
    )

    print(
        f"Reliability   : {reliability}%"
    )



    print("\n" + "=" * 50)
    print("Capabilities")
    print("=" * 50)


    print(
        f"Strength      : {model.get('strength','N/A')}"
    )

    print(
        f"Coding        : {model.get('coding','N/A')}"
    )

    print(
        f"Reasoning     : {model.get('reasoning','N/A')}"
    )

    print(
        f"Vision        : {model.get('vision','N/A')}"
    )



    print("\n" + "=" * 50)
    print("Suggestions")
    print("=" * 50)


    if score >= 85:

        print(
            "Current model is a strong choice."
        )

    elif score >= 70:

        print(
            "Current model is acceptable, but alternatives may perform better."
        )

    else:

        print(
            "Consider testing another model."
        )


    if settings.get("preference") == "balanced":

        print(
            "Configuration mode: balanced."
        )

    else:

        print(
            f"Configuration mode: {settings.get('preference')}"
        )