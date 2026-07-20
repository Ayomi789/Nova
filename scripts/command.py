import json
from pathlib import Path

from scripts.config import (
    load_models,
    load_providers,
    load_settings,
    save_settings,
)

from scripts.checks import (
    check_python,
    check_claude,
    check_api_key,
)


def models():

    data = load_models()
    settings = load_settings()

    current_model = settings.get("default_model")

    print("\nAvailable Models\n")

    for alias, info in data["models"].items():

        marker = "★" if (
            alias == current_model
            or info.get("id") == current_model
        ) else " "

        print(
            f"{marker} {alias:<10} -> {info['id']}"
        )


def providers():

    data = load_providers()
    settings = load_settings()

    current_provider = settings["provider"]

    print("\nAvailable Providers\n")

    for alias, provider in data["providers"].items():

        marker = "★" if alias == current_provider else " "

        print(
            f"{marker} {alias:<12} -> {provider['name']}"
        )


def use(alias):

    models_data = load_models()["models"]

    if alias not in models_data:

        print(f"❌ Unknown model: {alias}")
        return


    settings = load_settings()

    settings["default_model"] = alias

    save_settings(settings)


    print("✅ Default model updated\n")
    print(f"Alias : {alias}")
    print(f"Model : {models_data[alias]['id']}")


def current():

    settings = load_settings()
    models_data = load_models()["models"]
    providers_data = load_providers()["providers"]

    current_model = settings.get(
        "default_model"
    )


    current_alias = "Unknown"
    model_id = current_model


    for alias, info in models_data.items():

        if (
            alias == current_model
            or info.get("id") == current_model
        ):

            current_alias = alias
            model_id = info["id"]
            break


    provider_alias = settings["provider"]

    provider_name = providers_data[
        provider_alias
    ]["name"]


    print("\nCurrent Configuration\n")

    print(f"Alias      : {current_alias}")
    print(f"Model      : {model_id}")
    print(f"Provider   : {provider_name}")
    print(f"Proxy Host : {settings['proxy_host']}")
    print(f"Proxy Port : {settings['proxy_port']}")


def doctor():

    settings = load_settings()
    models_data = load_models()["models"]
    providers_data = load_providers()["providers"]


    print("\nNova Doctor\n")


    print("Python")
    print(
        "✓ Found"
        if check_python()
        else "✗ Not Found"
    )


    print("\nClaude Code")
    print(
        "✓ Found"
        if check_claude()
        else "✗ Not Found"
    )


    print("\nNVIDIA API Key")
    print(
        "✓ Loaded"
        if check_api_key()
        else "✗ Missing"
    )


    print("\nConfiguration")


    config_dir = (
        Path(__file__).parent.parent
        / "config"
    )


    for filename in (
        "settings.json",
        "models.json",
        "providers.json",
        "secrets.json",
    ):

        if (config_dir / filename).exists():

            print(
                f"✓ {filename}"
            )

        else:

            print(
                f"✗ {filename}"
            )


    current_model = settings.get(
        "default_model"
    )

    alias = "Unknown"
    model_id = current_model


    for name, info in models_data.items():

        if (
            name == current_model
            or info.get("id") == current_model
        ):

            alias = name
            model_id = info["id"]
            break


    provider_name = providers_data[
        settings["provider"]
    ]["name"]


    print("\nCurrent Model")

    print(
        f"Provider : {provider_name}"
    )

    print(
        f"Alias    : {alias}"
    )

    print(
        f"Model    : {model_id}"
    )


    print("\nProxy")

    print(
        f"Host : {settings['proxy_host']}"
    )

    print(
        f"Port : {settings['proxy_port']}"
    )


    print(
        "\n✓ Doctor completed successfully."
    )


def provider(alias=None):

    providers_data = load_providers()["providers"]
    settings = load_settings()


    if alias is None:

        current = settings["provider"]

        info = providers_data[current]


        print("\nCurrent Provider\n")

        print(
            f"Alias    : {current}"
        )

        print(
            f"Name     : {info['name']}"
        )

        print(
            f"Base URL : {info['base_url']}"
        )

        return


    if alias not in providers_data:

        print(
            f"❌ Unknown provider: {alias}"
        )

        return


    settings["provider"] = alias

    save_settings(settings)


    print(
        "✅ Provider updated\n"
    )

    print(
        f"Provider : {providers_data[alias]['name']}"
    )


def history():

    cache_dir = (
        Path(__file__).parent.parent
        / "cache"
    )

    benchmark_file = (
        cache_dir
        / "benchmark.json"
    )


    if not benchmark_file.exists():

        print(
            "\nNo benchmark history found."
        )

        return


    try:

        with open(
            benchmark_file,
            "r",
            encoding="utf-8"
        ) as f:

            history_data = json.load(f)


    except Exception as e:

        print(
            f"\nUnable to read benchmark history: {e}"
        )

        return


    if not history_data:

        print(
            "\nNo benchmark history found."
        )

        return


    providers = load_providers()["providers"]


    print(
        "\nBenchmark History\n"
    )


    for item in history_data:

        timestamp = item.get(
            "timestamp",
            "Unknown"
        )


        print(
            timestamp.replace(
                "T",
                " "
            )
        )


        provider_alias = item.get(
            "provider",
            "unknown"
        )


        provider_name = providers.get(
            provider_alias,
            {}
        ).get(
            "name",
            provider_alias
        )


        print(
            f"Provider : {provider_name}"
        )


        print(
            "\n🏆 Ranking"
        )


        results = item.get(
            "results",
            {}
        )


        ranking = []


        for model, data in results.items():


            latency = None


            if isinstance(data, dict):

                latency = data.get(
                    "average_ms"
                )


            elif isinstance(data, (int, float)):

                latency = data



            if latency is not None:

                ranking.append(
                    (
                        model,
                        latency
                    )
                )


        ranking.sort(
            key=lambda x: x[1]
        )


        if not ranking:

            print(
                "No valid benchmark data"
            )

        else:

            for index, (
                model,
                latency
            ) in enumerate(
                ranking,
                start=1
            ):

                print(
                    f"{index}. {model:<10} {latency} ms"
                )


        print()


    print(
        f"Total Benchmarks : {len(history_data)}"
    )