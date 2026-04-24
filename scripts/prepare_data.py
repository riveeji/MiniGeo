from pathlib import Path

from minigeo.rag.corpus import corpus_stats, load_corpus


def main() -> None:
    path = Path("data/processed/rag_corpus.jsonl")
    rows = load_corpus(path)
    stats = corpus_stats(rows)
    for key, value in stats.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()

