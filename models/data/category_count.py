from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CategoryCount:
    """How many rows fall into one category, e.g. project "prj1" -> 384."""

    category: Optional[str]
    count: int
