from scripts.chat_command import handle as handle_chat_command
from scripts.memory_manager import process as process_memory
from scripts.memory import (
    remember,
    recall,
    forget,
)


def handle_memory(prompt):

    text = prompt.lower().strip()

    if text.startswith("remember "):

        body = prompt[9:].strip()

        if " is " in body:

            key, value = body.split(
                " is ",
                1,
            )

        elif "=" in body:

            key, value = body.split(
                "=",
                1,
            )

        else:

            return (
                True,
                "❌ Use: remember key is value",
            )

        remember(
            key.strip(),
            value.strip(),
        )

        return (
            True,
            f"✅ I'll remember {key.strip()}",
        )

    if text.startswith("forget "):

        key = prompt[7:].strip()

        forget(key)

        return (
            True,
            f"🗑️ Forgot {key}",
        )

    if text.startswith("what is "):

        key = prompt[8:].strip()

        value = recall(key)

        if value is not None:

            return (
                True,
                value,
            )

        return (
            False,
            None,
        )

    return (
        False,
        None,
    )


def preprocess(prompt):

    handled, reply = handle_chat_command(prompt)

    if handled:

        return {
            "handled": True,
            "reply": reply,
        }

    handled, reply = handle_memory(prompt)

    if handled:

        return {
            "handled": True,
            "reply": reply,
        }

    process_memory(prompt)

    return {
        "handled": False,
        "reply": None,
    }