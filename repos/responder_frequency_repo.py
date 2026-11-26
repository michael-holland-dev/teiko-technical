from typing import List, Literal

from sqlalchemy import Integer, Select, String, cast, func, null, select
from sqlalchemy.orm import Session

from models.silver import Sample, Subject
from models.data import MelPBMCSubset, ResponderFrequency

from .base_repo import BaseRepo
from .cell_frequency_repo import CellFrequencyRepo
from .mel_pbmc_subset_repo import MelPBMCSubsetRepo

Unit = Literal["sample", "subject"]


class ResponderFrequencyRepo(BaseRepo):
    def __init__(self, session: Session):
        super().__init__(session)
        self.frequencies = CellFrequencyRepo(session)
        self.subsets = MelPBMCSubsetRepo(session)

    def responder_frequencies_query(
        self, subset: MelPBMCSubset, unit: Unit = "subject"
    ) -> Select:
        """Build the query for a subset's relative frequencies, tagged with subject and response.
        Per-subject averaging happens in SQL when unit is subject.
        """
        # Only subjects with a recorded response can be compared. The silver CHECK constraint
        # already limits response to RESPONSES or NULL.
        with_response = self.subsets.sample_ids_query(subset).where(
            Subject.response.is_not(None)
        )
        freq = self.frequencies.relative_frequencies_query(with_response).subquery()
        base = (
            select()
            .select_from(freq)
            .join(Sample, Sample.id == freq.c.sample_id)
            .join(Subject, Subject.id == Sample.subject_id)
        )
        if unit == "sample":
            return base.add_columns(
                freq.c.sample,
                Subject.uuid.label("subject"),
                Subject.response,
                Sample.time_from_treatment_start,
                freq.c.population,
                freq.c.percentage,
            ).order_by(freq.c.sample_id, freq.c.population_id)
        if unit == "subject":
            return (
                base.add_columns(
                    cast(null(), String).label("sample"),
                    Subject.uuid.label("subject"),
                    Subject.response,
                    cast(null(), Integer).label("time_from_treatment_start"),
                    freq.c.population,
                    func.avg(freq.c.percentage).label("percentage"),
                )
                .group_by(Subject.id, freq.c.population_id)
                .order_by(Subject.id, freq.c.population_id)
            )
        raise ValueError(f"unit must be 'sample' or 'subject', got {unit!r}")

    def responder_frequencies(
        self, subset: MelPBMCSubset, unit: Unit = "subject"
    ) -> List[ResponderFrequency]:
        """Return a subset's relative frequencies tagged with subject and response. Defaults to one
        row per subject and population.
        """
        return self.fetch(self.responder_frequencies_query(subset, unit), ResponderFrequency)
