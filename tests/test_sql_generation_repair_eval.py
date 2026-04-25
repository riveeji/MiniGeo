from minigeo.eval.sql import sql_exec_accuracy, summarize_sql_results
from minigeo.sql.generator import RuleBasedSQLGenerator
from minigeo.sql.repair import repair_sql
from minigeo.sql.tools import execute_sql, init_demo_db


def test_rule_based_sql_generator_handles_qinhuangdao_errors() -> None:
    sql = RuleBasedSQLGenerator().generate("秦皇岛样本中被误判最多的预测矿物是什么？")

    assert "Qinhuangdao" in sql
    assert "predicted_mineral" in sql
    assert "is_correct = 0" in sql
    assert "group by predicted_mineral" in sql.lower()


def test_rule_based_sql_generator_handles_peak_range_query() -> None:
    sql = RuleBasedSQLGenerator().generate("查询具有 460 到 470 cm-1 峰位的样本。")

    assert "peak_cm1 between 460 and 470" in sql.lower()
    assert "spectra" in sql.lower()


def test_rule_based_sql_generator_handles_schema_and_missing_sample_queries() -> None:
    generator = RuleBasedSQLGenerator()

    spectra_sql = generator.generate("哪个表保存样本光谱峰位？")
    missing_sql = generator.generate("资料库是否包含辉石样本 PX-101 的数据库记录？")
    fields_sql = generator.generate("查询 Agent 最终报告应返回哪些结构化字段。")

    assert "sqlite_master" in spectra_sql
    assert "spectra" in spectra_sql
    assert "PX-101" in missing_sql
    assert "sample_code" in missing_sql
    assert "sql" in fields_sql and "verification" in fields_sql


def test_repair_sql_fixes_common_column_and_join_mistakes() -> None:
    broken = "select prediction from predictions join samples where samples.region = 'Qinhuangdao'"
    repaired = repair_sql(broken, error="no such column: prediction")

    assert "predicted_mineral" in repaired
    assert "samples.sample_id = predictions.sample_id" in repaired


def test_generated_and_repaired_sql_executes(tmp_path) -> None:
    db_path = tmp_path / "demo.sqlite"
    init_demo_db(db_path)
    sql = RuleBasedSQLGenerator().generate("秦皇岛样本中被误判最多的预测矿物是什么？")

    result = execute_sql(db_path, sql)

    assert result["error"] is None
    assert result["execution_result"][0]["predicted_mineral"] == "feldspar"


def test_sql_eval_summarizes_expected_result_matches() -> None:
    rows = [
        {"id": "q1", "requires_sql": True, "expected_result": {"top_predicted_mineral": "feldspar"}},
        {"id": "q2", "requires_sql": True, "expected_result": {"found": False}},
    ]
    outputs = {
        "q1": {"error": None, "execution_result": [{"predicted_mineral": "feldspar", "errors": 2}]},
        "q2": {"error": "no such table", "execution_result": []},
    }

    assert sql_exec_accuracy(rows, outputs) == 0.5
    assert summarize_sql_results(rows, outputs)["sql_items"] == 2
