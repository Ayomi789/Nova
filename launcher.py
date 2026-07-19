from scripts.config import load_settings
from scripts.checks import (
    check_python,
    check_claude,
    check_api_key,
)
from scripts.launcher import launch


def banner():
    print("=" * 50)
    print("               NOVA AI")
    print("=" * 50)


def main():
    banner()

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