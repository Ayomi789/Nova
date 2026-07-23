from scripts.history import last
from scripts.memory import all_memories
from scripts.config import load_models


def handle(prompt):

    command = prompt.strip().lower()

    if not command.startswith("/"):
        return False, None

    if command == "/help":
        return True, """
Available Commands

/help       Show this menu
/history    Show recent conversation
/memory     Show saved memories
/models     Show active models
/brain      Explain Nova Brain
/stats      Show Nova statistics
"""

    if command == "/history":
        history = last(20)

        if not history:
            return True, "📝 No conversation history."

        output = []
        output.append("📝 Recent Conversation\n")

        MAX_PREVIEW = 500
        i = 0

        while i < len(history):
            user = history[i]
            assistant = history[i + 1] if i + 1 < len(history) else None

            output.append("────────────────────────")

            if user["role"] == "user":
                text = user["content"].strip()
                output.append("👤 You")
                output.append(text)
                output.append("")

            if assistant and assistant["role"] == "assistant":
                text = assistant["content"].strip()

                if len(text) > MAX_PREVIEW:
                    text = text[:MAX_PREVIEW]
                    text = text.rsplit(" ", 1)[0]
                    text += "..."

                output.append("🤖 Nova")
                output.append(text)
                output.append("")

            i += 2

        return True, "\n".join(output)

    if command == "/memory":
        memories = all_memories()

        if not memories:
            return True, "🧠 No saved memories."

        output = []
        output.append("🧠 Saved Memories\n")
        output.append("────────────────────────")

        for key, value in memories.items():
            pretty_key = (
                key.replace("_", " ")
                .replace("-", " ")
                .title()
            )

            output.append(f"📌 {pretty_key:<20} {value}")
            output.append("")

        output.append("────────────────────────")
        output.append(f"Total Memories : {len(memories)}")

        return True, "\n".join(output)

    if command == "/models":
        models = load_models()["models"]

        output = []

        output.append("🤖 Active Models\n")

        output.append("────────────────────────")

        for alias, info in models.items():

            provider = info.get(
                "provider",
                "Unknown",
            )

            model_id = info.get(
                "id",
                "Unknown",
            )

            output.append(f"🟢 {alias.title()}")

            output.append(
                f"Provider : {provider}"
            )

            output.append(
                f"Model    : {model_id}"
            )

            output.append("")

        output.append("────────────────────────")

        output.append(
            "Nova Brain dynamically selects\n"
            "the best model for every task."
        )

        return True, "\n".join(output)

    if command == "/brain":
        return True, """
🧠 Nova Brain Pipeline

────────────────────────

1️⃣ Understand Prompt

↓

2️⃣ Detect Task
   • Coding
   • Reasoning
   • Writing
   • General

↓

3️⃣ Select Best Models

↓

4️⃣ Race Models

↓

5️⃣ Judge Responses

↓

6️⃣ Return Best Answer

────────────────────────

Brain Routing : Enabled
Model Racing  : Enabled
Judge         : Enabled
Memory        : Enabled
"""

    if command == "/stats":
        history = last(9999)
        memories = all_memories()

        user_messages = sum(
            1 for item in history
            if item["role"] == "user"
        )

        assistant_messages = sum(
            1 for item in history
            if item["role"] == "assistant"
        )

        return True, f"""
📊 Nova Statistics

────────────────────────
💬 User Messages      {user_messages}
🤖 Assistant Replies  {assistant_messages}
🧠 Saved Memories     {len(memories)}
📚 History Entries    {len(history)}

────────────────────────
Nova Status

🟢 Online
🧠 Brain Routing Enabled
⚖️ Multi-Model Judge Enabled
"""

    return False, None