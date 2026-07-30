from scripts.router import choose_model
from brain.memory.router_memory import record
from brain.routing.personas import load_persona
from brain.routing.racer import (
    build_model_list,
    race_models,
)


def run(
    client,
    conversation,
    prompt,
):
    decision = choose_model(prompt)

    persona = load_persona(
        decision["task"]
    )

    full_prompt = (
        f"{persona}\n\n{prompt}"
    )

    models = build_model_list(
        decision,
    )

    winner, reply = race_models(
        client,
        models,
        conversation,
        full_prompt,
    )

    record(
        decision["task"],
        winner["alias"],
    )
    
    
    return {
        "decision": decision,
        "winner": winner,
        "reply": reply,
    }