from scripts import brain as nova_brain
from scripts.router import choose_model
from tools.base import Tool


class RouterTool(Tool):

    name = "router"

    description = (
        "Ask Nova's router brain which model it would "
        "recommend for a prompt, or inspect model ranks."
    )

    def run(
        self,
        action,
        prompt=None,
        n=3,
        alias=None,
    ):

        if action == "recommend":
            if not prompt:
                raise ValueError("Recommend requires a prompt.")

            decision = choose_model(prompt)

            model = decision.get("model", {})

            return (
                f"Task: {decision.get('task')} "
                f"(confidence {decision.get('confidence')}%)\n"
                f"Recommended model: {model.get('alias')} "
                f"({model.get('id')})\n"
                f"Provider: {model.get('provider')} · "
                f"score {model.get('score')}"
            )

        if action == "top":
            ranking = nova_brain.rank_models()

            if not ranking:
                return "No models configured."

            count = max(1, min(int(n), 20))

            lines = []

            for index, item in enumerate(
                ranking[:count],
                start=1,
            ):
                lines.append(
                    f"{index}. {item['alias']} "
                    f"({item['id']}) score {item['score']}"
                )

            return "\n".join(lines)

        if action == "explain":
            if not alias:
                raise ValueError("Explain requires an alias.")

            info = nova_brain.explain(alias)

            if not info:
                return f"Unknown model: {alias}"

            return (
                f"{alias}: rank #{info['rank']} "
                f"(score {info['score']}, "
                f"latency {info['latency']}ms, "
                f"reliability {info['reliability']})\n"
                f"{info.get('description', '')}"
            )

        raise ValueError(f"Unknown action: {action}")
