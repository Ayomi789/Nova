from scripts.config import load_models

from scripts.benchmark_stats import (
    average_latency,
    success_rate,
)


def compare(args):

    if len(args) < 2:

        print(
            "Usage: nova compare <model1> <model2>"
        )

        return


    models = load_models()["models"]


    for alias in args:


        if alias not in models:

            print(
                f"❌ Unknown model: {alias}"
            )

            continue


        model = models[alias]


        print()
        print("=" * 50)
        print(alias.upper())
        print("=" * 50)


        print(
            f"Model       : {model['id']}"
        )

        print(
            f"Provider    : {model['provider']}"
        )


        capabilities = model.get(
            "capabilities",
            []
        )


        if not capabilities:

            capabilities = model.get(
                "recommended_for",
                []
            )


        print(
            f"Capabilities: {', '.join(capabilities)}"
            if capabilities
            else "Capabilities: General"
        )


        print(
            f"Speed       : {model.get('speed','unknown')}"
        )


        latency = average_latency(alias)

        reliability = success_rate(alias)


        print()


        if latency is not None:

            print(
                f"Average     : {latency} ms"
            )

        else:

            print(
                "Average     : No data"
            )


        print(
            f"Success     : {reliability}%"
        )


        print()