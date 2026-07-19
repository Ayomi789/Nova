import sys

from scripts.config import load_settings
from scripts.checks import (
    check_python,
    check_claude,
    check_api_key,
)
from scripts.launcher import launch
from scripts.command import (
    models,
    providers,
    provider,
    use,
    current,
    doctor,
)


def banner():
    print("=" * 50)
    print("               NOVA AI")
    print("=" * 50)


def main():
    banner()

    # Handle CLI commands
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "models":
            models()
            return

        if command == "providers":
            providers()
            return

        if command == "provider":
            if len(sys.argv) == 2:
                provider()
                return

            provider(sys.argv[2])
            return

        if command == "use":
            if len(sys.argv) < 3:
                print("Usage: nova use <model>")
                return

            use(sys.argv[2])
            return

        if command == "current":
            current()
            return

        if command == "doctor":
            doctor()
            return

        print(f"❌ Unknown command: {command}")
        return

    # Normal launcher
    if not check_python():
        print("❌ Python not installed.")
        return

    print("✅ Python detected")

    if not check_claude():
        print("❌ Claude Code not found.")
        return

    print("✅ Claude Code detected")

    if not check_api_key():
        print("❌ NVIDIA API key missing.")
        return

    print("✅ NVIDIA API key loaded")

    settings = load_settings()

    model = settings["default_model"]

    print(f"✅ Selected model: {model}")

    print("\n🚀 Launching Claude Code...\n")

    launch(model)


if __name__ == "__main__":
    main()