from utils import Pos
from .path import PathControlPoint, SliderPath
from section.hit_objects.hit_samples import HitSampleInfo
from .curve import Curve, CurveBuffers, CircularArcProperties
from .path_type import PathType, SplineType

from typing import List, Optional

__all__ = [
    "PathControlPoint",
    "SliderPath",
    "Curve",
    "BorrowedCurve",
    "CurveBuffers",
    "CircularArcProperties",
    "PathType",
    "SplineType",
    "HitObjectSlider",
]

class HitObjectSlider:
    def __init__(
            self,
            pos: Pos,
            new_combo: bool,
            combo_offset: int,
            path: SliderPath,
            node_samples: List[List['HitSampleInfo']],
            repeat_count: int,
            velocity: float,
    ):
        self.pos = pos
        self.new_combo = new_combo
        self.combo_offset = combo_offset
        self.path = path
        self.node_samples = node_samples
        self.repeat_count = repeat_count
        self.velocity = velocity

    def span_count(self) -> int:
        return self.repeat_count + 1

    def duration(self) -> float:
        return self.duration_with_bufs(CurveBuffers())

    def duration_with_bufs(self, bufs: CurveBuffers) -> float:
        curve = self.path.get_curve_with_bufs(bufs)
        return float(self.span_count()) * curve.dist() / self.velocity