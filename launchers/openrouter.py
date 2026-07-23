from launchers.base import BaseProvider

from scripts.provider_config import load_provider

from bridge.nova_bridge import NovaBridge


class OpenRouterProvider(BaseProvider):

    def launch(self, model=None):

        config = load_provider()

        bridge = NovaBridge()

        return bridge.launch(config)


    def benchmark(self, model):

        raise NotImplementedError(
            "Benchmark engine not implemented yet."
        )


    def health_check(self):

        config = load_provider()

        bridge = NovaBridge()

        return bridge.health_check(config)



provider = OpenRouterProvider()


def launch(model=None):

    return provider.launch(model)