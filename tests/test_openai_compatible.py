import json
import http.client

from minigeo.llm.openai_compatible import OpenAICompatibleClient, client_from_env


def test_openai_compatible_client_posts_chat_payload_and_reads_content() -> None:
    captured = {}

    def fake_transport(url, headers, payload, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["payload"] = payload
        captured["timeout"] = timeout
        return {
            "choices": [
                {"message": {"content": "模型回答"}}
            ]
        }

    client = OpenAICompatibleClient(
        base_url="http://localhost:8000/v1",
        api_key="EMPTY",
        model="Qwen/Qwen3.5-2B",
        transport=fake_transport,
    )

    content = client.generate("回答石英是什么。")

    assert content == "模型回答"
    assert captured["url"] == "http://localhost:8000/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer EMPTY"
    assert captured["payload"]["model"] == "Qwen/Qwen3.5-2B"
    assert captured["payload"]["messages"][-1]["content"] == "回答石英是什么。"


def test_openai_compatible_client_accepts_json_string_transport() -> None:
    def fake_transport(url, headers, payload, timeout):
        return json.dumps({"choices": [{"message": {"content": "json response"}}]})

    client = OpenAICompatibleClient(
        base_url="http://localhost:8000/v1/",
        api_key="EMPTY",
        model="Qwen/Qwen3.5-2B",
        transport=fake_transport,
    )

    assert client.generate("test") == "json response"


def test_client_from_env_uses_openai_compatible_defaults() -> None:
    client = client_from_env(
        {
            "OPENAI_BASE_URL": "http://localhost:8000/v1",
            "OPENAI_API_KEY": "EMPTY",
            "MINIGEO_MODEL": "Qwen/Qwen3.5-2B",
        },
        transport=lambda url, headers, payload, timeout: {"choices": [{"message": {"content": "ok"}}]},
    )

    assert client.model == "Qwen/Qwen3.5-2B"
    assert client.generate("hello") == "ok"


def test_client_from_env_can_disable_qwen_thinking() -> None:
    captured = {}

    def fake_transport(url, headers, payload, timeout):
        captured["payload"] = payload
        return {"choices": [{"message": {"content": "ok"}}]}

    client = client_from_env(
        {
            "OPENAI_BASE_URL": "http://localhost:8000/v1",
            "OPENAI_API_KEY": "EMPTY",
            "MINIGEO_MODEL": "Qwen/Qwen3.5-4B",
            "MINIGEO_DISABLE_THINKING": "1",
        },
        transport=fake_transport,
    )

    assert client.generate("hello") == "ok"
    assert captured["payload"]["chat_template_kwargs"] == {"enable_thinking": False}


def test_client_from_env_requires_base_url() -> None:
    try:
        client_from_env({}, transport=lambda url, headers, payload, timeout: {})
    except ValueError as exc:
        assert "OPENAI_BASE_URL" in str(exc)
    else:
        raise AssertionError("client_from_env should require OPENAI_BASE_URL")


def test_openai_compatible_client_retries_transient_disconnects() -> None:
    calls = {"count": 0}

    def flaky_transport(url, headers, payload, timeout):
        calls["count"] += 1
        if calls["count"] == 1:
            raise http.client.IncompleteRead(b"{", 10)
        return {"choices": [{"message": {"content": "ok"}}]}

    client = OpenAICompatibleClient(
        base_url="https://example.test/v1",
        api_key="EMPTY",
        model="Qwen/Qwen3.5-4B",
        transport=flaky_transport,
        retries=1,
    )

    assert client.generate("hello") == "ok"
    assert calls["count"] == 2
