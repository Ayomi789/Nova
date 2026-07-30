import re

from scripts.memory import all_memories


def retrieve(prompt):

    memories = all_memories()

    if not memories:
        return {}

    prompt = prompt.lower()

    words = set(
        re.findall(r"\w+", prompt)
    )

    results = {}

    for key, value in memories.items():

        key_words = set(
            re.findall(r"\w+", key.lower())
        )

        if words & key_words:

            results[key] = value

    return results