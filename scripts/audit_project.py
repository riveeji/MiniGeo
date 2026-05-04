import os
from pathlib import Path
import subprocess
import sys

from minigeo.eval.audit import AuditStepResult, format_audit_report, overall_success


def _run_step(name: str, command: list[str], env: dict[str, str] | None = None) -> AuditStepResult:
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    return AuditStepResult(
        name=name,
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def _workspace_temp_env(temp_dir: Path) -> dict[str, str]:
    temp_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    resolved = str(temp_dir.resolve())
    env["TMP"] = resolved
    env["TEMP"] = resolved
    return env


def _pytest_command(python: str) -> list[str]:
    basetemp = Path(".pytest_tmp") / f"basetemp-{os.getpid()}"
    return [
        python,
        "-m",
        "pytest",
        "-q",
        "--basetemp",
        str(basetemp),
        "-p",
        "no:cacheprovider",
    ]


def main() -> None:
    python = sys.executable
    steps = [
        ("单元测试", _pytest_command(python), _workspace_temp_env(Path(".pytest_tmp"))),
        ("Benchmark 分布", [python, "scripts/evaluate_bench.py"]),
        ("检索消融", [python, "scripts/evaluate_retrieval_ablation.py"]),
        ("检索失败分析", [python, "scripts/analyze_retrieval_failures.py"]),
        ("拒答评测", [python, "scripts/evaluate_abstention.py"]),
        ("Verifier 评测", [python, "scripts/evaluate_verifier.py"]),
        ("SQL 评测", [python, "scripts/evaluate_sql.py"]),
        ("Agent Planner 评测", [python, "scripts/evaluate_agent_planner.py"]),
        ("SFT 数据构建", [python, "scripts/build_sft_corpus.py"]),
        ("数据质量审计", [python, "scripts/audit_data_quality.py"]),
        ("QLoRA 配置检查", [python, "scripts/train_lora.py", "--check-only"]),
        ("Agent Demo", [python, "scripts/agent_demo.py"]),
        ("结果文档生成", [python, "scripts/write_report_artifacts.py"]),
        ("本地结果摘要", [python, "scripts/write_local_results.py"]),
    ]

    results = []
    for step in steps:
        if len(step) == 3:
            name, command, env = step
            results.append(_run_step(name, command, env=env))
        else:
            name, command = step
            results.append(_run_step(name, command))
    output = Path("results/local_audit.md")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(format_audit_report(results), encoding="utf-8", newline="\n")
    print(f"wrote={output}")
    if not overall_success(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
