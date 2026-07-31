from tools.registry import get


def execute(
    tool_name,
    **kwargs,
):
    tool = get(tool_name)

    if tool is None:
        raise ValueError(
            f"Unknown tool: {tool_name}"
        )

    return tool.run(**kwargs)