# import os
# import subprocess
# import threading
# import time
# import json

# import requests
# import uvicorn

# from fastapi import FastAPI, Request
# from fastapi.responses import StreamingResponse

# from bridge.base import BaseBridge


# app = FastAPI(title="Nova Bridge")
# bridge_config = {}


# @app.get("/")
# async def root():
#     return {
#         "status": "ok",
#         "service": "Nova Bridge"
#     }


# @app.get("/healthz")
# async def health():
#     return {
#         "status": "healthy"
#     }


# def convert_messages(messages):
#     out = []

#     for m in messages:
#         role = m.get("role")
#         content = m.get("content")

#         if role == "assistant" and isinstance(content, list):
#             text = ""
#             tool_calls = []

#             for block in content:
#                 if block.get("type") == "text":
#                     text += block.get("text", "")
#                 elif block.get("type") == "tool_use":
#                     tool_calls.append({
#                         "id": block.get("id"),
#                         "type": "function",
#                         "function": {
#                             "name": block.get("name"),
#                             "arguments": json.dumps(block.get("input", {})),
#                         },
#                     })

#             msg = {"role": "assistant"}

#             if text:
#                 msg["content"] = text

#             if tool_calls:
#                 msg["tool_calls"] = tool_calls

#             out.append(msg)

#         elif role == "user" and isinstance(content, list):
#             tool_results = [
#                 c for c in content
#                 if c.get("type") == "tool_result"
#             ]

#             text = "\n".join(
#                 c.get("text", "") for c in content
#                 if c.get("type") == "text"
#             )

#             for tr in tool_results:
#                 result = tr.get("content", "")

#                 if isinstance(result, list):
#                     result = json.dumps(result)

#                 out.append({
#                     "role": "tool",
#                     "tool_call_id": tr.get("tool_use_id"),
#                     "content": result,
#                 })

#             if text:
#                 out.append({"role": "user", "content": text})

#         else:
#             out.append({"role": role, "content": content})

#     return out


# def convert_tools(tools):
#     out = []

#     for t in tools or []:
#         if t.get("type") == "function":
#             fn = t.get("function", {})
#             out.append({
#                 "type": "function",
#                 "function": {
#                     "name": fn.get("name"),
#                     "description": fn.get("description", ""),
#                     "parameters": fn.get("parameters", {
#                         "type": "object",
#                         "properties": {},
#                     }),
#                 },
#             })

#     return out


# def build_assistant_blocks(choice):
#     msg = choice.get("message", {})
#     blocks = []

#     text = msg.get("content")

#     if text:
#         blocks.append({"type": "text", "text": text})

#     for tc in msg.get("tool_calls", []):
#         try:
#             fn_input = json.loads(
#                 tc["function"].get("arguments", "{}")
#             )
#         except (ValueError, TypeError):
#             fn_input = {}

#         blocks.append({
#             "type": "tool_use",
#             "id": tc.get("id") or f"toolu_{int(time.time())}",
#             "name": tc["function"]["name"],
#             "input": fn_input,
#         })

#     return blocks


# def sse(event, data):
#     return (
#         f"event: {event}\n"
#         f"data: {json.dumps(data)}\n\n"
#     )


# def generate_events(upstream):
#     usage = {"input_tokens": 0, "output_tokens": 0}
#     model = bridge_config["model_id"]

#     yield sse("message_start", {
#         "type": "message_start",
#         "message": {
#             "id": "msg_nova_stream",
#             "type": "message",
#             "role": "assistant",
#             "model": model,
#             "content": [],
#             "stop_reason": None,
#             "stop_sequence": None,
#             "usage": usage,
#         },
#     })

#     text_index = None
#     next_index = 0
#     tool_open = {}

#     for raw in upstream.iter_lines(decode_unicode=True):
#         if not raw or raw.startswith(":"):
#             continue

#         if not raw.startswith("data:"):
#             continue

#         payload = raw[5:].strip()

#         if payload == "[DONE]":
#             break

#         try:
#             obj = json.loads(payload)
#         except ValueError:
#             continue

#         for choice in obj.get("choices", []):
#             delta = choice.get("delta", {}) or {}

#             content = delta.get("content")

#             if content:
#                 if text_index is None:
#                     text_index = next_index
#                     next_index += 1

#                     yield sse("content_block_start", {
#                         "type": "content_block_start",
#                         "index": text_index,
#                         "content_block": {
#                             "type": "text",
#                             "text": "",
#                         },
#                     })

#                 yield sse("content_block_delta", {
#                     "type": "content_block_delta",
#                     "index": text_index,
#                     "delta": {
#                         "type": "text_delta",
#                         "text": content,
#                     },
#                 })

#             for tc in delta.get("tool_calls", []):
#                 t_key = tc.get("index", 0)
#                 fn = tc.get("function", {})
#                 t_id = tc.get("id")

#                 if t_key not in tool_open:
#                     tool_open[t_key] = {
#                         "id": t_id or f"toolu_{int(time.time())}",
#                         "name": fn.get("name") or "unknown",
#                         "index": next_index,
#                     }
#                     next_index += 1

#                     yield sse("content_block_start", {
#                         "type": "content_block_start",
#                         "index": tool_open[t_key]["index"],
#                         "content_block": {
#                             "type": "tool_use",
#                             "id": tool_open[t_key]["id"],
#                             "name": tool_open[t_key]["name"],
#                             "input": {},
#                         },
#                     })

#                 chunks = fn.get("arguments") or ""

#                 if chunks:
#                     yield sse("content_block_delta", {
#                         "type": "content_block_delta",
#                         "index": tool_open[t_key]["index"],
#                         "delta": {
#                             "type": "input_json_delta",
#                             "partial_json": chunks,
#                         },
#                     })

#             finish = choice.get("finish_reason")

#             if finish:
#                 if text_index is not None:
#                     yield sse("content_block_stop", {
#                         "type": "content_block_stop",
#                         "index": text_index,
#                     })

#                 for t_key in tool_open:
#                     yield sse("content_block_stop", {
#                         "type": "content_block_stop",
#                         "index": tool_open[t_key]["index"],
#                     })

#                 text_index = None
#                 tool_open.clear()

#     yield sse("message_delta", {
#         "type": "message_delta",
#         "delta": {
#             "stop_reason": "end_turn",
#             "stop_sequence": None,
#         },
#         "usage": usage,
#     })

#     yield sse("message_stop", {"type": "message_stop"})


# @app.post("/v1/messages")
# async def messages(request: Request):
#     data = await request.json()

#     if not bridge_config:
#         return {
#             "type": "error",
#             "error": {
#                 "type": "api_error",
#                 "message": "Bridge not configured. Call launch() first.",
#             },
#         }

#     headers = {
#         "Authorization": f"Bearer {bridge_config['api_key']}",
#         "Content-Type": "application/json",
#     }

#     payload = {
#         "model": bridge_config["model_id"],
#         "messages": convert_messages(data.get("messages", [])),
#         "max_tokens": data.get("max_tokens", 4096),
#         "stream": data.get("stream", False),
#     }

#     if data.get("system"):
#         payload["system"] = data["system"]

#     if data.get("tools"):
#         payload["tools"] = convert_tools(data["tools"])

#     try:
#         response = requests.post(
#             bridge_config["base_url"] + bridge_config["chat_endpoint"],
#             json=payload,
#             headers=headers,
#             timeout=120,
#             stream=True,
#         )
#     except requests.RequestException as e:
#         return {
#             "type": "error",
#             "error": {
#                 "type": "api_error",
#                 "message": str(e),
#             },
#         }

#     if response.status_code != 200:
#         try:
#             detail = response.json()
#         except ValueError:
#             detail = response.text

#         return {
#             "type": "error",
#             "error": {
#                 "type": "api_error",
#                 "message": f"Upstream {response.status_code}: {detail}",
#             },
#         }

#     if data.get("stream"):
#         return StreamingResponse(
#             generate_events(response),
#             media_type="text/event-stream",
#             headers={"Cache-Control": "no-cache"},
#         )

#     result = response.json()

#     if "choices" in result:
#         choice = result["choices"][0]

#         return {
#             "id": "msg_nova",
#             "type": "message",
#             "role": "assistant",
#             "model": bridge_config["model_id"],
#             "content": build_assistant_blocks(choice),
#             "stop_reason": "end_turn",
#             "stop_sequence": None,
#             "usage": {
#                 "input_tokens": 0,
#                 "output_tokens": 0,
#             },
#         }

#     return {
#         "type": "error",
#         "error": {
#             "type": "api_error",
#             "message": json.dumps(result),
#         },
#     }


# class NovaBridge(BaseBridge):

#     def launch(self, config):
#         global bridge_config

#         bridge_config = config

#         print("🚀 Nova Bridge Starting")
#         print(f"Provider : {config['provider']}")
#         print(f"Model    : {config['model_id']}")
#         print("Endpoint : http://127.0.0.1:8788/v1/messages")

#         server = threading.Thread(
#             target=uvicorn.run,
#             kwargs={
#                 "app": app,
#                 "host": "127.0.0.1",
#                 "port": 8788,
#                 "log_level": "warning",
#             },
#             daemon=True,
#         )

#         server.start()

#         time.sleep(2)

#         env = os.environ.copy()

#         env["ANTHROPIC_BASE_URL"] = "http://127.0.0.1:8788"
#         env["ANTHROPIC_API_KEY"] = "not-used"

#         env["ANTHROPIC_CUSTOM_MODEL_OPTION"] = config["model_id"]
#         env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = config["model_id"]
#         env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = config["model_id"]
#         env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = config["model_id"]
#         env["CLAUDE_CODE_SUBAGENT_MODEL"] = config["model_id"]
#         env["CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS"] = "1"

#         print(">>> Launching Claude Code")

#         subprocess.run(
#             [r"C:\Users\DELL\AppData\Roaming\npm\claude.cmd"],
#             env=env,
#             check=True,
#         )

#         print(">>> Claude Code exited")

#         return server

#     def benchmark(self, config):
#         raise NotImplementedError()

#     def health_check(self, config):
#         return True


# if __name__ == "__main__":
#     from scripts.provider_config import load_provider

#     NovaBridge().launch(
#         load_provider()
#     )



import os
import subprocess
import threading
import time
import json

import requests
import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

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


@app.get("/bridge")
async def bridge_info():
    return {
        "model_id": bridge_config.get("model_id"),
        "provider": bridge_config.get("provider"),
    }


@app.post("/shutdown")
async def shutdown():
    threading.Thread(target=_exit_later, daemon=True).start()

    return {"status": "shutting_down"}


def _exit_later():
    time.sleep(0.5)
    os._exit(0)


BRIDGE_URL = "http://127.0.0.1:8788"


def bridge_alive():
    try:
        return requests.get(
            f"{BRIDGE_URL}/healthz",
            timeout=1.0,
        ).status_code == 200

    except requests.RequestException:
        return False


def bridge_model():
    try:
        return requests.get(
            f"{BRIDGE_URL}/bridge",
            timeout=1.0,
        ).json().get("model_id")

    except (requests.RequestException, ValueError):
        return None


def stop_bridge():
    try:
        requests.post(f"{BRIDGE_URL}/shutdown", timeout=1.0)

    except requests.RequestException:
        pass

def convert_messages(messages):
    out = []

    for m in messages:
        role = m.get("role")
        content = m.get("content")

        if role == "assistant" and isinstance(content, list):
            text = ""
            tool_calls = []

            for block in content:
                if block.get("type") == "text":
                    text += block.get("text", "")
                elif block.get("type") == "tool_use":
                    tool_calls.append({
                        "id": block.get("id"),
                        "type": "function",
                        "function": {
                            "name": block.get("name"),
                            "arguments": json.dumps(block.get("input", {})),
                        },
                    })

            msg = {"role": "assistant"}

            if text:
                msg["content"] = text

            if tool_calls:
                msg["tool_calls"] = tool_calls

            out.append(msg)

        elif role == "user" and isinstance(content, list):
            tool_results = [
                c for c in content
                if c.get("type") == "tool_result"
            ]

            text = "\n".join(
                c.get("text", "") for c in content
                if c.get("type") == "text"
            )

            for tr in tool_results:
                result = tr.get("content", "")

                if isinstance(result, list):
                    result = json.dumps(result)

                out.append({
                    "role": "tool",
                    "tool_call_id": tr.get("tool_use_id"),
                    "content": result,
                })

            if text:
                out.append({"role": "user", "content": text})

        else:
            out.append({"role": role, "content": content})

    return out


def convert_tools(tools):
    out = []

    for t in tools or []:
        if t.get("type") == "function":
            fn = t.get("function", {})
            out.append({
                "type": "function",
                "function": {
                    "name": fn.get("name"),
                    "description": fn.get("description", ""),
                    "parameters": fn.get("parameters", {
                        "type": "object",
                        "properties": {},
                    }),
                },
            })

    return out


def build_assistant_blocks(choice):
    msg = choice.get("message", {})
    blocks = []

    text = msg.get("content")

    if text:
        blocks.append({"type": "text", "text": text})

    for tc in msg.get("tool_calls", []):
        try:
            fn_input = json.loads(
                tc["function"].get("arguments", "{}")
            )
        except (ValueError, TypeError):
            fn_input = {}

        blocks.append({
            "type": "tool_use",
            "id": tc.get("id") or f"toolu_{int(time.time())}",
            "name": tc["function"]["name"],
            "input": fn_input,
        })

    return blocks


def sse(event, data):
    return (
        f"event: {event}\n"
        f"data: {json.dumps(data)}\n\n"
    )


def generate_events(upstream):
    usage = {"input_tokens": 0, "output_tokens": 0}
    model = bridge_config["model_id"]

    yield sse("message_start", {
        "type": "message_start",
        "message": {
            "id": "msg_nova_stream",
            "type": "message",
            "role": "assistant",
            "model": model,
            "content": [],
            "stop_reason": None,
            "stop_sequence": None,
            "usage": usage,
        },
    })

    text_index = None
    next_index = 0
    tool_open = {}

    for raw in upstream.iter_lines(decode_unicode=True):
        if not raw or raw.startswith(":"):
            continue

        if not raw.startswith("data:"):
            continue

        payload = raw[5:].strip()

        if payload == "[DONE]":
            break

        try:
            obj = json.loads(payload)
        except ValueError:
            continue

        for choice in obj.get("choices", []):
            delta = choice.get("delta", {}) or {}

            content = delta.get("content")

            if content:
                if text_index is None:
                    text_index = next_index
                    next_index += 1

                    yield sse("content_block_start", {
                        "type": "content_block_start",
                        "index": text_index,
                        "content_block": {
                            "type": "text",
                            "text": "",
                        },
                    })

                yield sse("content_block_delta", {
                    "type": "content_block_delta",
                    "index": text_index,
                    "delta": {
                        "type": "text_delta",
                        "text": content,
                    },
                })

            for tc in delta.get("tool_calls", []):
                t_key = tc.get("index", 0)
                fn = tc.get("function", {})
                t_id = tc.get("id")

                if t_key not in tool_open:
                    tool_open[t_key] = {
                        "id": t_id or f"toolu_{int(time.time())}",
                        "name": fn.get("name") or "unknown",
                        "index": next_index,
                    }
                    next_index += 1

                    yield sse("content_block_start", {
                        "type": "content_block_start",
                        "index": tool_open[t_key]["index"],
                        "content_block": {
                            "type": "tool_use",
                            "id": tool_open[t_key]["id"],
                            "name": tool_open[t_key]["name"],
                            "input": {},
                        },
                    })

                chunks = fn.get("arguments") or ""

                if chunks:
                    yield sse("content_block_delta", {
                        "type": "content_block_delta",
                        "index": tool_open[t_key]["index"],
                        "delta": {
                            "type": "input_json_delta",
                            "partial_json": chunks,
                        },
                    })

            finish = choice.get("finish_reason")

            if finish:
                if text_index is not None:
                    yield sse("content_block_stop", {
                        "type": "content_block_stop",
                        "index": text_index,
                    })

                for t_key in tool_open:
                    yield sse("content_block_stop", {
                        "type": "content_block_stop",
                        "index": tool_open[t_key]["index"],
                    })

                text_index = None
                tool_open.clear()

    yield sse("message_delta", {
        "type": "message_delta",
        "delta": {
            "stop_reason": "end_turn",
            "stop_sequence": None,
        },
        "usage": usage,
    })

    yield sse("message_stop", {"type": "message_stop"})


@app.post("/v1/messages")
async def messages(request: Request):
    data = await request.json()

    if not bridge_config:
        return {
            "type": "error",
            "error": {
                "type": "api_error",
                "message": "Bridge not configured. Call launch() first.",
            },
        }

    headers = {
        "Authorization": f"Bearer {bridge_config['api_key']}",
        "Content-Type": "application/json",
    }

    messages = convert_messages(data.get("messages", []))

    if data.get("system"):
        messages.insert(
            0,
            {
                "role": "system",
                "content": data["system"],
            },
        )

    payload = {
        "model": bridge_config["model_id"],
        "messages": messages,
        "max_tokens": data.get("max_tokens", 4096),
        "stream": data.get("stream", False),
    }

    if data.get("tools"):
        payload["tools"] = convert_tools(data["tools"])

    try:
        response = requests.post(
            bridge_config["base_url"] + bridge_config["chat_endpoint"],
            json=payload,
            headers=headers,
            timeout=120,
            stream=True,
        )
    except requests.RequestException as e:
        return JSONResponse(
            status_code=502,
            content={
                "type": "error",
                "error": {
                    "type": "api_error",
                    "message": str(e),
                },
            },
        )

    response.encoding = "utf-8"

    if response.status_code != 200:
        try:
            detail = response.json()
        except ValueError:
            detail = response.text

        return JSONResponse(
            status_code=response.status_code,
            content={
                "type": "error",
                "error": {
                    "type": "api_error",
                    "message": f"Upstream {response.status_code}: {detail}",
                },
            },
        )

    if data.get("stream"):
        return StreamingResponse(
            generate_events(response),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    result = response.json()

    if "choices" in result:
        choice = result["choices"][0]

        return {
            "id": "msg_nova",
            "type": "message",
            "role": "assistant",
            "model": bridge_config["model_id"],
            "content": build_assistant_blocks(choice),
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": 0,
                "output_tokens": 0,
            },
        }

    return JSONResponse(
        status_code=502,
        content={
            "type": "error",
            "error": {
                "type": "api_error",
                "message": json.dumps(result),
            },
        },
    )


class NovaBridge(BaseBridge):

    def launch(self, config):
        global bridge_config

        bridge_config = config

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
                "log_level": "warning",
            },
            daemon=True,
        )

        server.start()

        time.sleep(2)

        env = os.environ.copy()

        env["ANTHROPIC_BASE_URL"] = "http://127.0.0.1:8788"
        env["ANTHROPIC_API_KEY"] = "not-used"

        env["ANTHROPIC_CUSTOM_MODEL_OPTION"] = config["model_id"]
        env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = config["model_id"]
        env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = config["model_id"]
        env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = config["model_id"]
        env["CLAUDE_CODE_SUBAGENT_MODEL"] = config["model_id"]
        env["CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS"] = "1"

        # print(">>> Launching Claude Code")

        # subprocess.run(
        #     [r"C:\Users\DELL\AppData\Roaming\npm\claude.cmd"],
        #     env=env,
        #     check=True,
        # )

        # print(">>> Claude Code exited")
        
        print(">>> Entering Nova Shell")

        from scripts.chat_ui import run_chat

        run_chat(config)

        print(">>> Nova Shell exited")

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