from abc import ABC, abstractmethod


class Tool(ABC):
    name = ""
    description = ""

    @abstractmethod
    def run(self, **kwargs):
        pass