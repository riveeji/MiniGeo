from pathlib import Path

from minigeo.eval.release import check_release_artifacts, format_release_checklist


def main() -> None:
    rows = check_release_artifacts()
    output = Path("results/release_checklist.md")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(format_release_checklist(rows), encoding="utf-8", newline="\n")
    print(f"wrote={output}")
    missing_or_incomplete = [row for row in rows if row["status"] != "ready"]
    if missing_or_incomplete:
        print(f"release_checklist_pending={len(missing_or_incomplete)}")
    else:
        print("release_checklist_ready=true")


if __name__ == "__main__":
    main()
