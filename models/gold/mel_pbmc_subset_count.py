from enum import Enum
from typing import Optional

from sqlalchemy import CheckConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..base import AUTOINCREMENT
from .base import GoldBase


class Breakdown(str, Enum):
    """How a subset count row is grouped. TOTAL rows have no category."""

    TOTAL = "total"
    PROJECT = "project"
    RESPONSE = "response"
    SEX = "sex"


class Counted(str, Enum):
    """What a subset count row counts."""

    SAMPLES = "samples"
    SUBJECTS = "subjects"


def _in(column: str, enum) -> str:
    """Build a CHECK constraint expression limiting a column to an enum's values."""
    return f"{column} IN ({', '.join(repr(m.value) for m in enum)})"


class GoldMelPBMCSubsetCount(GoldBase):
    """Breakdowns of each summary melanoma PBMC subset, as (subset, breakdown, counted, category,
    count).

    For example ("miraclib_day0", "project", "samples", "prj1", 384) or
    ("miraclib_day0", "response", "subjects", "yes", 331). breakdown="total" rows
    hold the overall sample and subject counts, with no category. In the other
    breakdowns, category None means the subject has no recorded value.
    """

    __tablename__ = "gold_mel_pbmc_subset_counts"
    __table_args__ = (
        CheckConstraint(_in("breakdown", Breakdown), name="ck_gold_mel_pbmc_subset_counts_breakdown"),
        CheckConstraint(_in("counted", Counted), name="ck_gold_mel_pbmc_subset_counts_counted"),
        UniqueConstraint(
            "subset", "breakdown", "counted", "category", name="uq_gold_mel_pbmc_subset_counts"
        ),
        AUTOINCREMENT,
    )

    subset: Mapped[str] = mapped_column(String)
    breakdown: Mapped[str] = mapped_column(String)
    counted: Mapped[str] = mapped_column(String)
    category: Mapped[Optional[str]]
    count: Mapped[int]
