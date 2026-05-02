from minigeo.verifier.factory import build_verifier_from_env


def test_build_verifier_from_env_uses_local_pipeline_by_default() -> None:
    verifier = build_verifier_from_env({})

    report = verifier.verify("石英主要成分是二氧化硅。", [{"chunk_id": "q", "text": "石英主要成分是二氧化硅。"}])

    assert report["verdict"] == "supported"


def test_build_verifier_from_env_uses_model_components_when_enabled() -> None:
    calls = []
    payloads = []

    def fake_transport(url, headers, payload, timeout):
        payloads.append(payload)
        calls.append(payload["messages"][-1]["content"])
        if "抽取" in payload["messages"][-1]["content"]:
            return {"choices": [{"message": {"content": '["石英主要成分是二氧化硅"]'}}]}
        return {"choices": [{"message": {"content": '{"status":"supported","evidence":["q"],"confidence":0.9}'}}]}

    verifier = build_verifier_from_env(
        {
            "OPENAI_BASE_URL": "http://localhost:8000/v1",
            "OPENAI_API_KEY": "EMPTY",
            "MINIGEO_VERIFIER_MODEL": "Qwen/Qwen3.5-2B",
            "MINIGEO_VERIFIER_USE_MODEL": "1",
            "MINIGEO_DISABLE_THINKING": "1",
        },
        transport=fake_transport,
    )

    report = verifier.verify("石英主要成分是二氧化硅。", [{"chunk_id": "q", "text": "石英主要成分是二氧化硅。"}])

    assert report["claims"][0]["confidence"] == 0.9
    assert any("抽取" in prompt for prompt in calls)
    assert all(payload.get("chat_template_kwargs") == {"enable_thinking": False} for payload in payloads)
