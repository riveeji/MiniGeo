from pathlib import Path

from minigeo.eval.release import ReleaseArtifact, check_release_artifacts, format_release_checklist


def test_check_release_artifacts_marks_ready_when_required_terms_exist(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("MiniGeo\n当前状态\n运行方式\n", encoding="utf-8")

    artifacts = [
        ReleaseArtifact(
            name="README",
            path=readme,
            required_terms=("当前状态", "运行方式"),
            note="项目入口",
        )
    ]

    rows = check_release_artifacts(artifacts)

    assert rows == [
        {
            "name": "README",
            "path": readme.as_posix(),
            "status": "ready",
            "missing_terms": [],
            "note": "项目入口",
        }
    ]


def test_check_release_artifacts_reports_missing_terms_and_files(tmp_path: Path) -> None:
    doc = tmp_path / "docs.md"
    doc.write_text("只包含一部分内容", encoding="utf-8")

    rows = check_release_artifacts(
        [
            ReleaseArtifact("文档", doc, ("关键指标",), "需要补充"),
            ReleaseArtifact("缺失文件", tmp_path / "missing.md", (), "未生成"),
        ]
    )

    assert rows[0]["status"] == "incomplete"
    assert rows[0]["path"] == doc.as_posix()
    assert rows[0]["missing_terms"] == ["关键指标"]
    assert rows[1]["status"] == "missing"


def test_format_release_checklist_contains_summary_and_next_actions() -> None:
    markdown = format_release_checklist(
        [
            {"name": "README", "path": "README.md", "status": "ready", "missing_terms": [], "note": "项目入口"},
            {
                "name": "失败案例",
                "path": "results/failure_cases.md",
                "status": "incomplete",
                "missing_terms": ["failure_type"],
                "note": "需要失败归因",
            },
        ],
        remaining_gpu_tasks=["短 smoke 验证 json64 evidence adapter"],
    )

    assert "# MiniGeo 发布验收清单" in markdown
    assert "ready_items=1" in markdown
    assert "incomplete_items=1" in markdown
    assert "| README | ready | README.md |  | 项目入口 |" in markdown
    assert "短 smoke 验证 json64 evidence adapter" in markdown
