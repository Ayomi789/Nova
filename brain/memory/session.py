from scripts.history import add as add_history


def save_exchange(
    conversation,
    prompt,
    user_prompt,
    reply,
):

    conversation.append(
        {
            "role": "user",
            "content": user_prompt,
        }
    )

    add_history(
        "user",
        prompt,
    )

    if reply:

        conversation.append(
            {
                "role": "assistant",
                "content": reply,
            }
        )

        add_history(
            "assistant",
            reply,
        )