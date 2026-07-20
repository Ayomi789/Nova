import sys

from scripts.registry import COMMANDS

from scripts.config import (
    load_settings,
    get_model,
)

from scripts.checks import (
    check_python,
    check_claude,
    check_api_key,
)

from launchers.nvidia import launch as nvidia_launch
from launchers.openrouter import launch as openrouter_launch
from launchers.ollama import launch as ollama_launch


LAUNCHERS = {
    "nvidia": nvidia_launch,
    "openrouter": openrouter_launch,
    "ollama": ollama_launch,
}


def banner():
    print("=" * 50)
    print("               NOVA AI")
    print("=" * 50)


def handle_commands():

    if len(sys.argv) <= 1:
        return False

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    handler = COMMANDS.get(command)

    if handler is None:
        print(f"❌ Unknown command: {command}")
        return True

    handler(args)

    return True


def validate_environment():

    if not check_python():
        print("❌ Python not installed.")
        return False

    print("✅ Python detected")

    if not check_claude():
        print("❌ Claude Code not found.")
        return False

    print("✅ Claude Code detected")

    if not check_api_key():
        print("❌ NVIDIA API key missing.")
        return False

    print("✅ NVIDIA API key loaded")

    return True


def launch_provider():

    settings = load_settings()

    provider_name = settings["provider"]

    model_alias = settings["default_model"]

    model = get_model(model_alias)

    launcher = LAUNCHERS.get(provider_name)

    if launcher is None:
        print(f"❌ Unknown provider: {provider_name}")
        return

    print(f"✅ Provider : {provider_name}")
    print(f"✅ Alias    : {model_alias}")
    print(f"✅ Model    : {model['id']}")

    print("\n🚀 Launching Claude Code...\n")

    launcher(model["id"])


def main():

    banner()

    if handle_commands():
        return

    if not validate_environment():
        return

    launch_provider()


if __name__ == "__main__":
    main()