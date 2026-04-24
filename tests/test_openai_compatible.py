import json

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


def test_client_from_env_requires_base_url() -> None:
    try:
        client_from_env({}, transport=lambda url, headers, payload, timeout: {})
    except ValueError as exc:
        assert "OPENAI_BASE_URL" in str(exc)
    else:
        raise AssertionError("client_from_env should require OPENAI_BASE_URL")
