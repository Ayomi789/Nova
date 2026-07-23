from abc import ABC, abstractmethod


class BaseBridge(ABC):
    """
    Base interface for every Nova bridge.
    """

    @abstractmethod
    def launch(self, config):
        """
        Launch Claude Code using the supplied provider config.
        """
        pass

    @abstractmethod
    def benchmark(self, config):
        """
        Benchmark the supplied provider.
        """
        pass

    @abstractmethod
    def health_check(self, config):
        """
        Verify the supplied provider.
        """
        pass