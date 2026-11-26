from typing import Optional

from sqlalchemy import CheckConstraint, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from ..base import AUTOINCREMENT
from .base import GoldBase


class GoldResponderFrequency(GoldBase):
    """Frequencies of responders vs non-responders.

    Stored at both levels. unit="sample" has one row per (sample,
    population); unit="subject" averages each patient's samples into one.
    """

    __tablename__ = "gold_responder_frequencies"
    __table_args__ = (
        CheckConstraint("unit IN ('sample', 'subject')", name="ck_gold_responder_frequencies_unit"),
        Index("idx_gold_responder_frequencies_unit_population", "unit", "population"),
        AUTOINCREMENT,
    )

    unit: Mapped[str] = mapped_column(String)
    sample: Mapped[Optional[str]]
    subject: Mapped[str]
    response: Mapped[str]
    time_from_treatment_start: Mapped[Optional[int]]
    population: Mapped[str]
    percentage: Mapped[Optional[float]]
