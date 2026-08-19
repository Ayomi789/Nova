import re

import requests

from tools.base import Tool


class WebTool(Tool):

    name = "web"

    description = (
        "Fetch and read content from URLs "
        "as plain text."
    )

    USER_AGENT = "NovaAgent/0.2 (+local)"

    def run(
        self,
        action="fetch",
        url=None,
        max_bytes=20000,
    ):

        if action != "fetch":
            raise ValueError(f"Unknown action: {action}")

        if not url:
            raise ValueError("Fetch requires a url.")

        if not url.startswith(("http://", "https://")):
            return f"Unsupported URL scheme: {url}"

        try:
            response = requests.get(
                url,
                headers={"User-Agent": self.USER_AGENT},
                timeout=15,
            )

        except requests.RequestException as exc:
            return f"Request failed: {exc}"

        if response.status_code != 200:
            return f"HTTP {response.status_code} for {url}"

        response.encoding = "utf-8"

        text = self._to_text(response.text)

        if len(text) > max_bytes:
            text = text[:max_bytes] + "\n…[truncated]"

        return f"Contents of {url}:\n\n{text}"

    @staticmethod
    def _to_text(html):
        html = re.sub(
            r"(?is)<(script|style).*?>.*?</\1>", " ", html
        )
        html = re.sub(r"(?i)<br\s*/?>", "\n", html)
        html = re.sub(
            r"(?i)</(p|div|li|h[1-6]|tr|blockquote)>",
            "\n",
            html,
        )
        html = re.sub(r"(?s)<[^>]+>", " ", html)

        text = re.sub(r"[ \t]+", " ", html)
        text = re.sub(r"\n\s*\n+", "\n\n", text)

        return text.strip()