# from launchers.base import BaseProvider
# from scripts.launcher import launch as launcher
# from scripts.provider_config import load_provider


# class NvidiaProvider(BaseProvider):

#     def launch(self, model):
#         config = load_provider()

#         return launcher(
#             model,
#             config["api_key"],
#         )

#     def benchmark(self, model):
#         raise NotImplementedError(
#             "Benchmark engine not implemented yet."
#         )

#     def health_check(self):
#         return True


# provider = NvidiaProvider()


from launchers.base import BaseProvider
from bridge.nova_bridge import NovaBridge
from scripts.provider_config import load_provider


class NvidiaProvider(BaseProvider):

    def launch(self, model):
        config = load_provider()

        config["model_id"] = model

        NovaBridge().launch(config)

    def benchmark(self, model):
        raise NotImplementedError(
            "Benchmark engine not implemented yet."
        )

    def health_check(self):
        return True


provider = NvidiaProvider()