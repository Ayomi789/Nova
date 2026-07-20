import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONFIG = ROOT / "config"


def load(filename):
    """
    Load a JSON configuration file.
    """
    with open(CONFIG / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def save(filename, data):
    """
    Save a JSON configuration file.
    """
    with open(CONFIG / filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_settings():
    return load("settings.json")


def save_settings(settings):
    save("settings.json", settings)


def load_models():
    return load("models.json")


def load_providers():
    return load("providers.json")


def load_secrets():
    return load("secrets.json")


def get_provider(alias):
    """
    Return provider configuration merged with secrets.
    """

    providers = load_providers()["providers"]
    secrets = load_secrets()

    if alias not in providers:
        raise ValueError(f"Unknown provider: {alias}")

    provider = providers[alias].copy()

    provider["api_key"] = (
        secrets.get(alias, {})
        .get("api_key", "")
    )

    return provider


def get_model(alias):
    """
    Return a model configuration.
    """

    models = load_models()["models"]

    if alias not in models:
        raise ValueError(f"Unknown model: {alias}")

    return models[alias]


def get_preference():
    """
    Return the user's preferred recommendation mode.
    """

    return load_settings().get("preference", "balanced")


def set_preference(mode):
    """
    Save the user's preferred recommendation mode.
    """

    settings = load_settings()

    settings["preference"] = mode

    save_settings(settings)