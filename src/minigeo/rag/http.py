import json
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

Transport = Callable[[str, dict[str, str], dict[str, Any], float], dict[str, Any] | str]


def post_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP request failed with status {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"HTTP request failed: {exc.reason}") from exc
    return json.loads(body)


def parse_json_response(raw: dict[str, Any] | str) -> dict[str, Any]:
    if isinstance(raw, str):
        return json.loads(raw)
    return raw

