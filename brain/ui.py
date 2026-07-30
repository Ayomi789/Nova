def show_chat_banner():

    print("\n💬 Nova Chat\n")
    print("🧠 Nova Brain Routing Enabled")
    print("Type 'exit' to leave.")
    print("Type 'clear' to clear memory.\n")


def show_reply(reply):

    print()
    print("Nova >")
    print(reply)
    print()


def show_memory(memory):

    print(
        f"\n🧠 Learned: {memory['key']} = {memory['value']}"
    )


def show_error(error):

    print()
    print(f"❌ {error}")
    print()


def show_goodbye():

    print("\nGoodbye.\n")


def show_memory_cleared():

    print("\n🧹 Memory cleared.\n")