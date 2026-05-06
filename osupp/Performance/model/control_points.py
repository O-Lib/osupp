import math
from bisect import bisect_right
from dataclasses import dataclass


@dataclass(slots=True)
class TimingPoint:
    time: float
    beat_len: float

    @property
    def bpm(self) -> float:
        return 60000.0 / self.beat_len if self.beat_len != 0 else 0.0


@dataclass(slots=True)
class DifficultyPoint:
    time: float
    slider_velocity: float
    bpm_multiplier: float
    generate_ticks: bool

    @classmethod
    def new(cls, time: float, beat_len: float, speed_multiplier: float) -> "DifficultyPoint":
        slider_velocity = max(0.1, min(10.0, speed_multiplier))

        if beat_len < 0.0:
            bpm_multiplier = max(10.0, min(10000.0, -beat_len)) / 100.0
        else:
            bpm_multiplier = 1.0

        return cls(
            time=time,
            slider_velocity=slider_velocity,
            bpm_multiplier=bpm_multiplier,
            generate_ticks=not math.isnan(beat_len)
        )


@dataclass(slots=True)
class EffectPoint:
    time: float
    kiai: bool
    scroll_speed: float


def timing_point_at(points: list[TimingPoint], time: float) -> TimingPoint | None:
    if not points:
        return None

    idx = bisect_right(points, time, key=lambda p: p.time)
    return points[idx - 1] if idx > 0 else points[0]


def difficulty_point_at(points: list[DifficultyPoint], time: float) -> DifficultyPoint | None:
    if not points:
        return None

    idx = bisect_right(points, time, key=lambda p: p.time)
    return points[idx - 1] if idx > 0 else points[0]


def effect_point_at(points: list[EffectPoint], time: float) -> EffectPoint | None:
    if not points:
        return None

    idx = bisect_right(points, time, key=lambda p: p.time)
    return points[idx - 1] if idx > 0 else points[0]
