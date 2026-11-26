from dataclasses import fields
from typing import List, Type, TypeVar

from sqlalchemy import Select
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepo:
    def __init__(self, session: Session):
        self.session = session

    def fetch(self, stmt: Select, result_type: Type[T]) -> List[T]:
        """Run a query and build one dataclass per row. Extra columns such as internal ids are
        ignored.
        """
        names = [f.name for f in fields(result_type)]
        return [
            result_type(**{n: row._mapping[n] for n in names})
            for row in self.session.execute(stmt)
        ]
