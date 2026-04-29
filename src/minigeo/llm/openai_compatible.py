import json
import http.client
import os
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

Transport = Callable[[str, dict[str, str], dict[str, Any], float], dict[str, Any] | str]


class OpenAICompatibleClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout: float = 60.0,
        transport: Transport | None = None,
        retries: int = 2,
        retry_sleep: float = 1.0,
        disable_thinking: bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.transport = transport or self._urllib_transport
        self.retries = retries
        self.retry_sleep = retry_sleep
        self.disable_thinking = disable_thinking

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = self.chat(messages, temperature=temperature, max_tokens=max_tokens)
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError(f"Unexpected chat completion response: {response}") from exc

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if self.disable_thinking:
            payload["chat_template_kwargs"] = {"enable_thinking": False}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        raw = self._call_with_retries(f"{self.base_url}/chat/completions", headers, payload)
        if isinstance(raw, str):
            return json.loads(raw)
        return raw

    def _call_with_retries(self, url: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any] | str:
        last_exc: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                return self.transport(url, headers, payload, self.timeout)
            except (TimeoutError, ConnectionError, http.client.IncompleteRead, http.client.RemoteDisconnected) as exc:
                last_exc = exc
                if attempt >= self.retries:
                    break
                time.sleep(self.retry_sleep)
        assert last_exc is not None
        raise last_exc

    @staticmethod
    def _urllib_transport(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: float) -> dict[str, Any]:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"LLM request failed with HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise ConnectionError(f"LLM request failed: {exc.reason}") from exc
        except (TimeoutError, http.client.IncompleteRead, http.client.RemoteDisconnected) as exc:
            raise ConnectionError(f"LLM request failed due to transient connection error: {exc}") from exc
        return json.loads(body)


def client_from_env(env: dict[str, str] | None = None, transport: Transport | None = None) -> OpenAICompatibleClient:
    values = env if env is not None else os.environ
    base_url = values.get("OPENAI_BASE_URL", "").strip()
    if not base_url:
        raise ValueError("OPENAI_BASE_URL is required, for example http://localhost:8000/v1")
    api_key = values.get("OPENAI_API_KEY", "EMPTY")
    model = values.get("MINIGEO_MODEL", "Qwen/Qwen3.5-2B")
    timeout = float(values.get("MINIGEO_LLM_TIMEOUT", "60"))
    retries = int(values.get("MINIGEO_LLM_RETRIES", "2"))
    disable_thinking = _enabled(values.get("MINIGEO_DISABLE_THINKING"))
    return OpenAICompatibleClient(
        base_url=base_url,
        api_key=api_key,
        model=model,
        timeout=timeout,
        transport=transport,
        retries=retries,
        disable_thinking=disable_thinking,
    )


def _enabled(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}
