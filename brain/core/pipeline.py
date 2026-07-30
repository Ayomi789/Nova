from brain.core.context_builder import build_memory_context
from brain.routing.orchestrator import run
from brain.core.preprocessor import preprocess
from brain.memory.session import save_exchange
from scripts.memory_manager import process as process_memory
from brain.reflection.reflection import reflect
from brain.memory.reflection_memory import record as record_reflection



def process(client, conversation, prompt):

    preprocess_result = preprocess(prompt)

    if preprocess_result["handled"]:

        reply = preprocess_result["reply"]

        save_exchange(
            conversation,
            prompt,
            prompt,
            reply,
        )

        return {
            "handled": True,
            "reply": reply,
            "memory_result": None,
        }

    memory_result = process_memory(prompt)

    memory_context = build_memory_context(prompt)

    prompt_to_send = (
        f"{memory_context}\n\n{prompt}"
        if memory_context
        else prompt
    )

    pipeline_result = run(
        client,
        conversation,
        prompt_to_send,
    )

    reply = pipeline_result["reply"]

    reflection = reflect(
            prompt,
            reply,
        )
    
    
    record_reflection(
        pipeline_result["decision"]["task"],
        pipeline_result["winner"]["alias"],
        reflection,
    )
    
    
    
    save_exchange(
        conversation,
        prompt,
        prompt_to_send,
        reply,
    )

    return {
        "handled": False,
        "memory_result": memory_result,
        "reply": reply,
        "winner": pipeline_result["winner"],
        "decision": pipeline_result["decision"],
        "reflection": reflection,
    }