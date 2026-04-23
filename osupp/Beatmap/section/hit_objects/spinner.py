from dataclasses import dataclass
from utils import Pos


@dataclass(frozen=True)
class HitObjectSpinner:
    pos: Pos
    duration: float
    new_combo: bool
