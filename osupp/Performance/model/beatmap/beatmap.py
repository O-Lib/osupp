from enum import Enum
from typing import Dict, List

from osupp.Beatmap.section.enums import GameMode
from osupp.Beatmap.section.hit_objects.hit_objects import HitObject

from ...utils.sort import osu_legacy_sort
from ..control_points import TimingPoint


def calculate_bpm(hit_objects: list[HitObject], timing_points: list[TimingPoint]) -> float:
    if not timing_points:
        return 0.0

    last_time = 0.0
    if hit_objects:
        last_time = hit_objects[-1].start_time
    elif timing_points:
        last_time = timing_points[-1].time

    bpm_durations: dict[float, float] = {}

    def add_duration(beat_len: float, curr_time: float, next_time: float):
        rounded_beat_len = round(beat_len * 1000.0) / 1000.0
        if curr_time <= last_time:
            bpm_durations[rounded_beat_len] = bpm_durations.get(rounded_beat_len, 0.0) + (next_time - curr_time)

    if len(timing_points) == 1:
        add_duration(timing_points[0].beat_len, 0.0, last_time)
    elif len(timing_points) > 1:
        add_duration(timing_points[0].beat_len, 0.0, timing_points[1].time)

    for i in range(1, len(timing_points) - 1):
        curr = timing_points[i]
        next_tp = timing_points[i + 1]
        add_duration(curr.beat_len, curr.time, next_tp.time)

    if len(timing_points) >= 2:
        curr = timing_points[-1]
        add_duration(curr.beat_len, curr.time, last_time)

    most_common_beat_len = 0.0
    max_duration = -1.0
    for b_len, duration in bpm_durations.items():
        if duration > max_duration:
            max_duration = duration
            most_common_beat_len = b_len

    if most_common_beat_len == 0.0:
        return 0.0

    return 60000.0 / most_common_beat_len


class TooSuspiciousReason(Enum):
    DENSITY = "Density"
    LENGTH = "Length"
    OBJECT_COUNT = "ObjectCount"
    RED_FLAG = "RedFlag"
    SLIDER_POSITIONS = "SliderPositions"
    SLIDER_REPEATS = "SliderRepeats"

class TooSuspiciousError(Exception):
    def __init__(self, reason: TooSuspiciousReason):
        super().__init__(f"The map seems too suspicious to be accurate (reason: {reason.value})")
        self.reason = reason


def check_suspicion(hit_objects: list[HitObject], mode: GameMode, cs: float) -> None:
    if len(hit_objects) < 2:
        return

    DAY_MS = 60 * 60 * 24 * 1000
    if (hit_objects[-1].start_time - hit_objects[0].start_time) > DAY_MS:
        raise TooSuspiciousError(TooSuspiciousReason.LENGTH)

    THRESHOLD_OBJECTS = 30000 if mode == GameMode.Taiko else 500000
    if len(hit_objects) > THRESHOLD_OBJECTS:
        raise TooSuspiciousError(TooSuspiciousReason.OBJECT_COUNT)

    THRESHOLD_1S = 200
    THRESHOLD_10S = 500

    def too_dense(i: int, per_1s: int, per_10s: int) -> bool:
        if i + per_1s < len(hit_objects) and (hit_objects[i + per_1s].start_time - hit_objects[i].start_time) < 1000.0:
            return True
        if i + per_10s < len(hit_objects) and (hit_objects[i + per_10s].start_time - hit_objects[i].start_time) < 10000.0:
            return True
        return False

    repeats_beyond_threshold = 0
    pos_beyond_threshold = 0
    MAX_COORD = 10000.0
    MAX_REPEATS = 1000

    if mode == GameMode.Osu:
        for i, h in enumerate(hit_objects):
            if too_dense(i, THRESHOLD_1S, THRESHOLD_10S):
                raise TooSuspiciousError(TooSuspiciousReason.DENSITY)

            if hasattr(h.kind, "repeat_count"):
                if h.kind.repeat_count > MAX_REPEATS:
                    if abs(h.kind.pos.x) > MAX_COORD or abs(h.kind.pos.y) > MAX_COORD:
                        raise TooSuspiciousError(TooSuspiciousReason.RED_FLAG)
                    repeats_beyond_threshold += 1
                elif abs(h.kind.pos.x) > MAX_COORD or abs(h.kind.pos.y) > MAX_COORD:
                    pos_beyond_threshold += 1

    elif mode == GameMode.Taiko:
        for i in range(len(hit_objects)):
            if too_dense(i, THRESHOLD_1S * 2, THRESHOLD_10S * 2):
                raise TooSuspiciousError(TooSuspiciousReason.DENSITY)

    elif mode == GameMode.Catch:
        for h in hit_objects:
            if hasattr(h.kind, "repeats_count"):
                if h.kind.repeat_count > MAX_REPEATS:
                    if abs(h.kind.pos.x) > MAX_COORD or abs(h.kind.pos.y) > MAX_COORD:
                        raise TooSuspiciousError(TooSuspiciousReason.RED_FLAG)
                    repeats_beyond_threshold += 1
                elif abs(h.kind.pos.x) > MAX_COORD or abs(h.kind.pos.y) > MAX_COORD:
                    pos_beyond_threshold += 1

    elif mode == GameMode.Mania:
        keys_per_hand = max(1, int(cs) // 2)
        for i in range(len(hit_objects)):
            if too_dense(i, THRESHOLD_1S * keys_per_hand, THRESHOLD_10S * keys_per_hand):
                raise TooSuspiciousError(TooSuspiciousReason.DENSITY)

    CUTOFF = 128
    if pos_beyond_threshold > CUTOFF:
        raise TooSuspiciousError(TooSuspiciousReason.SLIDER_POSITIONS)
    if repeats_beyond_threshold > CUTOFF:
        raise TooSuspiciousError(TooSuspiciousReason.SLIDER_REPEATS)


def mania_hit_objects_legacy_sort(hit_objects: list[HitObject]) -> None:
    def compare_mania_objects(a: HitObject, b: HitObject) -> int:
        time_a = int(round(a.start_time))
        time_b = int(round(b.start_time))
        if time_a < time_b:
            return -1
        elif time_a > time_b:
            return 1
        return 0

    osu_legacy_sort(hit_objects, compare_mania_objects)
