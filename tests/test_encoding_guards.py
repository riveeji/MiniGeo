from pathlib import Path


def test_core_python_sources_keep_readable_chinese_text() -> None:
    files = [
        Path("src/minigeo/sql/generator.py"),
        Path("src/minigeo/verifier/claim_extractor.py"),
        Path("src/minigeo/verifier/support_classifier.py"),
        Path("scripts/agent_demo.py"),
    ]
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert "鐭" not in text
        assert "鏍" not in text
        assert "锛" not in text
        assert "銆" not in text

