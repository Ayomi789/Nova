import os
import subprocess
import threading
import time
import json

import requests
import uvicorn

from fastapi import FastAPI, Request

from bridge.base import BaseBridge


app = FastAPI(title="Nova Bridge")

bridge_config = {}


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Nova Bridge"
    }


@app.get("/healthz")
async def health():
    return {
        "status": "healthy"
    }


@app.post("/v1/messages")
async def messages(request: Request):

    data = await request.json()

    payload = {
        "model": bridge_config["model_id"],
        "messages": data.get("messages", []),
        "max_tokens": data.get("max_tokens", 4096),
    }

    headers = {
        "Authorization": f"Bearer {bridge_config['api_key']}",
        "Content-Type": "application/json",
    }

    print(">>> Forwarding request to OpenRouter")

    response = requests.post(
        bridge_config["base_url"] + bridge_config["chat_endpoint"],
        json=payload,
        headers=headers,
        timeout=120,
    )

    result = response.json()

    print("\n========== OPENROUTER RESPONSE ==========")
    print(json.dumps(result, indent=2))
    print("=========================================\n")


    if "choices" in result:

        choice = result["choices"][0]

        text = (
            choice.get("message", {})
            .get("content", "")
        )

        if not text:
            text = (
                choice.get("text")
                or "No response generated."
            )


        return {
            "id": "msg_nova",
            "type": "message",
            "role": "assistant",
            "model": bridge_config["model_id"],
            "content": [
                {
                    "type": "text",
                    "text": text
                }
            ],
            "stop_reason": "end_turn",
            "stop_sequence": None,
        }


    return {
        "id": "msg_nova_error",
        "type": "message",
        "role": "assistant",
        "model": bridge_config["model_id"],
        "content": [
            {
                "type": "text",
                "text": json.dumps(result)
            }
        ],
        "stop_reason": "end_turn",
        "stop_sequence": None,
    }



class NovaBridge(BaseBridge):

    def launch(self, config):

        global bridge_config

        bridge_config = config

        print(">>> NovaBridge.launch() CALLED")

        print("🚀 Nova Bridge Starting")
        print(f"Provider : {config['provider']}")
        print(f"Model    : {config['model_id']}")
        print("Endpoint : http://127.0.0.1:8788/v1/messages")


        server = threading.Thread(
            target=uvicorn.run,
            kwargs={
                "app": app,
                "host": "127.0.0.1",
                "port": 8788,
                "log_level": "info",
            },
            daemon=True,
        )


        print(">>> Starting Uvicorn thread")

        server.start()

        print(">>> Uvicorn thread started")


        time.sleep(2)


        env = os.environ.copy()


        env["ANTHROPIC_BASE_URL"] = (
            "http://127.0.0.1:8788"
        )

        env["ANTHROPIC_API_KEY"] = (
            "not-used"
        )


        env["ANTHROPIC_CUSTOM_MODEL_OPTION"] = (
            config["model_id"]
        )

        env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = (
            config["model_id"]
        )

        env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = (
            config["model_id"]
        )

        env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = (
            config["model_id"]
        )


        env["CLAUDE_CODE_SUBAGENT_MODEL"] = (
            config["model_id"]
        )

        env["CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS"] = (
            "1"
        )


        print(">>> Launching Claude Code")


        subprocess.run(
            [
                r"C:\Users\DELL\AppData\Roaming\npm\claude.cmd"
            ],
            env=env,
            check=True,
        )


        print(">>> Claude Code exited")


        return server



    def benchmark(self, config):

        raise NotImplementedError()



    def health_check(self, config):

        return True



if __name__ == "__main__":

    from scripts.provider_config import load_provider

    NovaBridge().launch(
        load_provider()
    )