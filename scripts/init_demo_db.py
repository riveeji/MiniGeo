from pathlib import Path

from minigeo.sql.tools import init_demo_db


def main() -> None:
    db_path = Path("data/processed/minigeo_demo.sqlite")
    init_demo_db(db_path)
    print(f"created={db_path}")


if __name__ == "__main__":
    main()

