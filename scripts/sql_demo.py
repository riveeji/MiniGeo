from pathlib import Path

from minigeo.sql.generator import RuleBasedSQLGenerator
from minigeo.sql.tools import execute_sql, init_demo_db


def main() -> None:
    db_path = Path("data/processed/minigeo_demo.sqlite")
    init_demo_db(db_path)
    sql = RuleBasedSQLGenerator().generate("秦皇岛样本中被误判最多的预测矿物是什么？")
    print(execute_sql(db_path, sql))


if __name__ == "__main__":
    main()
