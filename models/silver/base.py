from sqlalchemy.orm import DeclarativeBase

from ..base import IdMixin


class SilverBase(IdMixin, DeclarativeBase):
    """Base for the silver layer: cleaned, normalized tables (silver_* tables).

    Foreign keys always reference `id`. Identifiers that come from the
    source spreadsheet (e.g. "sbj000") are stored separately in a unique
    `uuid` column.
    """
