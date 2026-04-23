from dataclasses import dataclass


@dataclass(frozen=True)
class HitObjectHold:
    pos_x: float
    duration: float
