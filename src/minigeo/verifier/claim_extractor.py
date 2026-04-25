import json
import re
from typing import Protocol


class TextGenerator(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class LocalClaimExtractor:
    def extract(self, answer: str) -> list[str]:
        parts = [
            part.strip(" \t\r\n。.!！？；;")
            for part in re.split(r"[。.!！？；;]\s*", answer)
            if part.strip(" \t\r\n。.!！？；;")
        ]
        return parts or ([answer.strip()] if answer.strip() else [])


class ModelClaimExtractor:
    def __init__(self, client: TextGenerator, fallback: LocalClaimExtractor | None = None):
        self.client = client
        self.fallback = fallback or LocalClaimExtractor()

    def extract(self, answer: str) -> list[str]:
        prompt = (
            "请从下面的回答中抽取可验证的事实 claim。"
            "只返回 JSON 数组，每个元素是一条中文 claim。\n\n"
            f"回答：{answer}"
        )
        raw = self.client.generate(prompt)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return self.fallback.extract(answer)
        if not isinstance(data, list):
            return self.fallback.extract(answer)
        claims = [str(item).strip() for item in data if str(item).strip()]
        return claims or self.fallback.extract(answer)

