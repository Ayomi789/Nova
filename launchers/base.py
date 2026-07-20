from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """
    Base interface that every provider must implement.
    """

    @abstractmethod
    def launch(self, model):
        """Launch a model."""
        pass

    @abstractmethod
    def benchmark(self, model):
        """Benchmark a model."""
        pass

    @abstractmethod
    def health_check(self):
        """Verify provider connectivity."""
        pass