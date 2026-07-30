from scripts.memory_retriever import retrieve


def build_memory_context(prompt):

    memories = retrieve(prompt)

    if not memories:
        return ""

    lines = [
        "IMPORTANT USER MEMORY:",
        "Only use these facts. Do not invent additional personal details.",
        "",
    ]

    for key, value in memories.items():

        lines.append(
            f"• {key.title()}: {value}"
        )

    return "\n".join(lines)