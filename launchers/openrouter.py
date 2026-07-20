from launchers.base import BaseProvider


class OpenRouterProvider(BaseProvider):

    def launch(self, model):
        raise NotImplementedError(
            "OpenRouter launcher not implemented."
        )

    def benchmark(self, model):
        raise NotImplementedError(
            "Benchmark engine not implemented yet."
        )

    def health_check(self):
        return True


provider = OpenRouterProvider()


def launch(model):
    return provider.launch(model)