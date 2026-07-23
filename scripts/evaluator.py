import re


BAD_PHRASES = [
    "i don't know",
    "i do not know",
    "unable to",
    "cannot answer",
    "as an ai",
]


def evaluate(model, response, prompt=""):

    score = 0

    if response is None:
        return 0

    if not isinstance(response, str):
        return 0

    response = response.strip()

    if not response:
        return 0

    prompt = prompt.lower()
    text = response.lower()

    # -----------------------
    # Base
    # -----------------------

    score += 30

    # -----------------------
    # Length
    # -----------------------

    words = len(response.split())

    score += min(words / 10, 20)

    # -----------------------
    # Formatting
    # -----------------------

    if "##" in response:
        score += 6

    if "```" in response:
        score += 10

    score += min(response.count("- "), 8)

    score += min(
        len(re.findall(r"\n\d+\.", response)) * 2,
        8,
    )

    # -----------------------
    # Relevance
    # -----------------------

    prompt_words = {
        w
        for w in re.findall(r"[a-zA-Z]+", prompt)
        if len(w) > 3
    }

    matches = 0

    for word in prompt_words:
        if word in text:
            matches += 1

    score += min(matches * 2, 20)

    # -----------------------
    # Coding bonus
    # -----------------------

    coding_words = [
        "react",
        "python",
        "javascript",
        "typescript",
        "jwt",
        "api",
        "node",
        "express",
        "code",
    ]

    if any(word in prompt for word in coding_words):

        if "```" in response:
            score += 10

    # -----------------------
    # Penalize junk
    # -----------------------

    for phrase in BAD_PHRASES:

        if phrase in text:
            score -= 20

    if response.endswith("..."):
        score -= 8

    if words < 15:
        score -= 10

    # -----------------------
    # Reliability
    # -----------------------

    score += model.get(
        "reliability",
        0,
    ) * 0.1

    return round(max(score, 0), 2)