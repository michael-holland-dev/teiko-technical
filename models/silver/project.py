from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import AUTOINCREMENT
from .base import SilverBase

if TYPE_CHECKING:
    from .subject import Subject


class Project(SilverBase):
    __tablename__ = "silver_projects"
    __table_args__ = AUTOINCREMENT

    uuid: Mapped[str] = mapped_column(String, unique=True)

    subjects: Mapped[List["Subject"]] = relationship(back_populates="project")
