import re


MEMORY_PATTERNS = [
    (
        re.compile(
            r"my favorite (.+?) is (.+)",
            re.IGNORECASE,
        ),
        lambda m: (
            f"favorite {m.group(1).strip()}",
            m.group(2).strip(),
        ),
    ),
    (
        re.compile(
            r"my name is (.+)",
            re.IGNORECASE,
        ),
        lambda m: (
            "name",
            m.group(1).strip(),
        ),
    ),
    (
        re.compile(
            r"i(?: am|'m) from (.+)",
            re.IGNORECASE,
        ),
        lambda m: (
            "country",
            m.group(1).strip(),
        ),
    ),
    (
        re.compile(
            r"i prefer (.+)",
            re.IGNORECASE,
        ),
        lambda m: (
            "preference",
            m.group(1).strip(),
        ),
    ),
    (
        re.compile(
            r"i use (.+)",
            re.IGNORECASE,
        ),
        lambda m: (
            "tool",
            m.group(1).strip(),
        ),
    ),
]


def detect(prompt):

    text = prompt.strip()

    for pattern, parser in MEMORY_PATTERNS:

        match = pattern.fullmatch(text)

        if match:

            key, value = parser(match)

            return {
                "remember": True,
                "key": key,
                "value": value,
                "confidence": 95,
            }

    return {
        "remember": False,
        "key": None,
        "value": None,
        "confidence": 0,
    }