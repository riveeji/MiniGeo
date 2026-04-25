from pathlib import Path

from minigeo.agent.simple_agent import write_report
from minigeo.rag.corpus import load_corpus
from minigeo.rag.pipeline import retrieve_with_bm25
from minigeo.sql.generator import RuleBasedSQLGenerator
from minigeo.sql.tools import execute_sql, init_demo_db
from minigeo.verifier.simple import verify_answer


def main() -> None:
    question = "秦皇岛样本中哪些矿物类别最常被误判，可能原因是什么？"
    db_path = Path("data/processed/minigeo_demo.sqlite")
    init_demo_db(db_path)
    sql = RuleBasedSQLGenerator().generate(question)
    sql_result = execute_sql(db_path, sql)
    corpus = load_corpus(Path("data/processed/rag_corpus.jsonl"))
    evidence = retrieve_with_bm25("石英 长石 光谱 混淆 弱峰 噪声", corpus, top_k=3)
    answer = "秦皇岛错误预测以 feldspar 为主，可能与石英弱峰、长石框架振动接近和噪声有关。"
    verification = verify_answer(answer, evidence)
    report = write_report(
        answer=answer,
        sql=sql,
        evidence=[row["chunk_id"] for row in evidence],
        verification=verification,
        limitations=["演示数据库规模很小，结果只用于验证管线。"],
    )
    report["sql_result"] = sql_result
    print(report)


if __name__ == "__main__":
    main()

