from launchers.base import BaseProvider
from scripts.launcher import launch as launcher
from scripts.provider_config import load_provider



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


def launch(self, model=None):

    config = load_provider()

    return launcher(config["model_id"])