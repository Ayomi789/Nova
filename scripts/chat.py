from clients.nvidia import NvidiaClient

from brain.core.conversation import chat_loop
from brain.ui import show_chat_banner

from scripts.personality import NOVA_SYSTEM


def chat(args=None):
    """
    Start a new Nova chat session.
    """

    client = NvidiaClient()

    show_chat_banner()

    conversation = [
        {
            "role": "system",
            "content": NOVA_SYSTEM,
        }
    ]

    chat_loop(
        client=client,
        conversation=conversation,
    )