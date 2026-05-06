from dataclasses import dataclass, field
from collections import Counter
from enum import Enum

from osupp.Beatmap.section.enums import GameMode
from osupp.Beatmap.section.events import BreakPeriod
from osupp.Beatmap.section.timing_points import ControlPoints

from ..model import GameMods, HitObject

class TooSuspiciousError(Exception):
    def __init__(self, reason: str):
        super().__init__(f"Beatmap is too suspicious: {reason}")
        self.reason = reason


@dataclass(slots=True)
class Beatmap:
    version: int = 14
    is_convert: bool = False
    stack_leniency: float = 0.7
    mode: GameMode = GameMode.Osu

    ar: float = 5.0
    cs: float = 5.0
    hp: float = 5.0
    od: float = 5.0
    slider_multiplier: float = 1.4
    slider_tick_rate: float = 1.0

    breaks: list[BreakPeriod] = field(default_factory=list)
    timing_points: list = field(default_factory=list)
    difficulty_points: list = field(default_factory=list)
    effect_points: list = field(default_factory=list)
    hit_objects: list[HitObject] = field(default_factory=list)

    def bpm(self) -> float:
        if not self.timing_points:
            return 0.0

        last_time = self.hit_objects[-1].end_time if self.hit_objects else self.timing_points[-1].time

        durations = Counter()

        for i in range(len(self.timing_points)):
            curr = self.timing_points[i]
            next_time = self.timing_points[i + 1].time if i + 1 < len(self.timing_points) else last_time

            duration = max(0.0, next_time - curr.time)
            durations[round(curr.beat_len, 6)] += duration

        if not durations:
            return 0.0

        most_comum_beat_len = durations.most_common(1)[0][0]

        return 60000.0 / most_comum_beat_len if most_comum_beat_len != 0 else 0.0

    def check_suspicion(self) -> None:
        obj_count = len(self.hit_objects
                        )
        if obj_count > 25000:
            raise TooSuspiciousError("Object count exceeds limit (25,000)")

        if obj_count < 2:
            return

        duration = self.hit_objects[-1].start_time - self.hit_objects[0].start_time
        if duration > 86400000:
            raise TooSuspiciousError("Map duration exceeds 24 hours")

        for i in range(obj_count - 200):
            if self.hit_objects[i+200].start_time - self.hit_objects[i].start_time < 1000:
                raise TooSuspiciousError("Note density is too high (>200 notes/sec)")

    def get_max_combo(self) -> int:
        return len(self.hit_objects)