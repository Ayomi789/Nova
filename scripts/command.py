import json

from scripts.config import (
    load_models,
    load_settings,
    SETTINGS_FILE,
)


def models():
    data = load_models()

    print("\nAvailable Models\n")

    for alias, model in data["models"].items():
        print(f"{alias:<10} -> {model}")


def use(alias):

    models_data = load_models()["models"]

    if alias not in models_data:
        print(f"❌ Unknown model: {alias}")
        return

    settings = load_settings()

    settings["default_model"] = models_data[alias]

    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

    print("✅ Default model updated\n")
    print(f"Alias : {alias}")
    print(f"Model : {models_data[alias]}")