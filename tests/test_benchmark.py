from pathlib import Path

from minigeo.benchmark import benchmark_summary, load_benchmark


def test_load_benchmark_validates_required_fields(tmp_path: Path) -> None:
    path = tmp_path / "bench.jsonl"
    path.write_text(
        '{"id":"q1","question":"什么是石英？","answer":"石英是二氧化硅矿物。",'
        '"type":"concept","difficulty":"easy","answerable":true,'
        '"requires_sql":false,"evidence":["doc_quartz#chunk_001"],'
        '"expected_sql_intent":null,"expected_result":null}\n',
        encoding="utf-8",
    )

    rows = load_benchmark(path)

    assert rows[0]["id"] == "q1"
    assert rows[0]["evidence"] == ["doc_quartz#chunk_001"]


def test_benchmark_summary_counts_types_and_answerability(tmp_path: Path) -> None:
    path = tmp_path / "bench.jsonl"
    path.write_text(
        "\n".join(
            [
                '{"id":"q1","question":"A","answer":"B","type":"concept","difficulty":"easy","answerable":true,"requires_sql":false,"evidence":[],"expected_sql_intent":null,"expected_result":null}',
                '{"id":"q2","question":"C","answer":"D","type":"unanswerable","difficulty":"easy","answerable":false,"requires_sql":false,"evidence":[],"expected_sql_intent":null,"expected_result":null}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = benchmark_summary(load_benchmark(path))

    assert summary["items"] == 2
    assert summary["types"] == {"concept": 1, "unanswerable": 1}
    assert summary["answerable"] == 1
    assert summary["unanswerable"] == 1

