import json

from scripts import config as nova_config
from tools.base import Tool


class ConfigManagerTool(Tool):

    name = "config-manager"

    description = (
        "Inspect and adjust Nova's configuration: "
        "list config files, read a section or key, "
        "change a setting, or switch the preference mode."
    )

    SECTIONS = ("settings", "models", "providers")

    def run(
        self,
        action,
        section="settings",
        key=None,
        value=None,
        mode=None,
    ):

        if action == "list":
            files = sorted(
                path.name
                for path in nova_config.CONFIG.glob("*.json")
            )

            return (
                "Config files:\n\n"
                + ("\n".join(files) if files else "(none)")
            )

        if action == "get":
            if section not in self.SECTIONS:
                raise ValueError(f"Unknown section: {section}")

            if section == "settings":
                data = nova_config.load_settings()
            elif section == "models":
                data = nova_config.load_models()
            else:
                data = nova_config.load_providers()

            if key:
                data = data.get(key, "<not set>")

            return json.dumps(data, indent=2, ensure_ascii=False)

        if action == "prefer":
            if mode not in ("speed", "balanced", "deep"):
                raise ValueError(f"Unknown preference: {mode}")

            nova_config.set_preference(mode)

            return f"Preference set to '{mode}'."

        if action == "set":
            if section != "settings":
                raise ValueError(
                    "Only the 'settings' section can be modified."
                )

            if not key:
                raise ValueError("Set requires a key.")

            settings = nova_config.load_settings()

            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except ValueError:
                    pass

            settings[key] = value
            nova_config.save_settings(settings)

            return (
                f"settings.{key} = "
                f"{json.dumps(value, ensure_ascii=False)}"
            )

        raise ValueError(f"Unknown action: {action}")
