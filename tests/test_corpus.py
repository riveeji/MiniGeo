from pathlib import Path

from minigeo.rag.corpus import corpus_stats, load_corpus


def test_load_corpus_requires_chunk_id_and_text(tmp_path: Path) -> None:
    path = tmp_path / "corpus.jsonl"
    path.write_text(
        '{"chunk_id":"doc_1#chunk_1","doc_id":"doc_1","text":"石英具有较高硬度。",'
        '"source":"demo","url":"https://example.com","page":null,'
        '"topic":"mineral_property","mineral":"quartz","license":"public"}\n',
        encoding="utf-8",
    )

    rows = load_corpus(path)

    assert rows[0]["chunk_id"] == "doc_1#chunk_1"
    assert "石英" in rows[0]["text"]


def test_corpus_stats_counts_chunks_and_topics(tmp_path: Path) -> None:
    path = tmp_path / "corpus.jsonl"
    path.write_text(
        '{"chunk_id":"a","doc_id":"d","text":"石英","source":"s","url":"u","page":null,"topic":"concept","mineral":"quartz","license":"public"}\n'
        '{"chunk_id":"b","doc_id":"d","text":"长石","source":"s","url":"u","page":null,"topic":"concept","mineral":"feldspar","license":"public"}\n',
        encoding="utf-8",
    )

    stats = corpus_stats(load_corpus(path))

    assert stats["chunks"] == 2
    assert stats["topics"] == {"concept": 2}
    assert stats["minerals"] == {"quartz": 1, "feldspar": 1}

