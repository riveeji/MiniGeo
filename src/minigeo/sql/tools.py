import sqlite3
from pathlib import Path
from typing import Any


def init_demo_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.executescript(
            """
            drop table if exists spectra;
            drop table if exists predictions;
            drop table if exists samples;
            drop table if exists minerals;

            create table minerals (
                mineral_id integer primary key,
                name text not null,
                mineral_class text not null,
                key_spectral_feature text not null
            );

            create table samples (
                sample_id integer primary key,
                region text not null,
                true_mineral text not null
            );

            create table predictions (
                prediction_id integer primary key,
                sample_id integer not null,
                predicted_mineral text not null,
                is_correct integer not null,
                foreign key(sample_id) references samples(sample_id)
            );

            create table spectra (
                spectrum_id integer primary key,
                sample_id integer not null,
                peak_cm1 real not null,
                note text not null,
                foreign key(sample_id) references samples(sample_id)
            );
            """
        )
        conn.executemany(
            "insert into minerals(name, mineral_class, key_spectral_feature) values (?, ?, ?)",
            [
                ("quartz", "silicate", "Raman peak near 464 cm-1"),
                ("feldspar", "silicate", "Al-Si framework bands"),
                ("calcite", "carbonate", "carbonate band near 1085 cm-1"),
                ("hematite", "oxide", "iron oxide spectral bands"),
            ],
        )
        conn.executemany(
            "insert into samples(sample_id, region, true_mineral) values (?, ?, ?)",
            [
                (1, "Qinhuangdao", "quartz"),
                (2, "Qinhuangdao", "quartz"),
                (3, "Qinhuangdao", "calcite"),
                (4, "Qinhuangdao", "hematite"),
                (5, "Beijing", "quartz"),
            ],
        )
        conn.executemany(
            "insert into predictions(sample_id, predicted_mineral, is_correct) values (?, ?, ?)",
            [
                (1, "feldspar", 0),
                (2, "feldspar", 0),
                (3, "calcite", 1),
                (4, "quartz", 0),
                (5, "quartz", 1),
            ],
        )
        conn.executemany(
            "insert into spectra(sample_id, peak_cm1, note) values (?, ?, ?)",
            [
                (1, 464.0, "quartz-like Raman peak is weak and overlaps with feldspar framework bands"),
                (2, 462.5, "quartz peak is present but baseline noise is high"),
                (3, 1085.0, "carbonate band supports calcite"),
                (4, 225.0, "iron oxide bands support hematite"),
            ],
        )


def schema_text(conn: sqlite3.Connection) -> str:
    rows = conn.execute(
        "select name, sql from sqlite_master where type = 'table' and name not like 'sqlite_%' order by name"
    ).fetchall()
    return "\n".join(f"{name}: {sql}" for name, sql in rows)


def execute_sql(db_path: Path, sql: str) -> dict[str, Any]:
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql).fetchall()
            return {
                "sql": sql,
                "execution_result": [dict(row) for row in rows],
                "error": None,
            }
    except sqlite3.Error as exc:
        return {"sql": sql, "execution_result": [], "error": str(exc)}

