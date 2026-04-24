from pathlib import Path
import sys

from minigeo.llm.openai_compatible import client_from_env
from minigeo.rag.corpus import load_corpus
from minigeo.rag.model_rag import generate_model_rag_answer


def main() -> None:
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))
    try:
        client = client_from_env()
    except ValueError as exc:
        print(f"configuration_error={exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    question = "石英的主要化学成分是什么？"
    result = generate_model_rag_answer(question, corpus, client, top_k=5)
    printable = {
        "answer": result["answer"],
        "citations": result["citations"],
        "abstained": result["abstained"],
        "confidence": result["confidence"],
        "evidence": [row["chunk_id"] for row in result["evidence"]],
    }
    print(printable)


if __name__ == "__main__":
    main()
