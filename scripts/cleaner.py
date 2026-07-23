def clean_response(content):
    """
    Cleans model responses before they are shown to the user.
    """

    if not content:
        return "I couldn't generate a response."

    content = content.strip()

    # Remove leaked reasoning
    if "</think>" in content:
        content = content.split("</think>")[-1].strip()

    if "<think>" in content:
        content = content.split("<think>")[0].strip()

    return content