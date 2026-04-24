import re

_CJK_RE = re.compile(r"[\u3400-\u9fff]")
_WORD_RE = re.compile(r"[A-Za-z0-9_.+-]+|[\u3400-\u9fff]")


def _contains_cjk(text: str) -> bool:
    return bool(_CJK_RE.search(text))


def _fallback_cjk_tokens(text: str) -> list[str]:
    chars = [part for part in _WORD_RE.findall(text.lower()) if part.strip()]
    bigrams = [chars[i] + chars[i + 1] for i in range(len(chars) - 1) if _contains_cjk(chars[i] + chars[i + 1])]
    return chars + bigrams


def tokenize(text: str) -> list[str]:
    normalized = text.strip().lower()
    if not normalized:
        return []
    if _contains_cjk(normalized):
        try:
            import jieba  # type: ignore

            tokens = [token.strip().lower() for token in jieba.cut(normalized) if token.strip()]
            return tokens or _fallback_cjk_tokens(normalized)
        except Exception:
            return _fallback_cjk_tokens(normalized)
    return re.findall(r"[a-z0-9_.+-]+", normalized)

