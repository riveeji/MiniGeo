from minigeo.eval.abstention import abstention_accuracy, summarize_abstention


def test_abstention_accuracy_matches_answerable_flag() -> None:
    rows = [
        {"id": "q1", "answerable": True},
        {"id": "q2", "answerable": False},
        {"id": "q3", "answerable": False},
    ]
    answers = {
        "q1": {"abstained": False},
        "q2": {"abstained": True},
        "q3": {"abstained": False},
    }

    assert abstention_accuracy(rows, answers) == 2 / 3


def test_summarize_abstention_reports_confusion_counts() -> None:
    rows = [
        {"id": "q1", "answerable": True},
        {"id": "q2", "answerable": False},
    ]
    answers = {"q1": {"abstained": True}, "q2": {"abstained": True}}

    summary = summarize_abstention(rows, answers, latency_ms=1.5)

    assert summary["items"] == 2
    assert summary["abstention_accuracy"] == 0.5
    assert summary["false_abstain"] == 1
    assert summary["correct_abstain"] == 1
    assert summary["latency_ms"] == 1.5
