import json
from pathlib import Path


def test_colab_notebook_template_is_valid_and_actionable() -> None:
    path = Path("notebooks/minigeo_colab_template.ipynb")
    notebook = json.loads(path.read_text(encoding="utf-8"))
    source = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook.get("cells", [])
    )

    assert notebook["nbformat"] == 4
    assert "python scripts/build_sft_corpus.py" in source
    assert "python scripts/train_lora.py --check-only" in source
    assert "python scripts/evaluate_retrieval_ablation.py --use-services" in source
