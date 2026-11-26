from dataclasses import asdict
from typing import Any, Optional, Set, Type

from models.gold import GoldBase


def gold_columns(model: Type[GoldBase]) -> Set[str]:
    """Return a gold table's column names except the surrogate id."""
    return {c.name for c in model.__table__.columns if c.name != "id"}


def to_row(model: Type[GoldBase], obj: Optional[Any] = None, **values: Any) -> dict:
    """Build one insert row for a gold table from a dataclass plus extra values.

    The row's keys must match the table's columns exactly. A field renamed in one place but not
    the other raises here, at pipeline time, instead of dropping a column silently.
    """
    row = {**(asdict(obj) if obj is not None else {}), **values}
    expected = gold_columns(model)
    if set(row) != expected:
        missing, extra = sorted(expected - set(row)), sorted(set(row) - expected)
        raise ValueError(
            f"Row for {model.__tablename__} doesn't match its columns "
            f"(missing: {missing}, unexpected: {extra})"
        )
    return row
