import sys
from dataclasses import dataclass
from typing import Optional

@dataclass
class ControlPointProperties:
    slider_velocity: float = 0.0
    timing_signature: int = 0
    sample_bank: int = 0
    custom_sample_bank: int = 0
    sample_volume: int = 0
    effect_flags: int = 0

    @classmethod
    def default(cls) -> "ControlPointProperties":
        return cls()