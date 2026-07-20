from scripts.config import (
    get_preference,
    set_preference,
)

VALID = {
    "balanced",
    "speed",
    "quality",
    "coding",
    "reasoning",
    "vision",
}


def preference(mode=None):

    if mode is None:

        print("\nNova Preferences\n")

        print(f"Current : {get_preference()}")

        print("\nAvailable\n")

        for item in sorted(VALID):
            print(f"• {item}")

        return

    mode = mode.lower()

    if mode not in VALID:

        print(f"❌ Unknown preference: {mode}")

        return

    set_preference(mode)

    print(f"\n✓ Preference changed to {mode}\n")