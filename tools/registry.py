from tools.filesystem import FilesystemTool

TOOLS = {}


def register(tool):
    TOOLS[tool.name] = tool


register(FilesystemTool())


def get(name):
    return TOOLS.get(name)


def all():
    return TOOLS