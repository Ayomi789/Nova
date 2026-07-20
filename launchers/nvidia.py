from launchers.base import BaseProvider
from scripts.launcher import launch as launcher


class NvidiaProvider(BaseProvider):

    def launch(self, model):
        return launcher(model)

    def benchmark(self, model):
        raise NotImplementedError(
            "Benchmark engine not implemented yet."
        )

    def health_check(self):
        return True


provider = NvidiaProvider()


def launch(model):
    """
    Backward compatibility.
    """
    return provider.launch(model)