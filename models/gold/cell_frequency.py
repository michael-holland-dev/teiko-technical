from typing import Optional

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column

from ..base import AUTOINCREMENT
from .base import GoldBase


class GoldCellFrequency(GoldBase):
    """Relative frequency of each population in each sample."""

    __tablename__ = "gold_cell_frequencies"
    __table_args__ = (
        Index("idx_gold_cell_frequencies_sample", "sample"),
        Index("idx_gold_cell_frequencies_population", "population"),
        AUTOINCREMENT,
    )

    sample: Mapped[str] = mapped_column(String)
    total_count: Mapped[int]
    population: Mapped[str] = mapped_column(String)
    count: Mapped[int]
    percentage: Mapped[Optional[float]]
