from sqlalchemy import BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column

BigIntId = BigInteger().with_variant(Integer, "sqlite")

AUTOINCREMENT = {"sqlite_autoincrement": True}


class IdMixin:
    """Gives a table a surrogate BIGINT primary key, as its first column."""

    id: Mapped[int] = mapped_column(
        BigIntId, primary_key=True, autoincrement=True, sort_order=-1
    )
