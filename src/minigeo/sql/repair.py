import re


def repair_sql(sql: str, error: str = "") -> str:
    repaired = sql
    replacements = {
        r"\bprediction\b": "predicted_mineral",
        r"\bpredicted\b": "predicted_mineral",
        r"\bcorrect\b": "is_correct",
    }
    for pattern, replacement in replacements.items():
        repaired = re.sub(pattern, replacement, repaired, flags=re.IGNORECASE)

    lower = repaired.lower()
    if "join samples" in lower and "samples.sample_id = predictions.sample_id" not in lower:
        repaired = re.sub(
            r"join\s+samples(?:\s+where)?",
            "join samples on samples.sample_id = predictions.sample_id where",
            repaired,
            count=1,
            flags=re.IGNORECASE,
        )
        repaired = repaired.replace("where where", "where")

    if "no such table" in error.lower() and "prediction " in lower:
        repaired = re.sub(r"\bprediction\b", "predictions", repaired, flags=re.IGNORECASE)
    return repaired

