from pathlib import Path

from sqlalchemy import MetaData, create_engine, event, inspect
from sqlalchemy.engine import Engine

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "cell-count.csv"
DB_PATH = ROOT / "cell_counts.db"


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, _record):
    """Turn on foreign key enforcement for each new SQLite connection. SQLite ignores foreign keys
    unless this is set.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


def get_engine(db_path: Path = DB_PATH) -> Engine:
    """Create an engine for a SQLite file. Defaults to cell_counts.db in the repository root."""
    return create_engine(f"sqlite:///{db_path}")


def rebuild_layer(engine: Engine, metadata: MetaData) -> None:
    """Drop and recreate one layer's tables. Other layers in the same database are left alone."""
    metadata.drop_all(engine)
    metadata.create_all(engine)


def has_layer(engine: Engine, metadata: MetaData) -> bool:
    """Check whether every table in a layer exists. Used to confirm a pipeline step has run."""
    existing = set(inspect(engine).get_table_names())
    return set(metadata.tables) <= existing
