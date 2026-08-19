import importlib
import inspect
import pkgutil

from tools.base import Tool
from tools.filesystem import FilesystemTool
from tools.web import WebTool
from tools.shell import ShellTool
from tools.tasks import TaskTool
from tools.repo import RepoInspectorTool
from tools.config_manager import ConfigManagerTool
from tools.memory import MemoryTool
from tools.health import HealthTool
from tools.router import RouterTool
from tools.github import GithubTool
from tools.sqlite import SqliteTool
from tools.http import HttpTool
from tools.system import SystemTool
from tools.notify import NotifyTool
from tools.image import ImageTool
from tools.json import JsonTool
from tools.time import TimeTool


TOOLS = {}

EXCLUDED = {
    "base",
    "registry",
    "executor",
    "__init__",
}


def register(tool):

    if tool.name not in TOOLS:
        TOOLS[tool.name] = tool


# Built-ins are registered explicitly to keep a stable order;
# any other Tool subclass dropped into tools/*.py is discovered
# automatically by _discover() at startup.
register(FilesystemTool())
register(WebTool())
register(ShellTool())
register(TaskTool())
register(RepoInspectorTool())
register(ConfigManagerTool())
register(MemoryTool())
register(HealthTool())
register(RouterTool())
register(GithubTool())
register(SqliteTool())
register(HttpTool())
register(SystemTool())
register(NotifyTool())
register(ImageTool())
register(JsonTool())
register(TimeTool())


def _discover():

    import tools as tools_pkg

    for module_info in pkgutil.iter_modules(tools_pkg.__path__):

        name = module_info.name

        if name in EXCLUDED:
            continue

        module = importlib.import_module(
            f"tools.{name}"
        )

        for _, cls in inspect.getmembers(module, inspect.isclass):

            if (
                cls.__module__ == module.__name__
                and issubclass(cls, Tool)
                and cls is not Tool
            ):

                register(cls())


_discover()


def get(name):

    return TOOLS.get(name)


def all_tools():

    return list(TOOLS.values())