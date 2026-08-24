from brain.core.context_builder import build_memory_context
from brain.routing.orchestrator import run
from brain.core.preprocessor import preprocess
from brain.memory.session import save_exchange
from scripts.memory_manager import process as process_memory
from brain.reflection.reflection import reflect
from brain.memory.reflection_memory import record as record_reflection
from brain.routing.tool_router import detect as detect_tool
from tools.executor import execute


def process(client, conversation, prompt, stream=False, on_start=None, on_token=None):

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

    tool_result = detect_tool(prompt)

    tool_output = None

    if tool_result.use_tool:
        tool_output = execute(
            tool_result.tool,
            action=tool_result.action,
            **tool_result.arguments,
        )

    if tool_output is not None:
        prompt_to_send += (
            "\n\n"
            "===== TOOL RESULT =====\n"
            f"Tool: {tool_result.tool}\n"
            f"Action: {tool_result.action}\n\n"
            f"{tool_output}\n"
            "===== END TOOL RESULT =====\n"
        )

    pipeline_result = run(
        client,
        conversation,
        prompt_to_send,
        stream=stream,
        on_start=on_start,
        on_token=on_token,
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
        "tool": tool_result,
        "tool_output": tool_output,
    }