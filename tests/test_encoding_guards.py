from pathlib import Path


def test_core_text_files_keep_readable_chinese_text() -> None:
    files = [
        Path("README.md"),
        Path("src/minigeo/eval/local_summary.py"),
        Path("tests/test_local_summary.py"),
        Path("src/minigeo/sql/generator.py"),
        Path("src/minigeo/verifier/claim_extractor.py"),
        Path("src/minigeo/verifier/support_classifier.py"),
        Path("scripts/agent_demo.py"),
    ]
    mojibake_markers = ["зџ", "ж\xa0", "пј", "гЂ", "鏄", "鐨", "锛", "銆", "歿"]
    for path in files:
        text = path.read_text(encoding="utf-8")
        for marker in mojibake_markers:
            assert marker not in text, f"{path} contains mojibake marker {marker!r}"
