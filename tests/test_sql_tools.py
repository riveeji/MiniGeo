import sqlite3

from minigeo.sql.tools import execute_sql, init_demo_db, schema_text


def test_sql_tool_executes_demo_query(tmp_path) -> None:
    db_path = tmp_path / "demo.sqlite"
    init_demo_db(db_path)

    result = execute_sql(
        db_path,
        "select predicted_mineral, count(*) as errors from predictions "
        "join samples on samples.sample_id = predictions.sample_id "
        "where samples.region = 'Qinhuangdao' and is_correct = 0 "
        "group by predicted_mineral order by errors desc",
    )

    assert result["error"] is None
    assert result["execution_result"][0]["predicted_mineral"] == "feldspar"


def test_schema_text_lists_tables(tmp_path) -> None:
    db_path = tmp_path / "demo.sqlite"
    init_demo_db(db_path)

    text = schema_text(sqlite3.connect(db_path))

    assert "samples" in text
    assert "predictions" in text

