"""
Standalone Nova demo server.

Runs the bridge + web chat UI without the TUI,
configured entirely from environment variables:

    NVIDIA_API_KEY   (required)
    NOVA_MODEL       (optional, default stepfun-ai/step-3.7-flash)
    PORT             (optional, default 8788)

Run:
    python serve_demo.py
"""

import os

import uvicorn

from bridge import nova_bridge


def main():
    api_key = os.environ.get("NVIDIA_API_KEY")

    if not api_key:
        raise SystemExit(
            "Set NVIDIA_API_KEY environment variable."
        )

    model_id = os.environ.get(
        "NOVA_MODEL",
        "stepfun-ai/step-3.7-flash",
    )

    nova_bridge.bridge_config = {
        "provider": "nvidia",
        "name": "NVIDIA NIM",
        "base_url": os.environ.get(
            "NOVA_BASE_URL",
            "https://integrate.api.nvidia.com/v1",
        ),
        "chat_endpoint": "/chat/completions",
        "api_key": api_key,
        "model_alias": "demo",
        "model_id": model_id,
        "model": {"id": model_id},
    }

    port = int(os.environ.get("PORT", "8788"))

    print(f"Nova demo serving on :{port}")

    uvicorn.run(
        nova_bridge.app,
        host="0.0.0.0",
        port=port,
        log_level="warning",
    )


if __name__ == "__main__":
    main()