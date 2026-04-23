from __future__ import annotations
import bisect
from dataclasses import dataclass
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from section.timing_points.decode import ControlPoints


@dataclass
class DifficultyPoint:
    time: float
    slider_velocity: float
    generate_ticks: bool

    DEFAULT_SLIDER_VELOCITY: float = 1.0
    DEFAULT_GENERATE_TICKS: bool = True

    @classmethod
    def default(cls) -> "DifficultyPoint":
        return cls(
            time=0.0,
            slider_velocity=cls.DEFAULT_SLIDER_VELOCITY,
            generate_ticks=cls.DEFAULT_GENERATE_TICKS,
        )

    @classmethod
    def new(
        cls, time: float, beat_len: float, speed_multiplier: float
    ) -> "DifficultyPoint":
        sv = max(0.1, min(10.0, speed_multiplier))

        return cls(
            time=time, slider_velocity=sv, generate_ticks=not math.isnan(beat_len)
        )

    def check_already_existing(self, control_points: "ControlPoints") -> bool:
        existing = control_points.difficulty_point_at(self.time)
        if existing is not None:
            return self.is_redundant(existing)

        return self.is_redundant(DifficultyPoint.default())

    def add_to(self, control_points: "ControlPoints") -> None:
        points = control_points.difficulty_points

        idx = bisect.bisect_left(points, self.time, key=lambda p: p.time)

        if idx < len(points) and points[idx].time == self.time:
            points[idx] = self
        else:
            points.insert(idx, self)

    def is_redundant(self, existing: "DifficultyPoint") -> bool:
        return (
            self.generate_ticks == existing.generate_ticks
            and abs(self.slider_velocity - existing.slider_velocity) < 1e-9
        )

    def __lt__(self, other: "DifficultyPoint") -> bool:
        if not isinstance(other, DifficultyPoint):
            return NotImplemented
        return self.time < other.time

    def __le__(self, other: "DifficultyPoint") -> bool:
        return self.time <= other.time

    def __gt__(self, other: "DifficultyPoint") -> bool:
        return self.time > other.time

    def __ge__(self, other: "DifficultyPoint") -> bool:
        return self.time >= other.time
