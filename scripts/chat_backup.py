from clients.nvidia import NvidiaClient

from scripts.config import load_models

from scripts.router import choose_model



def chat(args=None):

    models = load_models()["models"]

    client = NvidiaClient()


    print("\n💬 Nova Chat\n")

    print("🧠 Nova Brain Routing Enabled")

    print("Type 'exit' to leave.")
    print("Type 'clear' to clear memory.\n")


    conversation = []


    while True:

        prompt = input("You > ")


        if prompt.lower() in (
            "exit",
            "quit",
        ):

            print("\nGoodbye.\n")

            break


        if prompt.lower() == "clear":

            conversation = []

            print("\n🧹 Memory cleared.\n")

            continue



        try:

            decision = choose_model(prompt)


            selected = decision["model"]


            alias = selected["alias"]

            model_id = selected["id"]



            print()

            print("🧠 Nova Brain")

            print(
                f"Task    : {decision['task']}"
            )

            print(
                f"Model   : {alias}"
            )

            print(
                f"Score   : {selected['score']}"
            )

            print()



            conversation.append(
                {
                    "role": "user",
                    "content": prompt,
                }
            )


            reply = client.chat(
                model_id,
                conversation,
            )


            conversation.append(
                {
                    "role": "assistant",
                    "content": reply,
                }
            )


            print("Nova >")

            print(reply)

            print()



        except Exception as e:

            print()

            print(
                f"❌ {e}"
            )

            print()