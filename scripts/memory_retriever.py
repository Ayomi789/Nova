from scripts.memory import all_memories


def retrieve(prompt):

    memories = all_memories()

    if not memories:
        return {}

    prompt = prompt.lower()

    results = {}

    keywords = {
        "language": [
            "language",
            "code",
            "coding",
            "programming",
            "rust",
            "python",
            "javascript",
            "typescript",
            "go",
        ],
        "color": [
            "color",
            "colour",
            "theme",
        ],
        "name": [
            "name",
            "call me",
            "who am i",
        ],
        "country": [
            "country",
            "where",
            "location",
            "live",
            "from",
        ],
    }

    for memory_key, value in memories.items():

        key = memory_key.lower()

        if key not in keywords:
            continue

        for word in keywords[key]:

            if word in prompt:

                results[memory_key] = value
                break

    return results