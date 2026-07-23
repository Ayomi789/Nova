from scripts.config import load_settings

from launchers.nvidia import provider as nvidia_provider
# from launchers.openrouter import provider as openrouter_provider
from launchers.ollama import provider as ollama_provider


PROVIDERS = {
    "nvidia": nvidia_provider,
    # "openrouter": openrouter_provider,
    "ollama": ollama_provider,
}


def get_provider(alias=None):
    """
    Return the active provider instance.
    """

    if alias is None:

        settings = load_settings()

        alias = settings["provider"]

    provider = PROVIDERS.get(alias)

    if provider is None:

        raise ValueError(
            f"Unknown provider: {alias}"
        )

    return provider


def available_providers():
    """
    Return every registered provider.
    """

    return PROVIDERS