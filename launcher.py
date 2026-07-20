import sys

from scripts.config import load_settings
from scripts.checks import (
    check_python,
    check_claude,
    check_api_key,
)

from scripts.command import (
    models,
    providers,
    provider,
    use,
    current,
    doctor,
    history,
)

from scripts.benchmark import benchmark
from scripts.recommend import recommend

from launchers.nvidia import launch as nvidia_launch
from launchers.openrouter import launch as openrouter_launch
from launchers.ollama import launch as ollama_launch


def banner():
    print("=" * 50)
    print("               NOVA AI")
    print("=" * 50)


LAUNCHERS = {
    "nvidia": nvidia_launch,
    "openrouter": openrouter_launch,
    "ollama": ollama_launch,
}


def handle_commands():

    if len(sys.argv) <= 1:
        return False

    command = sys.argv[1].lower()

    if command == "models":
        models()
        return True

    if command == "providers":
        providers()
        return True

    if command == "provider":

        if len(sys.argv) == 2:
            provider()
        else:
            provider(sys.argv[2])

        return True

    if command == "use":

        if len(sys.argv) < 3:
            print("Usage: nova use <model>")
        else:
            use(sys.argv[2])

        return True

    if command == "current":
        current()
        return True

    if command == "doctor":
        doctor()
        return True

    if command == "benchmark":
        benchmark()
        return True

    if command == "history":
        history()
        return True

    if command == "recommend":

        if len(sys.argv) == 2:
            recommend()
        else:
            recommend(sys.argv[2].lower())

        return True

    print(f"❌ Unknown command: {command}")
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
    model = settings["default_model"]

    print(f"✅ Provider: {provider_name}")
    print(f"✅ Selected model: {model}")

    print("\n🚀 Launching Claude Code...\n")

    launcher = LAUNCHERS.get(provider_name)

    if launcher is None:
        print(f"❌ Unknown provider: {provider_name}")
        return

    launcher(model)


def main():

    banner()

    if handle_commands():
        return

    if not validate_environment():
        return

    launch_provider()


if __name__ == "__main__":
    main()