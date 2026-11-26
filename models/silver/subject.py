from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import AUTOINCREMENT, BigIntId
from .base import SilverBase

if TYPE_CHECKING:
    from .project import Project
    from .sample import Sample

RESPONDER = "yes"
NON_RESPONDER = "no"
RESPONSES = (RESPONDER, NON_RESPONDER)

MALE = "M"
FEMALE = "F"
SEXES = (MALE, FEMALE)


def _in(column: str, values) -> str:
    """Build a CHECK constraint expression limiting a column to the given values."""
    return f"{column} IN ({', '.join(repr(v) for v in values)})"


class Subject(SilverBase):
    """A patient. These attributes are constant across the subject's samples."""

    __tablename__ = "silver_subjects"
    __table_args__ = (
        CheckConstraint(_in("sex", SEXES), name="ck_silver_subjects_sex"),
        CheckConstraint(_in("response", RESPONSES), name="ck_silver_subjects_response"),
        Index("idx_silver_subjects_condition_treatment", "condition", "treatment"),
        AUTOINCREMENT,
    )

    uuid: Mapped[str] = mapped_column(String, unique=True)
    project_id: Mapped[int] = mapped_column(
        BigIntId, ForeignKey("silver_projects.id"), index=True
    )
    condition: Mapped[str]
    age: Mapped[Optional[int]]
    sex: Mapped[Optional[str]]
    treatment: Mapped[str]
    response: Mapped[Optional[str]]

    project: Mapped["Project"] = relationship(back_populates="subjects")
    samples: Mapped[List["Sample"]] = relationship(back_populates="subject")
