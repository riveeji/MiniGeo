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
    ReleaseArtifact("A100 SFT runbook", Path("docs/a100-json-sft-smoke-cells.md"), ("A100", "json64", "download"), "下一次 GPU smoke 指令"),
    ReleaseArtifact("A100 evidence eval runbook", Path("docs/a100-json64-evidence-eval-cells.md"), ("A100", "evidence", "raw_model_output_original"), "证据注入评测指令"),
)


DEFAULT_REMAINING_GPU_TASKS = (
    "只在必要时开 A100，先运行 json64 evidence adapter 的短 smoke，确认原始尾部污染是否减少。",
    "如果短 smoke 同时保持 citation/refusal 指标且原始输出格式稳定，再考虑 553step 或 1 epoch 小规模 SFT。",
    "长训前继续保持 `reference_answer_leaks=[]`，adapter/checkpoints 不进 git。",
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
        "本文件由 `scripts/write_release_checklist.py` 生成，用于检查最终展示材料是否齐全。它只检查本地文件和关键文本，不代表外部 A100 结果已经重新跑完。",
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

    lines.extend(["", "## 剩余 GPU 任务", ""])
    for task in remaining_gpu_tasks:
        lines.append(f"- {task}")
    lines.append("")

    if incomplete or missing:
        lines.extend(
            [
                "## 本地下一步",
                "",
                "优先补齐 `incomplete` 和 `missing` 项；全部 ready 后再安排下一次 A100 短验证。",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "## 本地下一步",
                "",
                "本地展示材料已齐，可以进入最终人工通读和必要的 A100 短验证。",
                "",
            ]
        )
    return "\n".join(lines)
