from sqlalchemy.orm import DeclarativeBase

from ..base import IdMixin


class BronzeBase(IdMixin, DeclarativeBase):
    """Base for the bronze layer: raw data exactly as received (bronze_* tables)."""
