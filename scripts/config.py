import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONFIG = ROOT / "config"


def load(filename):
    """Load a JSON configuration file."""
    with open(CONFIG / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def save(filename, data):
    """Save a JSON configuration file."""
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