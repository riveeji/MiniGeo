import json
import os
import re
from typing import Protocol

from minigeo.llm.openai_compatible import OpenAICompatibleClient
from minigeo.rag.http import Transport
from minigeo.sql.generator import RuleBasedSQLGenerator


class TextGenerator(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class ModelSQLGenerator:
    def __init__(self, client: TextGenerator, fallback: RuleBasedSQLGenerator | None = None):
        self.client = client
        self.fallback = fallback or RuleBasedSQLGenerator()

    def generate(self, question: str, schema: str | None = None) -> str:
        prompt = (
            "你是 MiniGeo 的 Text-to-SQL 组件。根据问题和 SQLite schema 生成只读 SQL。"
            "只返回 JSON 对象：{\"sql\":\"select ...\"}。不要返回解释。\n\n"
            f"问题：{question}\n\nSchema:\n{schema or '使用 samples、predictions、spectra、minerals 四张表。'}"
        )
        raw = self.client.generate(prompt)
        sql = _extract_sql(raw)
        if sql:
            return sql
        return self.fallback.generate(question)


def _extract_sql(raw: str) -> str | None:
    text = raw.strip()
    try:
        data = json.loads(text)
        sql = str(data.get("sql", "")).strip()
        if sql.lower().startswith("select"):
            return sql
    except json.JSONDecodeError:
        pass
    match = re.search(r"select\b.+", text, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(0).strip().rstrip(";")
    return None


def _enabled(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def sql_generator_from_env(
    env: dict[str, str] | None = None,
    transport: Transport | None = None,
):
    values = env if env is not None else os.environ
    if not _enabled(values.get("MINIGEO_SQL_USE_MODEL")):
        return RuleBasedSQLGenerator()
    base_url = values.get("MINIGEO_SQL_BASE_URL") or values.get("OPENAI_BASE_URL", "")
    base_url = base_url.strip()
    if not base_url:
        raise ValueError("MINIGEO_SQL_BASE_URL or OPENAI_BASE_URL is required.")
    client = OpenAICompatibleClient(
        base_url=base_url,
        api_key=values.get("MINIGEO_SQL_API_KEY") or values.get("OPENAI_API_KEY", "EMPTY"),
        model=values.get("MINIGEO_SQL_MODEL", values.get("MINIGEO_MODEL", "Qwen/Qwen3.5-2B")),
        timeout=float(values.get("MINIGEO_SQL_TIMEOUT", values.get("MINIGEO_LLM_TIMEOUT", "60"))),
        transport=transport,
    )
    return ModelSQLGenerator(client)

