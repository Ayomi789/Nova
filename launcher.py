
import os
import sys

from scripts.registry import COMMANDS
from scripts.config import load_settings, get_model
from scripts.checks import (
    check_python,
    check_claude,
    check_api_key,
)
from launchers.manager import get_provider


def _enable_utf8():
    if os.name == "nt":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleOutputCP(65001)
            kernel32.SetConsoleCP(65001)

        except Exception:
            pass

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


def status(label, success=True):
    icon = "✓" if success else "✗"
    print(f"  {icon} {label}")


def banner():
    print()
    print("        ███╗   ██╗ ██████╗ ██╗   ██╗ █████╗ ")
    print("        ████╗  ██║██╔═══██╗██║   ██║██╔══██╗")
    print("        ██╔██╗ ██║██║   ██║██║   ██║███████║")
    print("        ██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║")
    print("        ██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║")
    print("        ╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝")
    print()
    print("                    NOVA AGENT")
    print()
    print("        AI Coding Agent • NVIDIA NIM")
    print()
    print("  ──────────────────────────────────────────────")
    print()


def startup_checks():
    banner()

    if not check_python():
        status("Python detected", False)
        print()
        print("  Nova cannot continue without Python.")
        return False

    status("Python detected")

    if not check_claude():
        status("Agent engine detected", False)
        print()
        print("  Claude Code could not be found.")
        return False

    status("Agent engine detected")

    if not check_api_key():
        status("NVIDIA API key loaded", False)
        print()
        print("  NVIDIA_API_KEY is missing or invalid.")
        return False

    status("NVIDIA API key loaded")

    settings = load_settings()

    provider = get_provider()

    model = get_model(
        settings["default_model"]
    )

    print()
    print("  Provider  :", settings["provider"])
    print("  Model     :", settings["default_model"])
    print("  Backend   :", model["id"])
    print()

    status("Nova Brain ready")
    status("Model routing ready")
    status("NVIDIA NIM ready")
    status("Agent bridge ready")

    print()
    print("  ──────────────────────────────────────────────")
    print()
    print("  🚀 Starting Nova Agent...")
    print()

    provider.launch(model["id"])

    return True


def handle_commands():

    if len(sys.argv) <= 1:
        return False

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    handler = COMMANDS.get(command)

    if handler is None:
        print()
        print(f"Unknown command: {command}")
        print()
        print("Run 'nova --help' to see available commands.")
        return True

    handler(args)

    return True


def main():
    _enable_utf8()

    if handle_commands():
        return

    startup_checks()


if __name__ == "__main__":
    main()
