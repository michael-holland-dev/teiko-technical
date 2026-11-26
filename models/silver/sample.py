from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import AUTOINCREMENT, BigIntId
from .base import SilverBase

if TYPE_CHECKING:
    from .cell_count import CellCount
    from .subject import Subject


class Sample(SilverBase):
    """A biological sample taken from a subject at a point in time."""

    __tablename__ = "silver_samples"
    __table_args__ = (
        Index("idx_silver_samples_type_time", "sample_type", "time_from_treatment_start"),
        AUTOINCREMENT,
    )

    uuid: Mapped[str] = mapped_column(String, unique=True)
    subject_id: Mapped[int] = mapped_column(
        BigIntId, ForeignKey("silver_subjects.id"), index=True
    )
    sample_type: Mapped[str]
    time_from_treatment_start: Mapped[Optional[int]]

    subject: Mapped["Subject"] = relationship(back_populates="samples")
    cell_counts: Mapped[List["CellCount"]] = relationship(back_populates="sample")
