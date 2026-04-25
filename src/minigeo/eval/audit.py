from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class AuditStepResult:
    name: str
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


def overall_success(results: Iterable[AuditStepResult]) -> bool:
    return all(result.returncode == 0 for result in results)


def _status(result: AuditStepResult) -> str:
    return "PASS" if result.returncode == 0 else "FAIL"


def _command_text(command: list[str]) -> str:
    return " ".join(command)


def _output_block(title: str, text: str) -> list[str]:
    if not text.strip():
        return []
    return [f"**{title}**", "", "```text", text.strip(), "```", ""]


def format_audit_report(results: list[AuditStepResult]) -> str:
    lines = [
        "# MiniGeo 本地总验收报告",
        "",
        "本报告由 `scripts/audit_project.py` 生成，用于记录当前仓库在本地环境中可复现的基础验收结果。",
        "",
        "## 总览",
        "",
        "| 步骤 | 状态 | 退出码 | 命令 |",
        "|---|---|---:|---|",
    ]
    for result in results:
        lines.append(
            f"| {result.name} | {_status(result)} | {result.returncode} | `{_command_text(result.command)}` |"
        )

    lines.extend(["", "## 详细输出", ""])
    for result in results:
        lines.extend([f"### {result.name}", "", f"- 状态：{_status(result)}", f"- 退出码：{result.returncode}", ""])
        lines.extend(_output_block("stdout", result.stdout))
        lines.extend(_output_block("stderr", result.stderr))

    return "\n".join(lines).rstrip() + "\n"
