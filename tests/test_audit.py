from minigeo.eval.audit import AuditStepResult, format_audit_report, overall_success


def test_format_audit_report_contains_step_status_and_outputs() -> None:
    report = format_audit_report(
        [
            AuditStepResult("单元测试", ["python", "-m", "pytest", "-q"], 0, "57 passed", ""),
            AuditStepResult("SQL 评测", ["python", "scripts/evaluate_sql.py"], 1, "", "boom"),
        ]
    )

    assert "# MiniGeo 本地总验收报告" in report
    assert "| 单元测试 | PASS |" in report
    assert "| SQL 评测 | FAIL |" in report
    assert "57 passed" in report
    assert "boom" in report


def test_overall_success_requires_every_step_to_pass() -> None:
    assert overall_success([AuditStepResult("ok", ["cmd"], 0, "", "")])
    assert not overall_success(
        [
            AuditStepResult("ok", ["cmd"], 0, "", ""),
            AuditStepResult("bad", ["cmd"], 2, "", ""),
        ]
    )
