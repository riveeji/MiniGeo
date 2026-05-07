from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class ReleaseArtifact:
    name: str
    path: Path
    required_terms: tuple[str, ...] = ()
    note: str = ""


DEFAULT_RELEASE_ARTIFACTS = (
    ReleaseArtifact("README", Path("README.md"), ("当前状态", "运行方式"), "项目入口和复现实验说明"),
    ReleaseArtifact("架构文档", Path("docs/architecture.md"), ("系统总览", "Verifier", "SQL"), "系统分层和公共接口"),
    ReleaseArtifact("Benchmark 文档", Path("docs/benchmark.md"), ("MiniGeo-Bench", "schema", "泄漏"), "评测集规则和泄漏控制"),
    ReleaseArtifact("Data card", Path("docs/data-card.md"), ("数据来源", "license", "reference_answer_leaks"), "语料、SFT 和版权说明"),
    ReleaseArtifact("主结果表", Path("results/main_results.md"), ("Citation Hit", "MiniGeo-Agent", "Qwen3.5-4B"), "核心定量结果"),
    ReleaseArtifact("失败案例分析", Path("results/failure_cases.md"), ("failure_type", "next_action"), "可复查失败样例"),
    ReleaseArtifact("Agent 多案例报告", Path("results/agent_cases.md"), ("通过率", "Verification", "Qinhuangdao"), "混合文档和 SQL demo"),
    ReleaseArtifact("Colab notebook 模板", Path("notebooks/minigeo_colab_template.ipynb"), (), "Colab 入口"),
    ReleaseArtifact("A100 SFT runbook", Path("docs/a100-json-sft-smoke-cells.md"), ("A100", "json64", "download"), "封档后复现实验指令"),
    ReleaseArtifact("A100 evidence eval runbook", Path("docs/a100-json64-evidence-eval-cells.md"), ("A100", "evidence", "raw_model_output_original"), "封档后证据注入复现实验指令"),
)


DEFAULT_REMAINING_GPU_TASKS = (
    "展示版已封档，不再安排 A100 或长训。",
    "保留已完成的 json64 evidence final smoke 结果；后续只有在专门修复 malformed JSON 时才考虑重新开短 smoke。",
    "继续保持 `reference_answer_leaks=[]`，adapter/checkpoints 不进 git。",
)


def _display_path(path: Path) -> str:
    return path.as_posix()


def check_release_artifacts(
    artifacts: Iterable[ReleaseArtifact] = DEFAULT_RELEASE_ARTIFACTS,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for artifact in artifacts:
        if not artifact.path.exists():
            rows.append(
                {
                    "name": artifact.name,
                    "path": _display_path(artifact.path),
                    "status": "missing",
                    "missing_terms": list(artifact.required_terms),
                    "note": artifact.note,
                }
            )
            continue

        text = artifact.path.read_text(encoding="utf-8", errors="ignore")
        missing_terms = [term for term in artifact.required_terms if term not in text]
        rows.append(
            {
                "name": artifact.name,
                "path": _display_path(artifact.path),
                "status": "ready" if not missing_terms else "incomplete",
                "missing_terms": missing_terms,
                "note": artifact.note,
            }
        )
    return rows


def format_release_checklist(
    rows: list[dict[str, Any]],
    remaining_gpu_tasks: Iterable[str] = DEFAULT_REMAINING_GPU_TASKS,
) -> str:
    ready = sum(1 for row in rows if row["status"] == "ready")
    incomplete = sum(1 for row in rows if row["status"] == "incomplete")
    missing = sum(1 for row in rows if row["status"] == "missing")

    lines = [
        "# MiniGeo 发布验收清单",
        "",
        "本文件由 `scripts/write_release_checklist.py` 生成，用于检查最终展示材料是否齐全。当前仓库已按展示版封档，A100 final smoke 结果已经接入本地 `results/`。",
        "",
        "## 汇总",
        "",
        f"- ready_items={ready}",
        f"- incomplete_items={incomplete}",
        f"- missing_items={missing}",
        "",
        "## 交付项",
        "",
        "| 交付项 | 状态 | 文件 | 缺失关键词 | 说明 |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        missing_terms = ", ".join(row.get("missing_terms") or [])
        lines.append(
            f"| {row['name']} | {row['status']} | {row['path']} | {missing_terms} | {row.get('note', '')} |"
        )

    lines.extend(["", "## 封档后续策略", ""])
    for task in remaining_gpu_tasks:
        lines.append(f"- {task}")
    lines.append("")

    if incomplete or missing:
        lines.extend(
            [
                "## 本地下一步",
                "",
                "优先补齐 `incomplete` 和 `missing` 项；全部 ready 后再封档。",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "## 本地下一步",
                "",
                "本地展示材料已齐，展示版可以保持冻结状态。",
                "",
            ]
        )
    return "\n".join(lines)
