from dataclasses import dataclass
import bisect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from section.timing_points import ControlPoints


@dataclass
class EffectPoint:
    time: float
    kiai: bool
    scroll_speed: float

    DEFAULT_KIAI: bool = False
    DEFAULT_SCROLL_SPEED: float = 1.0

    @classmethod
    def default(cls) -> "EffectPoint":
        return cls(
            time=0.0, kiai=cls.DEFAULT_KIAI, scroll_speed=cls.DEFAULT_SCROLL_SPEED
        )

    @classmethod
    def new(cls, time: float, kiai: bool) -> "EffectPoint":
        return cls(time=time, kiai=kiai, scroll_speed=cls.DEFAULT_SCROLL_SPEED)

    def check_already_existing(self, control_points: "ControlPoints") -> bool:
        existing = control_points.effect_points_at(self.time)
        if existing is not None:
            return self.is_redundant(existing)

        return self.is_redundant(EffectPoint.default())

    def add_to(self, control_points: "ControlPoints") -> None:
        points = control_points.effect_points

        idx = bisect.bisect_left(points, self.time, key=lambda p: p.time)

        if idx < len(points) and points[idx].time == self.time:
            points[idx] = self
        else:
            points.insert(idx, self)

    def is_redundant(self, existing: "EffectPoint") -> bool:
        return (
            self.kiai == existing.kiai
            and abs(self.scroll_speed - existing.scroll_speed) < 1e-9
        )

    def __lt__(self, other: "EffectPoint") -> bool:
        if not isinstance(other, EffectPoint):
            return NotImplemented
        return self.time < other.time

    def __le__(self, other: "EffectPoint") -> bool:
        if not isinstance(other, EffectPoint):
            return NotImplemented
        return self.time <= other.time

    def __gt__(self, other: "EffectPoint") -> bool:
        if not isinstance(other, EffectPoint):
            return NotImplemented
        return self.time > other.time

    def __ge__(self, other: "EffectPoint") -> bool:
        if not isinstance(other, EffectPoint):
            return NotImplemented
        return self.time >= other.time
