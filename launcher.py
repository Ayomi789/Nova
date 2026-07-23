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

from launchers.manager import get_provider


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
        print(f"Unknown command: {command}")
        return True

    handler(args)
    return True


def startup_checks():

    banner()

    if check_python():
        print("✅ Python detected")
    else:
        print("❌ Python not detected")
        return False

    if check_claude():
        print("✅ Claude Code detected")
    else:
        print("❌ Claude Code not detected")
        return False

    if check_api_key():
        print("✅ API key loaded")
    else:
        print("❌ API key missing")
        return False

    settings = load_settings()

    provider = get_provider()

    model = get_model(
        settings["default_model"]
    )

    print(f"✅ Provider : {settings['provider']}")
    print(f"✅ Alias    : {settings['default_model']}")
    print(f"✅ Model    : {model['id']}")

    print()
    print("🚀 Launching Claude Code...")
    print()

    provider.launch(model["id"])

    return True


def main():

    if handle_commands():
        return

    startup_checks()


if __name__ == "__main__":
    main()