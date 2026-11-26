import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from sqlalchemy.engine import Engine

from lib.database import CSV_PATH, DB_PATH, get_engine, rebuild_layer
from models.bronze import CSV_COLUMNS, BronzeBase, RawCellCount
from models.silver import (
    POPULATIONS,
    CellCount,
    CellPopulation,
    Project,
    Sample,
    SilverBase,
    Subject,
)


def build_bronze(engine: Engine, csv_path: Path = CSV_PATH) -> int:
    """Copy every row of cell-count.csv into the bronze table as raw text. Returns the number of
    rows loaded.
    """
    loaded_at = datetime.now(timezone.utc).replace(tzinfo=None)
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        missing = set(CSV_COLUMNS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{csv_path.name} is missing columns: {sorted(missing)}")
        rows = [
            {
                "source_file": csv_path.name,
                "source_row": i,
                "loaded_at": loaded_at,
                **{c: row[c] for c in CSV_COLUMNS},
            }
            for i, row in enumerate(reader, start=1)
        ]

    rebuild_layer(engine, BronzeBase.metadata)
    with Session(engine) as session, session.begin():
        session.execute(insert(RawCellCount), rows)
    return len(rows)


def null_if_blank(value):
    """Strip a string and return None if it is empty. Otherwise returns the stripped value."""
    value = value.strip()
    return value if value else None


def int_or_none(value):
    """Parse a string as an integer. Returns None if it is blank."""
    value = value.strip()
    return int(value) if value else None


def read_bronze(engine: Engine):
    """Read bronze rows, clean their values and split them into rows for each silver table. Raises
    an error if a subject's details disagree across samples.
    """
    projects: List[str] = []
    subjects: Dict[str, dict] = {}
    samples: List[dict] = []
    counts: List[dict] = []

    with Session(engine) as session:
        raw_rows = session.scalars(select(RawCellCount).order_by(RawCellCount.source_row))
        for raw in raw_rows:
            where = f"{raw.source_file} row {raw.source_row}"
            if raw.project not in projects:
                projects.append(raw.project)
            subject = {
                "uuid": raw.subject,
                "project": raw.project,
                "condition": raw.condition,
                "age": int_or_none(raw.age),
                "sex": null_if_blank(raw.sex),
                "treatment": raw.treatment,
                "response": null_if_blank(raw.response),
            }
            if subjects.setdefault(raw.subject, subject) != subject:
                raise ValueError(
                    f"Subject {raw.subject} has conflicting attributes across samples ({where})"
                )
            samples.append(
                {
                    "uuid": raw.sample,
                    "subject": raw.subject,
                    "sample_type": raw.sample_type,
                    "time_from_treatment_start": int_or_none(raw.time_from_treatment_start),
                }
            )
            for pop in POPULATIONS:
                counts.append(
                    {"sample": raw.sample, "population": pop, "count": int(getattr(raw, pop))}
                )
    return projects, list(subjects.values()), samples, counts


def id_map(session: Session, key_column) -> Dict[str, int]:
    """Map each natural key to the database id assigned on insert. Used to fill in foreign keys for
    child tables.
    """
    model = key_column.class_
    return {key: id_ for key, id_ in session.execute(select(key_column, model.id))}


def without(row: dict, key: str) -> dict:
    """Return a copy of a dict without one key. Used to drop natural keys before insert."""
    return {k: v for k, v in row.items() if k != key}


def load_silver(session: Session, projects, subjects, samples, counts) -> Dict[str, int]:
    """Insert the silver tables, parents first, filling in foreign keys from the parents' ids.
    Returns row counts per table.
    """
    session.execute(insert(Project), [{"uuid": p} for p in projects])
    session.execute(insert(CellPopulation), [{"name": p} for p in POPULATIONS])
    project_ids = id_map(session, Project.uuid)
    population_ids = id_map(session, CellPopulation.name)

    session.execute(
        insert(Subject),
        [{**without(s, "project"), "project_id": project_ids[s["project"]]} for s in subjects],
    )
    subject_ids = id_map(session, Subject.uuid)

    session.execute(
        insert(Sample),
        [{**without(s, "subject"), "subject_id": subject_ids[s["subject"]]} for s in samples],
    )
    sample_ids = id_map(session, Sample.uuid)

    session.execute(
        insert(CellCount),
        [
            {
                "sample_id": sample_ids[c["sample"]],
                "population_id": population_ids[c["population"]],
                "count": c["count"],
            }
            for c in counts
        ],
    )
    return {
        Project.__tablename__: len(projects),
        CellPopulation.__tablename__: len(POPULATIONS),
        Subject.__tablename__: len(subjects),
        Sample.__tablename__: len(samples),
        CellCount.__tablename__: len(counts),
    }


def build_silver(engine: Engine) -> Dict[str, int]:
    """Rebuild the silver tables from bronze. Returns row counts per table."""
    data = read_bronze(engine)
    rebuild_layer(engine, SilverBase.metadata)
    with Session(engine) as session, session.begin():
        return load_silver(session, *data)


def main():
    """Build the bronze and silver layers in cell_counts.db. Prints the row count for each table.
    """
    engine = get_engine(DB_PATH)
    n_raw = build_bronze(engine)
    row_counts = build_silver(engine)
    engine.dispose()

    print(f"Loaded {DB_PATH.name}")
    print("  bronze")
    print(f"    {RawCellCount.__tablename__ + ':':<26}{n_raw}")
    print("  silver")
    for table, n in row_counts.items():
        print(f"    {table + ':':<26}{n}")


if __name__ == "__main__":
    main()
