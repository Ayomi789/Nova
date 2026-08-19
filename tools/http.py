import json

import requests

from tools.base import Tool


class HttpTool(Tool):

    name = "http"

    description = (
        "Send raw HTTP requests with any method, custom "
        "headers and a JSON body; returns status and body."
    )

    MAX_BODY = 20000

    def run(
        self,
        method="GET",
        url=None,
        headers=None,
        body=None,
        timeout=15,
    ):

        if not url:
            raise ValueError("A url is required.")

        if not url.startswith(("http://", "https://")):
            return f"Unsupported URL scheme: {url}"

        parsed_headers = {}

        if headers:
            if isinstance(headers, str):
                try:
                    parsed_headers = json.loads(headers)
                except ValueError:
                    return f"Headers must be valid JSON: {headers}"
            elif isinstance(headers, dict):
                parsed_headers = headers
            else:
                return f"Headers must be an object: {headers}"

        parsed_body = None

        if body:
            if isinstance(body, str):
                try:
                    parsed_body = json.loads(body)
                except ValueError:
                    return f"Body must be valid JSON: {body}"
            else:
                parsed_body = body

        try:
            response = requests.request(
                method.upper(),
                url,
                headers=parsed_headers,
                json=parsed_body,
                timeout=max(1, min(int(timeout), 120)),
            )

        except requests.RequestException as exc:
            return f"Request failed: {exc}"

        response.encoding = "utf-8"

        text = response.text

        if len(text) > self.MAX_BODY:
            text = text[: self.MAX_BODY] + "\n…[truncated]"

        return f"HTTP {response.status_code} {response.reason}\n\n{text}"
