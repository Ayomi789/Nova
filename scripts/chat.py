from concurrent.futures import ThreadPoolExecutor, as_completed

from clients.nvidia import NvidiaClient
from scripts.router import choose_model
from scripts.evaluator import evaluate
from scripts.chat_command import handle as handle_chat_command
from scripts.personality import NOVA_SYSTEM

from scripts.history import (
    add as add_history,
    last,
    clear as clear_history,
)
from scripts.memory import (
    remember,
    recall,
    forget,
)


def get_fallbacks(decision):

    ranking = decision.get(
        "ranking",
        []
    )

    primary = decision["model"]["alias"]

    return [
        model
        for model in ranking
        if model["alias"] != primary
    ]


def build_model_list(decision):

    confidence = decision["confidence"]

    selected = decision["model"]

    if confidence >= 95:

        return [
            selected,
        ]

    if confidence >= 70:

        return [
            selected,
            *get_fallbacks(decision)[:1],
        ]

    return [
        selected,
        *get_fallbacks(decision)[:2],
    ]
    
    
    
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

        # Found in permanent memory
        if value is not None:

            return (
                True,
                value,
            )

        # Not in memory.
        # Let the LLM answer from conversation history.
        return (
            False,
            None,
        )

    return (
        False,
        None,
    )
    
    
    
def race_models(
    client,
    models,
    conversation,
    prompt,
):

    def ask(model):

        try:

            result = client.chat(
                model["id"],
                conversation,
                timeout=300,
            )

            return (
                model,
                result,
            )

        except Exception as e:

            print(
                f"❌ {model['alias']} failed: {e}"
            )

            return None

    responses = []

    with ThreadPoolExecutor(
        max_workers=len(models),
    ) as executor:

        futures = [
            executor.submit(
                ask,
                model,
            )
            for model in models
        ]

        for future in as_completed(futures):

            result = future.result()

            if result:

                responses.append(result)

    if not responses:

        raise Exception(
            "All models failed"
        )

    print("\n⚖️ Nova Judge\n")

    winner = None
    reply = None
    best_score = -1

    for model, result in responses:

        score = evaluate(
            model,
            result,
            prompt,
        )

        print(
            f"{model['alias']:<12} {score}"
        )

        if score > best_score:

            best_score = score
            winner = model
            reply = result

    print()

    print(
        f"🏆 Winner: {winner['alias']}"
    )

    return reply




def chat(args=None):

    client = NvidiaClient()

    print("\n💬 Nova Chat\n")
    print("🧠 Nova Brain Routing Enabled")
    print("Type 'exit' to leave.")
    print("Type 'clear' to clear memory.\n")

    conversation = [
            {
                "role": "system",
                "content": NOVA_SYSTEM,
            }
        ]

    conversation.extend(
            last(20)
        )
    
    while True:

        prompt = input("You > ").strip()

        handled, command_reply = handle_chat_command(prompt)

        if handled:

            print()

            print("Nova >")

            print(command_reply)

            print()

            continue

        if prompt.lower() in (
            "exit",
            "quit",
        ):

            print("\nGoodbye.\n")
            break

        if prompt.lower() == "clear":

            conversation.clear()

            clear_history()

            print("\n🧹 Memory cleared.\n")

            continue

        handled, memory_reply = handle_memory(prompt)

        if handled:

            add_history(
                "user",
                prompt,
            )

            add_history(
                "assistant",
                memory_reply,
            )

            print()

            print("Nova >")

            print(memory_reply)

            print()

            continue

        conversation.append(
            {
                "role": "user",
                "content": prompt,
            }
        )
        
        add_history(
            "user",
            prompt,
        )

        try:

            decision = choose_model(prompt)

            print()

            print("🧠 Nova Brain")

            print(
                f"Task       : {decision['task']}"
            )

            print(
                f"Confidence : {decision['confidence']}%"
            )

            print(
                f"Model      : {decision['model']['alias']}"
            )

            print()

            models = build_model_list(
                decision,
            )

            print(
                f"🚀 Racing {len(models)} models...\n"
            )

            reply = race_models(
                client,
                models,
                conversation,
                prompt,
            )

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

            print()

            print("Nova >")

            print(reply)

            print()

        except Exception as e:

            print()

            print(f"❌ {e}")

            print()