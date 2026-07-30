from concurrent.futures import ThreadPoolExecutor, as_completed

from brain.routing.judge import evaluate


def get_fallbacks(decision):
    ranking = decision.get("ranking", [])
    primary = decision["model"]["alias"]

    return [
        model
        for model in ranking
        if model["alias"] != primary
    ]


def build_model_list(decision):
    confidence = decision["confidence"]
    selected = decision["model"]

    if confidence >= 70:
        return [
            selected,
            *get_fallbacks(decision)[:1],
        ]

    return [
        selected,
        *get_fallbacks(decision)[:2],
    ]


def race_models(client, models, conversation, prompt):

    def ask(model):
        try:
            messages = [
                *conversation,
                {
                    "role": "user",
                    "content": prompt,
                },
            ]

            reply = client.chat(
                model=model["id"],
                messages=messages,
                timeout=300,
            )

            return model, reply

        except Exception:
            return None

    responses = []

    with ThreadPoolExecutor(max_workers=len(models)) as executor:

        futures = [
            executor.submit(ask, model)
            for model in models
        ]

        for future in as_completed(futures):
            result = future.result()

            if result is not None:
                responses.append(result)

    if not responses:
        raise Exception("All models failed")

    winner = None
    best_reply = None
    best_score = -1

    for model, reply in responses:

        score = evaluate(
            model,
            reply,
            prompt,
        )

        if score > best_score:
            best_score = score
            winner = model
            best_reply = reply

    return winner, best_reply