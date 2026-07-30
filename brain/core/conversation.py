from brain.core.pipeline import process

from brain.ui import (
    show_error,
    show_goodbye,
    show_memory,
    show_memory_cleared,
    show_reply,
)

from scripts.history import clear as clear_history


EXIT_COMMANDS = {"exit", "quit"}
CLEAR_COMMAND = "clear"


def chat_loop(client, conversation):
    """
    Main interactive chat loop.
    """

    while True:

        try:

            prompt = input("You > ").strip()

            if not prompt:
                continue

            command = prompt.lower()

            if command in EXIT_COMMANDS:
                show_goodbye()
                break

            if command == CLEAR_COMMAND:
                conversation.clear()
                clear_history()
                show_memory_cleared()
                continue

            response = process(
                client,
                conversation,
                prompt,
            )

            if response.get("handled"):
                show_reply(response["reply"])
                continue

            memory = response.get("memory_result")

            if memory:
                show_memory(memory)

            show_reply(response["reply"])

        except Exception as e:
            show_error(e)