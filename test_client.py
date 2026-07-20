from pprint import pprint

from clients.nvidia import NvidiaClient
from scripts.config import get_model

client = NvidiaClient()

model = get_model("minimax")["id"]

result = client.benchmark(model)

print("\nResults\n")

pprint(result)