import re


def reflect(prompt, reply):

    score = 100
    feedback = []

    prompt = prompt.lower()
    reply = reply.strip()

    if not reply:
        return {
            "score": 0,
            "feedback": [
                "Empty response",
            ],
        }

    # ------------------------
    # Response length
    # ------------------------

    words = len(reply.split())

    if words < 20:
        score -= 30
        feedback.append("Response is very short")

    elif words < 50:
        score -= 10
        feedback.append("Response could be more detailed")

    else:
        feedback.append("Good response length")

    # ------------------------
    # Code requests
    # ------------------------

    coding_keywords = [
        "code",
        "python",
        "react",
        "typescript",
        "javascript",
        "next",
        "build",
        "implement",
    ]

    if any(word in prompt for word in coding_keywords):

        has_code = (
            "```" in reply
            or re.search(
                r"\b(def|class|function|const|let|import|return)\b",
                reply,
            )
        )

        if has_code:
            feedback.append("Includes code")
        else:
            score -= 35
            feedback.append("Missing code")

    # ------------------------
    # Explanation requests
    # ------------------------

    explain_keywords = [
        "why",
        "explain",
        "how",
        "compare",
        "analysis",
    ]

    if any(word in prompt for word in explain_keywords):

        if words < 80:
            score -= 15
            feedback.append("Explanation is too brief")
        else:
            feedback.append("Explanation is detailed")

    # ------------------------
    # Formatting
    # ------------------------

    if (
        "#" in reply
        or "-" in reply
        or "*" in reply
        or "1." in reply
    ):
        feedback.append("Well structured")
    else:
        score -= 5
        feedback.append("Could improve formatting")

    # ------------------------
    # Keyword relevance
    # ------------------------

    prompt_words = set(
        re.findall(r"\b[a-zA-Z]{4,}\b", prompt)
    )

    reply_lower = reply.lower()

    matched = sum(
        1
        for word in prompt_words
        if word in reply_lower
    )

    if prompt_words:

        relevance = matched / len(prompt_words)

        if relevance < 0.30:
            score -= 25
            feedback.append("Low keyword relevance")
        else:
            feedback.append("Relevant response")

    score = max(0, min(score, 100))

    return {
        "score": score,
        "feedback": feedback,
    }