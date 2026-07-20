from abc import ABC, abstractmethod


class BaseClient(ABC):
    """
    Base class for all provider API clients.
    """

    @abstractmethod
    def benchmark(self, model):
        """Benchmark a model."""
        raise NotImplementedError

    @abstractmethod
    def chat(self, model, messages):
        """Send a chat completion request."""
        raise NotImplementedError

    @abstractmethod
    def health(self):
        """Check provider health."""
        raise NotImplementedError

    @abstractmethod
    def models(self):
        """Return available models."""
        raise NotImplementedError