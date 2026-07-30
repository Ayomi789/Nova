from scripts.config import (
    load_models,
    load_providers,
    load_secrets,
    load_settings,
)


def load_provider():
    """
    Returns the currently selected provider with all
    information Nova needs.
    """

    settings = load_settings()

    providers = load_providers()["providers"]

    models = load_models()["models"]

    secrets = load_secrets()

    provider_alias = settings["provider"]

    model_alias = settings["default_model"]

    provider = providers[provider_alias]

    model = models[model_alias]

    api_key = (
        secrets.get(provider_alias, {})
        .get("api_key")
    )
    

    return {
        "provider": provider_alias,
        "name": provider["name"],
        "base_url": provider["base_url"],
        "chat_endpoint": provider["chat_endpoint"],
        "api_key": api_key,
        "model_alias": model_alias,
        "model_id": model["id"],
        "model": model,
    }