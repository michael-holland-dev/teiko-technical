from typing import Optional

from sqlalchemy import Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..base import AUTOINCREMENT
from .base import GoldBase


class GoldMelPBMCSubsetSample(GoldBase):
    """The samples in each summary melanoma PBMC subset, one row per (subset, sample).

    The subset's own filters (treatment and timepoint, plus melanoma and PBMC) are not repeated
    on every row; they are defined once in models.data.mel_pbmc_subset.
    """

    __tablename__ = "gold_mel_pbmc_subset_samples"
    __table_args__ = (
        UniqueConstraint("subset", "sample", name="uq_gold_mel_pbmc_subset_samples"),
        Index("idx_gold_mel_pbmc_subset_samples_subset_project", "subset", "project"),
        AUTOINCREMENT,
    )

    subset: Mapped[str] = mapped_column(String)
    sample: Mapped[str] = mapped_column(String)
    subject: Mapped[str]
    project: Mapped[str]
    response: Mapped[Optional[str]]
    sex: Mapped[Optional[str]]
    age: Mapped[Optional[int]]
