from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import AUTOINCREMENT
from .base import SilverBase

if TYPE_CHECKING:
    from .cell_count import CellCount

POPULATIONS = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]


class CellPopulation(SilverBase):
    """Lookup table of immune cell population names.

    Populations are columns in the spreadsheet, not rows, so they have no
    spreadsheet id. Their unique name is the natural key.
    """

    __tablename__ = "silver_cell_populations"
    __table_args__ = AUTOINCREMENT

    name: Mapped[str] = mapped_column(unique=True)

    cell_counts: Mapped[List["CellCount"]] = relationship(back_populates="population")
