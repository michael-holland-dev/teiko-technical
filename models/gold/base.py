from sqlalchemy.orm import DeclarativeBase

from ..base import IdMixin


class GoldBase(IdMixin, DeclarativeBase):
    """Base for the gold layer: precomputed, dashboard-ready tables (gold_* tables).

    Gold tables are flat on purpose: no foreign keys or joins, and
    identifiers are the spreadsheet ids (e.g. "sample00000"). The dashboard
    reads them with simple filtered SELECTs.
    """
