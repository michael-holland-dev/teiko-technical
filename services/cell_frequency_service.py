from typing import List, Optional, Sequence

from sqlalchemy.orm import Session

from models.data import PopulationFrequency
from repos import CellFrequencyRepo


class CellFrequencyService:
    def __init__(self, session: Session):
        self.frequencies = CellFrequencyRepo(session)

    def relative_frequencies(
        self, sample_uuids: Optional[Sequence[str]] = None
    ) -> List[PopulationFrequency]:
        """Return the relative frequency summary table. The calculation is done entirely in the
        repo's query.
        """
        return self.frequencies.relative_frequencies(sample_uuids)
