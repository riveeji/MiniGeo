import json
import http.client
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

Transport = Callable[[str, dict[str, str], dict[str, Any], float], dict[str, Any] | str]

_POST_JSON_ATTEMPTS = 3
_RETRY_DELAY_SECONDS = 0.25


def post_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    for attempt in range(_POST_JSON_ATTEMPTS):
        request = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read().decode("utf-8")
            return json.loads(body)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP request failed with status {exc.code}: {detail}") from exc
        except http.client.IncompleteRead as exc:
            if attempt == _POST_JSON_ATTEMPTS - 1:
                raise RuntimeError(
                    "HTTP request failed after "
                    f"{_POST_JSON_ATTEMPTS} attempts: incomplete response "
                    f"({len(exc.partial)} bytes read, {exc.expected} more expected)"
                ) from exc
        except (urllib.error.URLError, http.client.RemoteDisconnected, TimeoutError, ConnectionResetError) as exc:
            if attempt == _POST_JSON_ATTEMPTS - 1:
                reason = getattr(exc, "reason", str(exc))
                raise RuntimeError(
                    f"HTTP request failed after {_POST_JSON_ATTEMPTS} attempts: {reason}"
                ) from exc
        time.sleep(_RETRY_DELAY_SECONDS * (attempt + 1))
    raise RuntimeError("HTTP request failed.")


def parse_json_response(raw: dict[str, Any] | str) -> dict[str, Any]:
    if isinstance(raw, str):
        return json.loads(raw)
    return raw
