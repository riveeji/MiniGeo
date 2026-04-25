from pathlib import Path
import subprocess
import sys

from minigeo.eval.audit import AuditStepResult, format_audit_report, overall_success


def _run_step(name: str, command: list[str]) -> AuditStepResult:
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return AuditStepResult(
        name=name,
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def main() -> None:
    python = sys.executable
    steps = [
        ("单元测试", [python, "-m", "pytest", "-q"]),
        ("Benchmark 分布", [python, "scripts/evaluate_bench.py"]),
        ("检索消融", [python, "scripts/evaluate_retrieval_ablation.py"]),
        ("拒答评测", [python, "scripts/evaluate_abstention.py"]),
        ("Verifier 评测", [python, "scripts/evaluate_verifier.py"]),
        ("SQL 评测", [python, "scripts/evaluate_sql.py"]),
        ("SFT 数据构建", [python, "scripts/build_sft_corpus.py"]),
        ("QLoRA 配置检查", [python, "scripts/train_lora.py", "--check-only"]),
        ("Agent Demo", [python, "scripts/agent_demo.py"]),
        ("结果文档生成", [python, "scripts/write_report_artifacts.py"]),
        ("本地结果摘要", [python, "scripts/write_local_results.py"]),
    ]

    results = [_run_step(name, command) for name, command in steps]
    output = Path("results/local_audit.md")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(format_audit_report(results), encoding="utf-8", newline="\n")
    print(f"wrote={output}")
    if not overall_success(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
