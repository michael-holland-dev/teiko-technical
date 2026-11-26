from datetime import datetime

from sqlalchemy import Index, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..base import AUTOINCREMENT
from .base import BronzeBase

CSV_COLUMNS = [
    "project",
    "subject",
    "condition",
    "age",
    "sex",
    "treatment",
    "response",
    "sample",
    "sample_type",
    "time_from_treatment_start",
    "b_cell",
    "cd8_t_cell",
    "cd4_t_cell",
    "nk_cell",
    "monocyte",
]


class RawCellCount(BronzeBase):
    """One row of cell-count.csv, untouched.

    Every value is stored as the text that was in the file (blank stays "")
    with no types, constraints or cleaning. Those happen on the way to
    silver. Lineage columns record where and when each row came from, so any
    silver or gold value can be traced back to its line in the source file.
    """

    __tablename__ = "bronze_raw_cell_counts"
    __table_args__ = (
        Index("idx_bronze_raw_cell_counts_source", "source_file", "source_row"),
        AUTOINCREMENT,
    )

    source_file: Mapped[str] = mapped_column(Text)
    source_row: Mapped[int]
    loaded_at: Mapped[datetime]

    project: Mapped[str] = mapped_column(Text)
    subject: Mapped[str] = mapped_column(Text)
    condition: Mapped[str] = mapped_column(Text)
    age: Mapped[str] = mapped_column(Text)
    sex: Mapped[str] = mapped_column(Text)
    treatment: Mapped[str] = mapped_column(Text)
    response: Mapped[str] = mapped_column(Text)
    sample: Mapped[str] = mapped_column(Text)
    sample_type: Mapped[str] = mapped_column(Text)
    time_from_treatment_start: Mapped[str] = mapped_column(Text)
    b_cell: Mapped[str] = mapped_column(Text)
    cd8_t_cell: Mapped[str] = mapped_column(Text)
    cd4_t_cell: Mapped[str] = mapped_column(Text)
    nk_cell: Mapped[str] = mapped_column(Text)
    monocyte: Mapped[str] = mapped_column(Text)
