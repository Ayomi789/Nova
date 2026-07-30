from pathlib import Path

PERSONA_DIR = (
    Path(__file__).resolve().parent.parent
    / "personas"
)

def load_persona(task: str) -> str:
    path = PERSONA_DIR / f"{task}.md"

    if not path.exists():
        path = PERSONA_DIR / "general.md"

    return path.read_text(
        encoding="utf-8"
    ).strip()