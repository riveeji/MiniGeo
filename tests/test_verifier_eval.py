from minigeo.eval.verifier import summarize_verification_reports, unsupported_claim_rate


def test_summarize_verification_reports_counts_statuses() -> None:
    reports = [
        {"verdict": "supported", "claims": [{"status": "supported"}, {"status": "supported"}]},
        {"verdict": "insufficient_evidence", "claims": [{"status": "insufficient"}]},
    ]

    summary = summarize_verification_reports(reports)

    assert summary["reports"] == 2
    assert summary["claims"] == 3
    assert summary["statuses"] == {"supported": 2, "insufficient": 1}
    assert summary["verdicts"] == {"supported": 1, "insufficient_evidence": 1}


def test_summarize_verification_reports_accepts_latency() -> None:
    summary = summarize_verification_reports(
        [{"verdict": "supported", "claims": [{"status": "supported"}]}],
        latency_ms=12.5,
    )

    assert summary["latency_ms"] == 12.5


def test_unsupported_claim_rate_counts_non_supported_claims() -> None:
    reports = [
        {"claims": [{"status": "supported"}, {"status": "insufficient"}, {"status": "contradicted"}]},
    ]

    assert unsupported_claim_rate(reports) == 2 / 3
