from dataclasses import dataclass
from utils import Pos

@dataclass(frozen=True)
class HitObjectCircle:
    pos: Pos
    new_combo: bool
    combo_offset: int