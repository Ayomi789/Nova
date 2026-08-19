import re
from brain.routing.intents import Intent

TOOL_PATTERNS = {
    "filesystem": {
        "read": [
            "read",
            "open",
            "show",
            "display",
        ],
        "write": [
            "write",
            "save",
            "create",
        ],
        "list": [
            "list",
            "directory",
            "files",
            "folders",
        ],
        "exists": [
            "exists",
            "exist",
            "check",
        ],
    }
}

def extract_path(prompt):

    match = re.search(
        r"([\w\-/\\.]+\.[a-zA-Z0-9]+)",
        prompt,
    )

    if match:
        return match.group(1)

    return None





def detect(prompt):

    original_prompt = prompt
    prompt = prompt.lower()

    for tool, actions in TOOL_PATTERNS.items():

        for action, words in actions.items():

            for word in words:

                if re.search(
                    rf"\b{re.escape(word)}\b",
                    prompt,
                ):
                    path = extract_path(original_prompt)

                    if path is None:
                        return Intent(
                            use_tool=False,
                            arguments={},
                        )

                    return Intent(
                        use_tool=True,
                        tool=tool,
                        action=action,
                        confidence=100,
                        arguments={"path": path},
                    )

    return Intent(
        use_tool=False,
        arguments={},
)