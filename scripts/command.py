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

    current_model = settings["default_model"]

    print("\nAvailable Models\n")

    for alias, model in data["models"].items():
        marker = "★" if model == current_model else " "
        print(f"{marker} {alias:<10} -> {model}")


def providers():
    data = load_providers()
    settings = load_settings()

    current_provider = settings["provider"]

    print("\nAvailable Providers\n")

    for alias, provider in data["providers"].items():
        marker = "★" if alias == current_provider else " "
        print(f"{marker} {alias:<12} -> {provider['name']}")


def use(alias):

    models_data = load_models()["models"]

    if alias not in models_data:
        print(f"❌ Unknown model: {alias}")
        return

    settings = load_settings()

    settings["default_model"] = models_data[alias]

    save_settings(settings)

    print("✅ Default model updated\n")
    print(f"Alias : {alias}")
    print(f"Model : {models_data[alias]}")


def current():

    settings = load_settings()
    models_data = load_models()["models"]

    current_model = settings["default_model"]
    current_alias = "Unknown"

    for alias, model in models_data.items():
        if model == current_model:
            current_alias = alias
            break

    print("\nCurrent Configuration\n")

    print(f"Alias      : {current_alias}")
    print(f"Model      : {current_model}")
    print(f"Provider   : {settings['provider']}")
    print(f"Proxy Host : {settings['proxy_host']}")
    print(f"Proxy Port : {settings['proxy_port']}")


def doctor():

    settings = load_settings()
    models_data = load_models()

    print("\nNova Doctor\n")

    # Python
    print("Python")
    print("✓ Found" if check_python() else "✗ Not Found")

    # Claude Code
    print("\nClaude Code")
    print("✓ Found" if check_claude() else "✗ Not Found")

    # NVIDIA API
    print("\nNVIDIA API Key")
    print("✓ Loaded" if check_api_key() else "✗ Missing")

    # Configuration
    print("\nConfiguration")

    config_dir = Path(__file__).parent.parent / "config"

    for filename in (
        "settings.json",
        "models.json",
        "providers.json",
        "secrets.json",
    ):
        if (config_dir / filename).exists():
            print(f"✓ {filename}")
        else:
            print(f"✗ {filename}")

    # Current Model
    print("\nCurrent Model")

    current_model = settings["default_model"]
    current_alias = "Unknown"

    for alias, model in models_data["models"].items():
        if model == current_model:
            current_alias = alias
            break

    print(f"Provider : {settings['provider']}")
    print(f"Alias    : {current_alias}")
    print(f"Model    : {current_model}")

    # Proxy
    print("\nProxy")

    print(f"Host : {settings['proxy_host']}")
    print(f"Port : {settings['proxy_port']}")

    print("\n✓ Doctor completed successfully.")





def provider(alias=None):

    providers_data = load_providers()["providers"]
    settings = load_settings()

    # Show current provider
    if alias is None:

        current = settings["provider"]
        info = providers_data[current]

        print("\nCurrent Provider\n")

        print(f"Alias    : {current}")
        print(f"Name     : {info['name']}")
        print(f"Base URL : {info['base_url']}")

        return

    # Change provider
    if alias not in providers_data:
        print(f"❌ Unknown provider: {alias}")
        return

    settings["provider"] = alias

    save_settings(settings)

    print("✅ Provider updated\n")
    print(f"Provider : {providers_data[alias]['name']}")