from launchers.base import BaseProvider


class OllamaProvider(BaseProvider):

    def launch(self, model):
        raise NotImplementedError(
            "Ollama launcher not implemented."
        )

    def benchmark(self, model):
        raise NotImplementedError(
            "Benchmark engine not implemented yet."
        )

    def health_check(self):
        return True


provider = OllamaProvider()


def launch(model):
    return provider.launch(model)