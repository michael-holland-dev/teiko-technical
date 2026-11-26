from typing import Iterable, List

from models.data import PopulationFrequency, ResponderFrequency
from models.gold import GoldCellFrequency, GoldResponderFrequency
from repos import Unit

from .base_serializer import to_row


def cell_frequency_rows(frequencies: Iterable[PopulationFrequency]) -> List[dict]:
    """Turn per-sample population frequencies into gold_cell_frequencies rows."""
    return [to_row(GoldCellFrequency, f) for f in frequencies]


def responder_frequency_rows(unit: Unit, frequencies: Iterable[ResponderFrequency]) -> List[dict]:
    """Turn responder frequencies into gold_responder_frequencies rows, tagged with their unit."""
    return [to_row(GoldResponderFrequency, f, unit=unit) for f in frequencies]
