from typing import Any


def expected_result_matches(expected: dict[str, Any] | None, output: dict[str, Any]) -> bool:
    if output.get("error"):
        return False
    rows = output.get("execution_result", [])
    if expected is None:
        return bool(rows) or output.get("error") is None
    if expected.get("found") is False:
        return rows == []
    if "top_predicted_mineral" in expected:
        return bool(rows) and rows[0].get("predicted_mineral") == expected["top_predicted_mineral"]
    if "table" in expected:
        table = expected["table"]
        sql = str(output.get("sql", "")).lower()
        return table.lower() in sql or any(table in str(value) for row in rows for value in row.values())
    if "tables" in expected:
        sql = str(output.get("sql", "")).lower()
        if all(table.lower() in sql for table in expected["tables"]):
            return True
        values = {str(value) for row in rows for value in row.values()}
        return set(expected["tables"]) <= values
    if "fields" in expected:
        return bool(rows) and set(expected["fields"]) <= set(rows[0].keys())
    return output.get("error") is None


def sql_exec_accuracy(benchmark_rows: list[dict[str, Any]], outputs: dict[str, dict[str, Any]]) -> float:
    sql_rows = [row for row in benchmark_rows if row.get("requires_sql")]
    if not sql_rows:
        return 0.0
    correct = 0
    for row in sql_rows:
        if expected_result_matches(row.get("expected_result"), outputs.get(row["id"], {"error": "missing"})):
            correct += 1
    return correct / len(sql_rows)


def summarize_sql_results(benchmark_rows: list[dict[str, Any]], outputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    sql_rows = [row for row in benchmark_rows if row.get("requires_sql")]
    failures = {
        row["id"]: outputs.get(row["id"], {"error": "missing"}).get("error")
        for row in sql_rows
        if not expected_result_matches(row.get("expected_result"), outputs.get(row["id"], {"error": "missing"}))
    }
    return {
        "sql_items": len(sql_rows),
        "sql_exec_accuracy": sql_exec_accuracy(benchmark_rows, outputs),
        "failures": failures,
    }
