from pathlib import Path
import json

from minigeo.agent.simple_agent import MiniGeoAgent
from minigeo.rag.corpus import load_corpus
from minigeo.sql.tools import init_demo_db


def main() -> None:
    question = (
        "Analyze which mineral categories are most frequently misclassified in samples collected from Qinhuangdao, "
        "and explain possible causes using spectral evidence."
    )
    db_path = Path("data/processed/minigeo_demo.sqlite")
    init_demo_db(db_path)
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))
    report = MiniGeoAgent(db_path=db_path, corpus=corpus).run(question)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
