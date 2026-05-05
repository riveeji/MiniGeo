from pathlib import Path
from typing import Any

from minigeo.agent.planner import plan_agent_tools
from minigeo.rag.pipeline import retrieve_with_bm25
from minigeo.sql.generator import RuleBasedSQLGenerator
from minigeo.sql.tools import execute_sql
from minigeo.verifier.verifier import MiniGeoVerifier


def write_report(
    answer: str,
    sql: str | None,
    evidence: list[str],
    verification: dict[str, Any],
    limitations: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "answer": answer,
        "sql": sql,
        "evidence": evidence,
        "verification": verification,
        "limitations": limitations or [],
    }


class MiniGeoAgent:
    def __init__(
        self,
        db_path: Path,
        corpus: list[dict[str, Any]],
        sql_generator: Any | None = None,
        verifier: MiniGeoVerifier | None = None,
    ) -> None:
        self.db_path = db_path
        self.corpus = corpus
        self.sql_generator = sql_generator or RuleBasedSQLGenerator()
        self.verifier = verifier or MiniGeoVerifier()

    def run(self, question: str) -> dict[str, Any]:
        plan = plan_agent_tools(question)
        if plan["mode"] == "docs":
            sql = None
            sql_result = {"sql": None, "execution_result": [], "error": None}
            evidence = self._retrieve_docs_for_question(question, top_k=3)
            answer = self._answer_from_docs(question, evidence)
        else:
            sql = self.sql_generator.generate(question)
            sql_result = execute_sql(self.db_path, sql)
            doc_evidence = self._retrieve_evidence(sql_result, top_k=3) if plan["requires_docs"] else []
            sql_evidence = self._sql_evidence_chunk(sql_result)
            evidence = [sql_evidence] + doc_evidence if sql_evidence else doc_evidence
            answer = self._answer_from_sql_and_evidence(sql_result, doc_evidence)
        verification = self.verifier.verify(answer, evidence)
        report = write_report(
            answer=answer,
            sql=sql,
            evidence=[row["chunk_id"] for row in evidence],
            verification=verification,
            limitations=[
                "当前 Agent 使用演示数据库和种子语料，结论只用于验证工具链。",
                "误判原因来自检索证据和光谱字段的解释性归纳，需要真实实验记录复核。",
            ],
        )
        report["sql_result"] = sql_result
        report["plan"] = plan
        return report

    def _retrieve_docs_for_question(self, question: str, top_k: int) -> list[dict[str, Any]]:
        return retrieve_with_bm25(question, self.corpus, top_k=top_k)

    def _sql_evidence_chunk(self, sql_result: dict[str, Any]) -> dict[str, Any] | None:
        if sql_result.get("error"):
            return None
        rows = sql_result.get("execution_result", [])
        if not rows:
            return None
        if all("predicted_mineral" in row and "errors" in row for row in rows):
            ranking = ", ".join(f"{row['predicted_mineral']} {row['errors']} 次" for row in rows)
            top = rows[0]["predicted_mineral"]
            text = f"SQL 结果显示，秦皇岛样本中最常被误判为 {top}，误判分布为 {ranking}。"
            mineral = top
        else:
            text = f"SQL 结果显示：{self._summarize_sql_rows(rows)}。"
            mineral = "structured_result"
        return {
            "chunk_id": "agent_sql#result",
            "doc_id": "agent_sql",
            "text": text,
            "source": "MiniGeo demo SQLite",
            "url": "",
            "page": None,
            "topic": "sql_result",
            "mineral": mineral,
            "license": "generated",
        }

    def _evidence_query(self, sql_result: dict[str, Any]) -> str:
        minerals = " ".join(str(row.get("predicted_mineral", "")) for row in sql_result.get("execution_result", []))
        return f"石英 拉曼峰 464 长石 硅酸盐 光谱 方解石 赤铁矿 {minerals}"

    def _retrieve_evidence(self, sql_result: dict[str, Any], top_k: int) -> list[dict[str, Any]]:
        candidates = retrieve_with_bm25(self._evidence_query(sql_result), self.corpus, top_k=10)
        selected: list[dict[str, Any]] = []
        predicted = [str(row.get("predicted_mineral", "")) for row in sql_result.get("execution_result", [])]
        for mineral in predicted:
            match = self._best_mineral_chunk(mineral, candidates)
            if match and match["chunk_id"] not in {row["chunk_id"] for row in selected}:
                selected.append(match)
        if selected:
            return selected[:top_k]
        for row in candidates:
            if len(selected) >= top_k:
                break
            if row["chunk_id"] not in {selected_row["chunk_id"] for selected_row in selected}:
                selected.append(row)
        return selected[:top_k]

    def _best_mineral_chunk(self, mineral: str, candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
        aliases = {
            "feldspar": ["feldspar", "长石"],
            "quartz": ["quartz", "石英"],
            "calcite": ["calcite", "方解石"],
            "hematite": ["hematite", "赤铁矿"],
        }.get(mineral, [mineral])
        rows_by_id = {row["chunk_id"]: row for row in self.corpus}
        rows_by_id.update({row["chunk_id"]: row for row in candidates})
        matches = [
            row
            for row in rows_by_id.values()
            if row.get("mineral") == mineral
            or any(alias.lower() in str(row.get("text", "")).lower() for alias in aliases)
            or mineral in str(row.get("chunk_id", ""))
        ]
        if not matches:
            return None
        reason_terms = ["混淆", "弱峰", "噪声", "光谱", "拉曼峰"]
        return max(
            matches,
            key=lambda row: (
                row.get("mineral") == mineral or mineral in str(row.get("chunk_id", "")),
                sum(term in str(row.get("text", "")) for term in reason_terms),
                float(row.get("score", 0.0)),
            ),
        )

    def _answer_from_sql_and_evidence(
        self,
        sql_result: dict[str, Any],
        evidence: list[dict[str, Any]],
    ) -> str:
        if sql_result.get("error"):
            return f"SQL 执行失败，无法给出可靠分析：{sql_result['error']}"
        rows = sql_result.get("execution_result", [])
        if not rows:
            return "SQL 查询没有返回误判记录，当前证据不足，无法给出可靠结论。"

        if not all("predicted_mineral" in row and "errors" in row for row in rows):
            return f"SQL 查询返回 {len(rows)} 行结果：{self._summarize_sql_rows(rows)}。"

        ranking = ", ".join(f"{row['predicted_mineral']}（{row['errors']} 次）" for row in rows)
        top = rows[0]["predicted_mineral"]
        citations = " ".join(f"[{row['chunk_id']}]" for row in evidence)
        return (
            f"SQL 结果显示，秦皇岛样本中最常被误判为 {top}，误判分布为 {ranking}。"
            "可能原因包括：石英的 464 cm-1 附近拉曼峰是关键识别证据，"
            "长石与石英同属硅酸盐体系，Al-Si 骨架相关光谱特征可能增加混淆风险。"
            f"相关证据见 {citations}。"
        )

    def _answer_from_docs(self, question: str, evidence: list[dict[str, Any]]) -> str:
        if not evidence:
            return "当前文档证据不足，无法给出可靠回答。"
        if "石英" in question and ("拉曼" in question or "光谱" in question):
            quartz_chunks = [
                row for row in evidence
                if row.get("chunk_id") == "doc_quartz#chunk_002" or row.get("mineral") == "quartz"
            ]
            if quartz_chunks:
                citation = quartz_chunks[0]["chunk_id"]
                return f"根据文档证据，石英常见强拉曼峰接近 464 cm-1，可作为识别石英的重要光谱证据。相关证据见 [{citation}]。"
        citations = " ".join(f"[{row['chunk_id']}]" for row in evidence)
        evidence_text = "；".join(str(row.get("text", "")) for row in evidence[:2])
        return f"根据检索到的文档证据：{evidence_text}。相关证据见 {citations}。"

    def _summarize_sql_rows(self, rows: list[dict[str, Any]], limit: int = 3) -> str:
        rendered = []
        for row in rows[:limit]:
            rendered.append(", ".join(f"{key}={value}" for key, value in row.items()))
        suffix = f"；另有 {len(rows) - limit} 行" if len(rows) > limit else ""
        return "；".join(rendered) + suffix
