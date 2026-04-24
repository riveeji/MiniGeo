from pathlib import Path

from minigeo.rag.corpus import load_corpus
from minigeo.rag.pipeline import offline_rag_answer


def main() -> None:
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))
    question = "石英常见的拉曼峰大约在什么位置？"
    result = offline_rag_answer(question, corpus)
    print(result)


if __name__ == "__main__":
    main()

