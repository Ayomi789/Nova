import base64
import os
import struct
from pathlib import Path

import requests

from scripts.provider_config import load_provider
from tools.base import Tool


class ImageTool(Tool):

    name = "image"

    description = (
        "Inspect image files (format, dimensions, size) "
        "or analyze their content with Nova's vision models."
    )

    MAX_DESCRIBE_BYTES = 4 * 1024 * 1024

    MIME = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
        ".webp": "image/webp",
    }

    def run(
        self,
        action,
        path=None,
        prompt="Describe this image in detail.",
    ):

        if not path:
            raise ValueError("A path is required.")

        image = Path(path)

        if not image.exists():
            return f"File not found: {path}"

        if action == "info":
            size = image.stat().st_size
            fmt, width, height = self._dimensions(image)

            return (
                f"{image.name} · {self._fmt_size(size)}\n"
                f"Format: {fmt} · {width}x{height}"
            )

        if action == "describe":
            size = image.stat().st_size

            if size > self.MAX_DESCRIBE_BYTES:
                return (
                    f"Image is {self._fmt_size(size)}; "
                    f"describe is limited to 4 MB."
                )

            try:
                provider = load_provider()
            except Exception as exc:
                return f"Cannot load provider config: {exc}"

            api_key = provider.get("api_key")

            if not api_key:
                return "No API key is configured."

            mime = self.MIME.get(image.suffix.lower(), "application/octet-stream")
            data = base64.b64encode(image.read_bytes()).decode("ascii")

            payload = {
                "model": provider["model_id"],
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime};base64,{data}"
                                },
                            },
                        ],
                    }
                ],
                "max_tokens": 512,
            }

            url = (
                provider["base_url"].rstrip("/")
                + provider["chat_endpoint"]
            )

            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=60,
                )
            except requests.RequestException as exc:
                return f"Vision request failed: {exc}"

            if response.status_code != 200:
                return (
                    f"Vision HTTP {response.status_code}: "
                    f"{response.text[:500]}"
                )

            try:
                return response.json()["choices"][0]["message"]["content"]

            except (KeyError, IndexError, ValueError):
                return f"Unexpected vision response: {response.text[:500]}"

        raise ValueError(f"Unknown action: {action}")

    @staticmethod
    def _dimensions(image):
        fmt = (image.suffix or "?").lstrip(".").upper() or "?"
        width = height = 0

        try:
            data = image.read_bytes()[:64]

            if data[:8] == b"\x89PNG\r\n\x1a\n":
                fmt = "PNG"
                width, height = struct.unpack(">II", data[16:24])

            elif data[:6] in (b"GIF87a", b"GIF89a"):
                fmt = "GIF"
                width, height = struct.unpack("<HH", data[6:10])

            elif data[:2] == b"BM":
                fmt = "BMP"
                width, height = struct.unpack("<ii", data[18:26])

            elif data[:3] == b"\xff\xd8\xff":
                fmt = "JPEG"
                width, height = ImageTool._jpeg_size(image)

        except Exception:
            pass

        return fmt, width or "?", height or "?"

    @staticmethod
    def _jpeg_size(image):
        with open(image, "rb") as handle:
            handle.read(2)

            while True:
                marker = handle.read(1)

                if not marker:
                    return 0, 0

                if marker != b"\xff":
                    continue

                kind = handle.read(1)

                if not kind:
                    return 0, 0

                code = kind[0]

                if code in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                            0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    handle.read(3)
                    height, width = struct.unpack(">HH", handle.read(4))
                    return width, height

                length = struct.unpack(">H", handle.read(2))[0]
                handle.seek(length - 2, os.SEEK_CUR)

    @staticmethod
    def _fmt_size(bytes_value):
        for unit in ("B", "KB", "MB", "GB"):
            if bytes_value < 1024 or unit == "GB":
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024

        return f"{bytes_value:.1f} GB"
