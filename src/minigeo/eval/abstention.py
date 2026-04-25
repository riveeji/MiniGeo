from typing import Any


def _expected_abstain(row: dict[str, Any]) -> bool:
    return not bool(row.get("answerable", True))


def abstention_accuracy(rows: list[dict[str, Any]], answers: dict[str, dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    correct = 0
    for row in rows:
        answer = answers.get(row["id"], {})
        if bool(answer.get("abstained", False)) == _expected_abstain(row):
            correct += 1
    return correct / len(rows)


def summarize_abstention(
    rows: list[dict[str, Any]],
    answers: dict[str, dict[str, Any]],
    latency_ms: float | None = None,
) -> dict[str, Any]:
    false_abstain = 0
    correct_abstain = 0
    missed_abstain = 0
    correct_answer = 0
    for row in rows:
        expected = _expected_abstain(row)
        observed = bool(answers.get(row["id"], {}).get("abstained", False))
        if expected and observed:
            correct_abstain += 1
        elif expected and not observed:
            missed_abstain += 1
        elif not expected and observed:
            false_abstain += 1
        else:
            correct_answer += 1
    summary = {
        "items": len(rows),
        "abstention_accuracy": abstention_accuracy(rows, answers),
        "correct_abstain": correct_abstain,
        "missed_abstain": missed_abstain,
        "false_abstain": false_abstain,
        "correct_answer": correct_answer,
    }
    if latency_ms is not None:
        summary["latency_ms"] = latency_ms
    return summary
