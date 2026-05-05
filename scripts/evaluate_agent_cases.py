from pathlib import Path
import json

from minigeo.eval.agent_cases import DEFAULT_AGENT_CASES, evaluate_agent_cases, format_agent_case_report
from minigeo.rag.corpus import load_corpus
from minigeo.sql.tools import init_demo_db


def main() -> None:
    db_path = Path("data/processed/minigeo_demo.sqlite")
    corpus_path = Path("data/processed/rag_corpus.jsonl")
    json_output = Path("results/agent_cases.json")
    markdown_output = Path("results/agent_cases.md")

    init_demo_db(db_path)
    corpus = load_corpus(corpus_path)
    summary, reports = evaluate_agent_cases(DEFAULT_AGENT_CASES, db_path=db_path, corpus=corpus)

    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(
        json.dumps({"summary": summary, "reports": reports}, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    markdown_output.write_text(format_agent_case_report(summary, reports), encoding="utf-8", newline="\n")
    print(f"wrote={json_output}")
    print(f"wrote={markdown_output}")
    print(f"pass_rate={summary['pass_rate']}")


if __name__ == "__main__":
    main()
