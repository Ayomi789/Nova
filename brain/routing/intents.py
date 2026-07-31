from dataclasses import dataclass


@dataclass
class Intent:
    use_tool: bool
    tool: str | None = None
    action: str | None = None
    confidence: int = 0
    arguments: dict | None = None