import math
from dataclasses import dataclass
from typing import List, Optional

from ..utils.util import almost_eq, clamp


@dataclass
class TimingPoint:
    time: float = 0.0
    beat_len: float = 60000.0 / 60.0

    DEFAULT_BEAT_LEN = 60000.0 / 60.0
    DEFAULT_BPM = 60.0

    @classmethod
    def new(cls, time: float, beat_len: float) -> "TimingPoint":
        return cls(time=time, beat_len=clamp(beat_len, 6.0, 60000.0))

    def bpm(self) -> float:
        return 60000.0 / self.beat_len


def timing_point_at(points: list[TimingPoint], time: float) -> TimingPoint | None:
    if not points:
        return None

    import bisect
    times = [p.time for p in points]
    idx = bisect.bisect_right(times, time)

    if idx == 0:
        return points[0]
    return points[idx - 1]


@dataclass
class DifficultyPoint:
    time: float = 0.0
    slider_velocity: float = 1.0
    bpm_multiplier: float = 1.0
    generate_ticks: bool = True

    DEFAULT_SLIDER_VELOCITY = 1.0
    DEFAULT_BPM_MULTIPLIER = 1.0
    DEFAULT_GENERATE_TICKS = True

    @classmethod
    def new(cls, time: float, beat_len: float, speed_multiplier: float) -> "DifficultyPoint":
        if beat_len < 0.0:
            bpm_mult = clamp(float(-beat_len), 10.0, 10000.0) / 100.0
        else:
            bpm_mult = 1.0

        return cls(
            time=time,
            slider_velocity=clamp(speed_multiplier, 0.1, 10.0),
            bpm_multiplier=bpm_mult,
            generate_ticks=not math.isnan(beat_len)
        )

    def is_redundant(self, existing: "DifficultyPoint") -> bool:
        return (self.generate_ticks == existing.generate_ticks and
                 almost_eq(self.slider_velocity, existing.slider_velocity))


def difficulty_point_at(points: list[DifficultyPoint], time: float) -> DifficultyPoint | None:
    if not points:
        return None

    import bisect
    times = [p.time for p in points]
    idx = bisect.bisect_right(times, time)

    if idx == 0:
        return points[0]
    return points[idx - 1]


@dataclass
class EffectPoint:
    time: float = 0.0
    kiai: bool = False
    scroll_speed: float = 1.0

    DEFAULT_KIAI = False
    DEFAULT_SCROLL_SPEED = 1.0

    @classmethod
    def new(cls, time: float, kiai: bool) -> "EffectPoint":
        return cls(
            time=time,
            kiai=kiai,
            scroll_speed=cls.DEFAULT_SCROLL_SPEED
        )

    def is_redundant(self, existing: "EffectPoint") -> bool:
        return self.kiai == existing.kiai and almost_eq(self.scroll_speed, existing.scroll_speed)


def effect_point_at(points: list[EffectPoint], time: float) -> EffectPoint | None:
    if not points:
        return None

    import bisect
    times = [p.time for p in points]
    idx = bisect.bisect_right(times, time)

    if idx == 0:
        return points[0]
    return points[idx - 1]
