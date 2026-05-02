import math
from typing import List, Optional


def _clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(value, max_val))


class DifficultyPoint:
    __slots__ = ("time", "slider_velocity", "bpm_multiplier", "generate_ticks")

    DEFAULT_SLIDER_VELOCITY = 1.0
    DEFAULT_BPM_MULTIPLIER = 1.0
    DEFAULT_GENERATE_TICKS = True

    def __init__(self, time: float, slider_velocity: float, bpm_multiplier: float, generate_ticks: bool):
        self.time = time
        self.slider_velocity = slider_velocity
        self.bpm_multiplier = bpm_multiplier
        self.generate_ticks = generate_ticks

    @classmethod
    def new(cls, time: float, beat_len: float, speed_multiplier: float) -> "DifficultyPoint":
        slider_velocity = _clamp(speed_multiplier, 0.1, 10.0)

        if beat_len < 0.0:
            bpm_multiplier = _clamp(float(-beat_len), 10.0, 10000.0) / 100.0
        else:
            bpm_multiplier = 1.0

        generate_ticks = not math.isnan(beat_len)

        return cls(time, slider_velocity, bpm_multiplier, generate_ticks)

    @classmethod
    def default(cls) -> "DifficultyPoint":
        return cls(
            0.0,
            cls.DEFAULT_SLIDER_VELOCITY,
            cls.DEFAULT_BPM_MULTIPLIER,
            cls.DEFAULT_GENERATE_TICKS
        )

    def is_redundant(self, existing: "DifficultyPoint") -> bool:
        return (self.generate_ticks == existing.generate_ticks and
                math.isclose(self.slider_velocity, existing.slider_velocity, rel_tol=1e-9, abs_tol=0.0))


def difficulty_point_at(points: List[DifficultyPoint], time: float) -> Optional[DifficultyPoint]:
    if not points:
        return None

    lo, hi = 0, len(points)
    while lo < hi:
        mid = (lo + hi) // 2
        if points[mid].time <= time:
            lo = mid + 1
        else:
            hi = mid

    idx = max(0, lo - 1)
    if idx <  len(points) and points[idx].time <= time:
        return points[idx]
    return None


class EffectPoint:
    __slots__ = ("time", "kiai", "scroll_speed")

    DEFAULT_KIAI = False
    DEFAULT_SCROLL_SPEED = 1.0

    def __init__(self, time: float, kiai: bool, scroll_speed: float = 1.0):
        self.time = time
        self.kiai = kiai
        self.scroll_speed = scroll_speed

    @classmethod
    def new(cls, time: float, kiai: bool) -> "EffectPoint":
        return cls(time, kiai, cls.DEFAULT_SCROLL_SPEED)

    @classmethod
    def default(cls) -> "EffectPoint":
        return cls(0.0, cls.DEFAULT_KIAI, cls.DEFAULT_SCROLL_SPEED)

    def is_redundant(self, existing: "EffectPoint") -> bool:
        return (self.kiai == existing.kiai and
                math.isclose(self.scroll_speed, existing.scroll_speed, rel_tol=1e-9, abs_tol=0.0))


def effect_point_at(points: List[EffectPoint], time: float) -> Optional[EffectPoint]:
    if not points:
        return None

    lo, hi = 0, len(points)
    while lo < hi:
        mid = (lo + hi) // 2
        if points[mid].time <= time:
            lo = mid + 1
        else:
            hi = mid

    idx = max(0, lo - 1)
    if idx < len(points) and points[idx].time <= time:
        return points[idx]
    return None


class TimingPoint:
    DEFAULT_BEAT_LEN = 60000.0 / 60.0
    DEFAULT_BPM = 60000.0 / DEFAULT_BEAT_LEN

    def __init__(self, time: float, beat_len: float):
        self.time = time
        self.beat_len = beat_len

    @classmethod
    def new(cls, time: float, beat_len: float) -> "TimingPoint":
        clamped_beat_len = _clamp(beat_len, 6.0, 60000.0)
        return cls(time, clamped_beat_len)

    @classmethod
    def default(cls) -> "TimingPoint":
        return cls(0.0, cls.DEFAULT_BEAT_LEN)

    def bpm(self) -> float:
        return 60000.0 / self.beat_len


def timing_point_at(points: List[TimingPoint], time: float) -> Optional[TimingPoint]:
    if not points:
        return None

    lo, hi = 0, len(points)
    while lo < hi:
        mid = (lo + hi) // 2
        if points[mid].time <= time:
            lo = mid + 1
        else:
            hi = mid

    idx = max(0, lo - 1)
    return points[idx] if idx < len(points) else None