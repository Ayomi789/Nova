from scripts.config import load_models
from scripts.brain import rank_models
import re



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

    "general": {}
}

def detect_task(prompt):

    prompt = prompt.lower()

    normalized = (
        prompt
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
    )

    scores = {}
    matches = {}

    for task, keywords in TASK_KEYWORDS.items():

        total = 0
        found = []

        for keyword, weight in keywords.items():

            phrase = " " in keyword

            if phrase:

                matched = keyword in prompt

            else:

                matched = (
                    re.search(
                        rf"\b{re.escape(keyword)}\b",
                        prompt,
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

    task = max(
        scores,
        key=scores.get,
    )

    highest = scores[task]

    if highest == 0:

        return {
            "task": "general",
            "confidence": 0,
            "matches": [],
            "scores": scores,
        }

    total_score = sum(scores.values())

    confidence = (
        round(highest / total_score * 100)
        if total_score
        else 100
    )

    return {
        "task": task,
        "confidence": confidence,
        "matches": matches[task],
        "scores": scores,
    }

def model_score(model, task):

    score = 0


    # Normal task scoring
    if task != "speed":

        score += model.get(
            task,
            0
        ) * 0.5


        score += model.get(
            "score",
            0
        ) * 0.3


        score += model.get(
            "reliability",
            0
        ) * 0.15


        latency = model.get(
            "latency"
        )

        if latency:

            speed_bonus = max(
                0,
                100 - latency / 100
            )

            score += speed_bonus * 0.05


    # Speed routing
    else:

        latency = model.get(
            "latency"
        )

        reliability = model.get(
            "reliability",
            0
        )


        if latency:

            # Lower latency = higher score
            score += max(
                0,
                100 - latency / 100
            ) * 0.75


        # keep reliable models preferred
        score += reliability * 0.25



    return round(
        score,
        2
    )
def choose_model(prompt):

    detection = detect_task(prompt)

    task = detection["task"]

    models = load_models()["models"]

    ranking = rank_models()

    candidates = []

    for item in ranking:

        alias = item["alias"]

        model = models.get(
            alias,
            {}
        )

        combined = {
            **model,
            **item,
        }

        candidates.append(
            {
                "alias": alias,
                "id": item["id"],
                "provider": item["provider"],
                "score": model_score(
                    combined,
                    task,
                ),
            }
        )

    candidates.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    return {

        "task": task,

        "confidence": detection["confidence"],

        "matches": detection["matches"],

        "scores": detection["scores"],

        "model": candidates[0],

        "ranking": candidates,

    }