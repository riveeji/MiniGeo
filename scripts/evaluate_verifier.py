from pathlib import Path

from minigeo.rag.corpus import load_corpus
from minigeo.verifier.simple import verify_answer


def main() -> None:
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))
    answer = "石英常见强拉曼峰接近 464 cm-1。"
    report = verify_answer(answer, [row for row in corpus if row["chunk_id"] == "doc_quartz#chunk_002"])
    print(report)


if __name__ == "__main__":
    main()

