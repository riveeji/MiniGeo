from pathlib import Path

from minigeo.sql.tools import execute_sql, init_demo_db


def main() -> None:
    db_path = Path("data/processed/minigeo_demo.sqlite")
    init_demo_db(db_path)
    sql = (
        "select predicted_mineral, count(*) as errors from predictions "
        "join samples on samples.sample_id = predictions.sample_id "
        "where samples.region = 'Qinhuangdao' and is_correct = 0 "
        "group by predicted_mineral order by errors desc"
    )
    print(execute_sql(db_path, sql))


if __name__ == "__main__":
    main()

