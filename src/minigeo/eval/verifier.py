from collections import Counter
from typing import Any


def summarize_verification_reports(reports: list[dict[str, Any]], latency_ms: float | None = None) -> dict[str, Any]:
    verdicts: Counter[str] = Counter()
    statuses: Counter[str] = Counter()
    claim_count = 0
    for report in reports:
        verdicts.update([report.get("verdict", "unknown")])
        claims = report.get("claims", [])
        claim_count += len(claims)
        statuses.update(claim.get("status", "unknown") for claim in claims)
    summary = {
        "reports": len(reports),
        "claims": claim_count,
        "verdicts": dict(verdicts),
        "statuses": dict(statuses),
        "unsupported_claim_rate": unsupported_claim_rate(reports),
    }
    if latency_ms is not None:
        summary["latency_ms"] = latency_ms
    return summary


def unsupported_claim_rate(reports: list[dict[str, Any]]) -> float:
    total = 0
    unsupported = 0
    for report in reports:
        for claim in report.get("claims", []):
            total += 1
            if claim.get("status") != "supported":
                unsupported += 1
    if total == 0:
        return 0.0
    return unsupported / total
