import json
import time
import statistics
import urllib.request
import urllib.error

from clients.base import BaseClient
from scripts.config import get_provider


class NvidiaClient(BaseClient):

    def __init__(self):

        self.provider = get_provider("nvidia")
        self.base_url = self.provider["base_url"]
        self.api_key = self.provider["api_key"]

    def _request(self, model):

        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": "Explain what you are in one short sentence."
                }
            ],
            "temperature": 0,
            "max_tokens": 50,
        }

        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        start = time.perf_counter()

        try:

            with urllib.request.urlopen(
                request,
                timeout=30
            ) as response:

                response.read()

            elapsed = round(
                (time.perf_counter() - start) * 1000
            )

            return elapsed

        except urllib.error.HTTPError as e:

            body = e.read().decode(
                "utf-8",
                errors="ignore"
            )

            raise Exception(
                f"HTTP {e.code}: {body}"
            )

        except urllib.error.URLError as e:

            raise Exception(
                f"Network Error: {e.reason}"
            )

        except Exception as e:

            raise Exception(str(e))

    def benchmark(self, model, runs=3):

        latencies = []
        successes = 0

        print()

        for i in range(runs):

            print(f"Run {i + 1}/{runs}...", end=" ")

            try:

                latency = self._request(model)

                latencies.append(latency)
                successes += 1

                print(f"{latency} ms")

            except Exception as e:

                print(f"FAILED ({e})")

        if not latencies:

            return {
                "success": False,
                "provider": "nvidia",
                "model": model,
                "runs": [],
                "average_ms": None,
                "median_ms": None,
                "best_ms": None,
                "worst_ms": None,
                "success_rate": 0,
            }

        return {
            "success": True,
            "provider": "nvidia",
            "model": model,
            "runs": latencies,
            "average_ms": round(statistics.mean(latencies)),
            "median_ms": round(statistics.median(latencies)),
            "best_ms": min(latencies),
            "worst_ms": max(latencies),
            "success_rate": round(successes / runs * 100),
        }

    def chat(self, model, messages):
        raise NotImplementedError

    def health(self):
        raise NotImplementedError

    def models(self):
        raise NotImplementedError