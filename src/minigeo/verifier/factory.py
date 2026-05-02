import os

from minigeo.llm.openai_compatible import OpenAICompatibleClient
from minigeo.rag.http import Transport
from minigeo.verifier.claim_extractor import LocalClaimExtractor, ModelClaimExtractor
from minigeo.verifier.support_classifier import HeuristicSupportClassifier, ModelSupportClassifier
from minigeo.verifier.verifier import MiniGeoVerifier


def _enabled(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def build_verifier_from_env(
    env: dict[str, str] | None = None,
    transport: Transport | None = None,
) -> MiniGeoVerifier:
    values = env if env is not None else os.environ
    use_model = _enabled(values.get("MINIGEO_VERIFIER_USE_MODEL"))
    if not use_model:
        return MiniGeoVerifier()

    base_url = values.get("MINIGEO_VERIFIER_BASE_URL") or values.get("OPENAI_BASE_URL", "")
    base_url = base_url.strip()
    if not base_url:
        raise ValueError("MINIGEO_VERIFIER_BASE_URL or OPENAI_BASE_URL is required.")
    client = OpenAICompatibleClient(
        base_url=base_url,
        api_key=values.get("MINIGEO_VERIFIER_API_KEY") or values.get("OPENAI_API_KEY", "EMPTY"),
        model=values.get("MINIGEO_VERIFIER_MODEL", values.get("MINIGEO_MODEL", "Qwen/Qwen3.5-2B")),
        timeout=float(values.get("MINIGEO_VERIFIER_TIMEOUT", values.get("MINIGEO_LLM_TIMEOUT", "60"))),
        transport=transport,
        retries=int(values.get("MINIGEO_VERIFIER_RETRIES", values.get("MINIGEO_LLM_RETRIES", "2"))),
        disable_thinking=_enabled(values.get("MINIGEO_DISABLE_THINKING")),
    )
    return MiniGeoVerifier(
        claim_extractor=ModelClaimExtractor(client, fallback=LocalClaimExtractor()),
        support_classifier=ModelSupportClassifier(client, fallback=HeuristicSupportClassifier()),
    )
