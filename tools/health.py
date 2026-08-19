import json
from pathlib import Path

from scripts.config import load_models
from tools.base import Tool


class HealthTool(Tool):

    name = "health"

    description = (
        "Report model health: overall overview or one "
        "model's status, latency and reliability."
    )

    HEALTH_FILE = (
        Path(__file__).resolve().parent.parent
        / "cache"
        / "model_health.json"
    )

    def _load_health(self):

        if not self.HEALTH_FILE.exists():
            return {}

        try:
            return json.loads(
                self.HEALTH_FILE.read_text(encoding="utf-8")
            )

        except Exception:
            return {}

    def run(
        self,
        action,
        alias=None,
    ):

        health = self._load_health()

        if action == "overview":
            models = load_models().get("models", {})

            if not models:
                return "No models configured."

            rows = []

            for name in sorted(models):
                info = health.get(name, {})

                if info:
                    rows.append(
                        f"- {name}: {info.get('status', 'unknown')} "
                        f"(latency {info.get('latency', '—')}ms, "
                        f"reliability {info.get('reliability', '—')})"
                    )
                else:
                    rows.append(f"- {name}: untested")

            online = sum(
                1
                for info in health.values()
                if info.get("status") == "healthy"
            )

            return (
                f"{len(models)} models · {online} healthy:\n\n"
                + "\n".join(rows)
            )

        if action == "model":
            if not alias:
                raise ValueError("Model requires an alias.")

            info = health.get(alias)

            if not info:
                return f"No health data for '{alias}'."

            return json.dumps(info, indent=2, ensure_ascii=False)

        raise ValueError(f"Unknown action: {action}")
