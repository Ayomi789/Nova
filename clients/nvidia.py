import json
import time
import statistics
import requests

from clients.base import BaseClient
from scripts.config import get_provider
from scripts.cleaner import clean_response


class NvidiaClient(BaseClient):

    def __init__(self):
        provider = get_provider("nvidia")
        self.provider = provider
        self.base_url = provider["base_url"].rstrip("/")
        self.api_key = provider["api_key"]
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _post(self, endpoint, payload, timeout=120, stream=False):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=timeout,
                stream=stream,
            )
        except requests.exceptions.Timeout:
            raise Exception("Request timed out")
        except requests.exceptions.ConnectionError:
            raise Exception("Unable to connect to NVIDIA")
        except requests.exceptions.RequestException as e:
            raise Exception(str(e))

        if response.status_code >= 400:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

        return response

    def _get(self, endpoint, timeout=60):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=timeout,
            )
        except requests.exceptions.Timeout:
            raise Exception("Request timed out")
        except requests.exceptions.ConnectionError:
            raise Exception("Unable to connect to NVIDIA")
        except requests.exceptions.RequestException as e:
            raise Exception(str(e))

        if response.status_code >= 400:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

        return response

    def _request(self, model):
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Say OK."}],
            "temperature": 0,
            "max_tokens": 5,
        }

        start = time.perf_counter()
        self._post("/chat/completions", payload, timeout=120)
        return round((time.perf_counter() - start) * 1000)

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

    def chat(
        self,
        model,
        messages,
        temperature=0.7,
        max_tokens=2048,
        timeout=300,
    ):
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = self._post(
            "/chat/completions",
            payload,
            timeout=timeout,
        )

        data = response.json()

        DEBUG = False
        
        if DEBUG:
            print("\n========== RAW RESPONSE ==========")
            print(json.dumps(data, indent=2))
            print("==================================\n")

        message = data["choices"][0]["message"]

        content = message.get("content")

        return clean_response(content)



    def stream_chat(self, model, messages, temperature=0.7, max_tokens=2048):
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        print("\n========== PAYLOAD ==========")

        print(json.dumps(payload, indent=2))

        print("=============================\n")
        
        
        
        response = self._post(
            "/chat/completions",
            payload,
            timeout=300,
            stream=True,
        )

        for line in response.iter_lines():
            if not line:
                continue

            line = line.decode("utf-8")

            if not line.startswith("data: "):
                continue

            line = line[6:]

            if line == "[DONE]":
                break

            try:
                chunk = json.loads(line)
                delta = chunk["choices"][0].get("delta", {}).get("content")
                if delta:
                    yield delta
            except Exception:
                continue

    def health(self):
        try:
            self.models()
            return True
        except Exception:
            return False

    def models(self):
        response = self._get("/models")
        return response.json()
