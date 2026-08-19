import re

from scripts.brain import rank_models
from scripts.config import load_models
from brain.memory.router_memory import get_score


GREETINGS = {
    "hi",
    "hello",
    "hey",
    "yo",
    "sup",
    "good morning",
    "good afternoon",
    "good evening",
}


TASK_KEYWORDS = {
    "coding": {
        "react": 10,
        "next": 10,
        "python": 10,
        "javascript": 9,
        "typescript": 9,
        "jwt": 10,
        "node": 9,
        "express": 9,
        "api": 8,
        "database": 8,
        "sql": 8,
        "mongodb": 8,
        "postgres": 8,
        "bug": 8,
        "debug": 9,
        "fix": 8,
        "code": 7,
        "build": 6,
        "create": 5,
        "function": 6,
    },
    "reasoning": {
        "why": 10,
        "explain": 10,
        "analyze": 9,
        "analysis": 9,
        "research": 9,
        "compare": 8,
        "strategy": 8,
        "plan": 7,
        "physics": 9,
        "quantum": 10,
        "math": 8,
        "algorithm": 8,
        "proof": 9,
    },
    "vision": {
        "image": 10,
        "photo": 10,
        "picture": 10,
        "design": 9,
        "ui": 9,
        "ux": 9,
        "figma": 8,
        "logo": 8,
        "draw": 8,
        "visual": 8,
    },
    "speed": {
        "2+2": 10,
        "calculate": 9,
        "quick": 5,
        "fast": 5,
        "brief": 4,
        "short": 3,
    },
}


def detect_task(prompt):

    clean = prompt.strip().lower()

    # Greeting detection
    if clean in GREETINGS:
        return {
            "task": "general_chat",
            "confidence": 100,
            "matches": ["greeting"],
            "scores": {},
        }

    normalized = (
        clean.replace(" ", "")
        .replace("-", "")
        .replace("_", "")
    )

    scores = {}
    matches = {}

    for task, keywords in TASK_KEYWORDS.items():

        total = 0
        found = []

        for keyword, weight in keywords.items():

            if " " in keyword:
                matched = keyword in clean
            else:

                matched = (
                    re.search(
                        rf"\b{re.escape(keyword)}\b",
                        clean,
                    )
                    is not None
                )

                if not matched:
                    matched = keyword in normalized

            if matched:
                total += weight
                found.append(keyword)

        scores[task] = total
        matches[task] = found

    highest = max(scores.values())

    if highest == 0:
        return {
            "task": "general",
            "confidence": 40,
            "matches": [],
            "scores": scores,
        }

    task = max(scores, key=scores.get)

    total = sum(scores.values())

    confidence = min(
        95,
        round(highest / total * 100),
    )

    return {
        "task": task,
        "confidence": confidence,
        "matches": matches[task],
        "scores": scores,
    }


def model_score(model, task):

    history = get_score(
        task,
        model["alias"],
    )

    latency = model.get("latency", 999999)

    if task == "speed":

        score = (
            max(0, 100 - latency / 100) * 0.70
            + model.get("reliability", 0) * 0.20
            + history * 0.10
        )

        return round(score, 2)

    score = (
        model.get(task, 0) * 0.45
        + model.get("score", 0) * 0.25
        + model.get("reliability", 0) * 0.15
        + max(0, 100 - latency / 100) * 0.05
        + history * 0.10
    )

    return round(score, 2)


def choose_model(prompt):

    detection = detect_task(prompt)

    task = detection["task"]

    # NEW:
    # Don't waste time ranking models for greetings.
    if task == "general_chat":

        ranking = rank_models()

        first = ranking[0]

        return {
            **detection,
            "model": {
                "alias": first["alias"],
                "id": first["id"],
                "provider": first["provider"],
                "score": first["score"],
            },
            "ranking": [],
        }

    models = load_models()["models"]

    ranking = rank_models()

    candidates = []

    for item in ranking:

        alias = item["alias"]

        merged = {
            **models.get(alias, {}),
            **item,
        }

        candidates.append({
            "alias": alias,
            "id": item["id"],
            "provider": item["provider"],
            "score": model_score(
                merged,
                task,
            ),
        })

    candidates.sort(
        key=lambda m: m["score"],
        reverse=True,
    )

    return {
        **detection,
        "model": candidates[0],
        "ranking": candidates,
    }