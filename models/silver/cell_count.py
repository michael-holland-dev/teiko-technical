from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import AUTOINCREMENT, BigIntId
from .base import SilverBase

if TYPE_CHECKING:
    from .cell_population import CellPopulation
    from .sample import Sample


class CellCount(SilverBase):
    """Raw count of one cell population in one sample (long format)."""

    __tablename__ = "silver_cell_counts"
    __table_args__ = (
        CheckConstraint("count >= 0", name="ck_silver_cell_counts_count"),
        UniqueConstraint("sample_id", "population_id", name="uq_silver_cell_counts_sample_population"),
        AUTOINCREMENT,
    )

    sample_id: Mapped[int] = mapped_column(BigIntId, ForeignKey("silver_samples.id"))
    population_id: Mapped[int] = mapped_column(
        BigIntId, ForeignKey("silver_cell_populations.id"), index=True
    )
    count: Mapped[int]

    sample: Mapped["Sample"] = relationship(back_populates="cell_counts")
    population: Mapped["CellPopulation"] = relationship(back_populates="cell_counts")
