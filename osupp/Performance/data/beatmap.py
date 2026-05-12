"""
MIT License

Copyright (c) 2026-Present O!Lib Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import bisect
import math
from dataclasses import dataclass
from typing import TypeVar, Sequence, Any
from collections import defaultdict
from .hit_objects import HitObject, Pos, Slider, Spinner, HoldNote
from .mode import GameMode
from .mods import PerformanceMods
from .attributes import AdjustedBeatmapAttributes

T = TypeVar("T")


@dataclass(slots=True)
class TimingPoint:
    time: float
    beat_len: float

    DEFAULT_BEAT_LEN: float = 1000.0
    DEFAULT_BPM: float = 60000.0 / 1000.0

    @classmethod
    def create(cls, time: float, beat_len: float) -> "TimingPoint":
        clamped_beat_len = max(6.0, min(60000.0, beat_len))
        return cls(time=time, beat_len=clamped_beat_len)

    def bpm(self) -> float:
        return 60000.0 / self.beat_len

def timing_point_at(points: Sequence[TimingPoint], time: float) -> TimingPoint | None:
    if not points:
        return None

    times = [p.time for p in points]
    idx = bisect.bisect_right(times, time)
    return points[max(0, (idx - 1))]


@dataclass(slots=True)
class DifficultyPoint:
    time: float
    slider_velocity: float
    bpm_multiplier: float
    generate_ticks: bool

    DEFAULT_SLIDER_VELOCITY: float = 1.0
    DEFAULT_BPM_MULTIPLIER: float = 1.0
    DEFAULT_GENERATE_TICKS: bool = True

    @classmethod
    def create(cls, time: float, beat_len: float, speed_multiplier: float) -> "DifficultyPoint":
        sv = max(0.1, min(10.0, speed_multiplier))

        if beat_len < 0.0:
            bpm_mult = max(10.0, min(10000.0, float(-beat_len))) / 100.0
        else:
            bpm_mult = 1.0

        gen_ticks = not math.isnan(beat_len)

        return cls(
            time=time,
            slider_velocity=sv,
            bpm_multiplier=bpm_mult,
            generate_ticks=gen_ticks
        )

    def is_redundant(self, existing: "DifficultyPoint") -> bool:
        return (self.generate_ticks == existing.generate_ticks and
                math.isclose(self.slider_velocity, existing.slider_velocity, rel_tol=1e-9))

def difficulty_point_at(points: Sequence[DifficultyPoint], time: float) -> DifficultyPoint | None:
    if not points:
        return None
    times = [p.time for p in points]
    idx = bisect.bisect_right(times, time)
    return points[idx - 1] if idx > 0 else None


@dataclass(slots=True)
class EffectPoint:
    time: float
    kiai: bool
    scroll_speed: float

    DEFAULT_KIAI: bool = False
    DEFAULT_SCROLL_SPEED: float = 1.0

    @classmethod
    def create(cls, time: float, kiai: bool) -> "EffectPoint":
        return cls(time=time, kiai=kiai, scroll_speed=cls.DEFAULT_SCROLL_SPEED)

    def is_redundant(self, existing: "EffectPoint") -> bool:
        return (self.kiai == existing.kiai and
                math.isclose(self.scroll_speed, existing.scroll_speed, rel_tol=1e-9))

def effect_point_at(points: Sequence[EffectPoint], time: float) -> EffectPoint | None:
    if not points:
        return None
    times = [p.time for p in points]
    idx = bisect.bisect_right(times, time)
    return points[idx - 1] if idx > 0 else None


def calculate_bpm(last_hit_object: HitObject | None, timing_points: Sequence[TimingPoint]) -> float:
    if last_hit_object is not None:
        last_time = last_hit_object.end_time
    elif timing_points:
        last_time = timing_points[-1].time
    else:
        last_time = 0.0

    bpm_durations: dict[float, float] = defaultdict(float)

    def add_duration(beat_len: float, curr_time: float, next_time: float) -> None:
        rounded_beat_len = round(beat_len * 1000.0) / 1000.0
        if curr_time <= last_time:
            bpm_durations[rounded_beat_len] += (next_time - curr_time)

    if len(timing_points) == 1:
        add_duration(timing_points[0].beat_len, 0.0, last_time)
    elif len(timing_points) > 1:
        add_duration(timing_points[0].beat_len, 0.0, timing_points[1].time)

    for i in range(1, len(timing_points) - 1):
        curr = timing_points[i]
        next_tp = timing_points[i + 1]
        add_duration(curr.beat_len, curr.time, next_tp.time)

    if len(timing_points) > 1:
        curr = timing_points[-1]
        add_duration(curr.beat_len, curr.time, last_time)

    if not bpm_durations:
        return 0.0

    most_common_beat_len = max(bpm_durations.items(), key=lambda item: item[1])[0]

    if most_common_beat_len == 0.0:
        return 0.0

    return 60000.0 / most_common_beat_len

def check_suspicion(hit_objects: Sequence[HitObject], mode: GameMode, cs: float) -> None:
    if len(hit_objects) < 2:
        return

    DAY_MS = 24 * 60 * 60 * 1000.0
    if hit_objects[-1].start_time - hit_objects[0].start_time > DAY_MS:
        raise ValueError("Suspicious Map: 24 hours duration.")

    threshold_objects = 30000 if mode == GameMode.TAIKO else 500000
    if len(hit_objects) > threshold_objects:
        raise ValueError(f"Suspicious Map: Excess Objects ({hit_objects}).")

    THRESHOLD_1S = 200
    THRESHOLD_10S = 500

    def is_too_dense(i: int, per_1s: int, per_10s: int) -> bool:
        total_objs = len(hit_objects)
        if total_objs > i + per_1s and hit_objects[i + per_1s].start_time - hit_objects[i].start_time < 1000.0:
            return True
        if total_objs > i + per_10s and hit_objects[i + per_10s].start_time - hit_objects[i].start_time < 10000.0:
            return True
        return False

    per_1s = THRESHOLD_1S
    per_10s = THRESHOLD_10S

    if mode == GameMode.TAIKO:
        per_1s *= 2
        per_10s *= 2
    elif mode == GameMode.MANIA:
        keys_per_hand = max(1, int(cs) // 2)
        per_1s *= keys_per_hand
        per_10s *= keys_per_hand

    repeats_beyond_threshold = 0
    pos_beyond_threshold = 0

    for i, h in enumerate(hit_objects):
        if mode != GameMode.CATCH:
            if is_too_dense(i, per_1s, per_10s):
                raise ValueError("Suspicious Map: Note's Density impossible to detect.")

        if mode in (GameMode.OSU, GameMode.CATCH) and h.is_slider():
            slider = h.kind
            is_pos_broken = abs(h.pos.x) > 10000.0 or abs(h.pos.y) > 10000.0
            is_repeats_broken = slider.repeats > 1000

            if is_repeats_broken:
                if is_pos_broken:
                    raise ValueError("Suspicious Map: Slider corrupted (RedFlag).")
                repeats_beyond_threshold += 1
            elif is_pos_broken:
                pos_beyond_threshold += 1

    if mode in (GameMode.OSU,GameMode.CATCH):
        if pos_beyond_threshold > 128:
            raise ValueError("Suspicious Map: Too many sliders.")
        if repeats_beyond_threshold > 128:
            raise ValueError("Suspicous Map: Too many sliders repeats.")


class PerformanceBeatmap:
    __slots__ = ("version", "is_convert", "stack_leniency", "mode", "base_ar",
                 "base_cs", "base_hp", "base_od", "slider_multiplier", "slider_tick_rate",
                 "timing_points", "difficulty_points", "effect_points", "hit_objects")

    def __init__(self, raw_beatmap: Any, override_mode: GameMode | None = None):
        self.version = int(getattr(raw_beatmap, "version", getattr(raw_beatmap, "format_version", 14)))
        self.is_convert = False
        self.stack_leniency = float(getattr(raw_beatmap, "stack_leniency", 0.7))

        if override_mode is not None:
            self.mode = override_mode
            self.is_convert = True
        else:
            raw_mode = getattr(raw_beatmap, "mode", 0)
            self.mode = GameMode(int(raw_mode)) if isinstance(raw_mode, int) else GameMode.OSU

        diff = getattr(raw_beatmap, "difficulty", None)
        self.base_cs = float(getattr(diff, "cs", getattr(diff, "circle_size", 5.0)))
        self.base_ar = float(getattr(diff, "ar", getattr(diff, "approach_rate", 5.0)))
        self.base_od = float(getattr(diff, "od", getattr(diff, "overall_difficulty", 5.0)))
        self.base_hp = float(getattr(diff, "hp", getattr(diff, "drain_rate", 5.0)))

        self.slider_multiplier = float(getattr(diff, "slider_multiplier", 1.4))
        self.slider_tick_rate = float(getattr(diff, "slider_tick_rate", 1.0))

        self.hit_objects: list[HitObject] = []
        raw_objects = getattr(raw_beatmap, "hit_objects", [])

        for obj in raw_objects:
            pos_x = float(getattr(obj, "x", getattr(getattr(obj, "pos", None), "x", 0.0)))
            pos_y = float(getattr(obj, "y", getattr(getattr(obj, "pos", None), "y", 0.0)))
            start_time = float(getattr(obj, "start_time", getattr(obj, "time", 0.0)))

            kind = None
            obj_type = type(obj).__name__.lower()

            if "slider" in obj_type:
                repeats = int(getattr(obj, "repeat_count", getattr(obj, "repeats", getattr(obj, "span_count", 1) - 1)))
                dist = getattr(obj, "length", getattr(obj, "expected_dist", getattr(obj, "spatial_length", None)))
                dist = float(dist) if dist is not None else None
                control_pts = getattr(obj, "control_points", getattr(obj, "path", []))

                kind = Slider(expected_dist=dist, repeats=repeats, control_points=list(control_pts))

            elif "spinner" in obj_type:
                end_time = float(getattr(obj, "end_time", getattr(obj, "duration", start_time)))
                kind = Spinner(duration=max(0.0, end_time - start_time))

            elif "hold" in obj_type or ("mania" in obj_type and "long" in obj_type):
                end_time = float(getattr(obj, "end_time", start_time))
                kind = HoldNote(duration=max(0.0, end_time - start_time))

            self.hit_objects.append(HitObject(pos=Pos(pos_x, pos_y), start_time=start_time, kind=kind))

        self.hit_objects.sort(key=lambda h: h.start_time)

        check_suspicion(self.hit_objects, self.mode, self.base_cs)

        self.timing_points: list[TimingPoint] = []
        self.difficulty_points: list[DifficultyPoint] = []
        self.effect_points: list[EffectPoint] = []

        raw_timing = getattr(raw_beatmap, "timing_points", getattr(raw_beatmap, "control_points", []))

        for cp in raw_timing:
            time = float(getattr(cp, "time", 0.0))

            if hasattr(cp, "beat_length") and getattr(cp, "beat_length") > 0:
                tp = TimingPoint.create(time, float(cp.beat_length))
                if not self.timing_points or self.timing_points[-1].time != time:
                    self.timing_points.append(tp)

            if hasattr(cp, "slider_velocity") or (hasattr(cp, "beat_length") and getattr(cp, "beat_length") < 0):
                sv = float(getattr(cp, "slider_velocity", 1.0))
                if hasattr(cp, "beat_length"):
                    bl = getattr(cp, "beat_length")
                    if bl < 0: sv = 100.0 / -bl

                gen_ticks = bool(getattr(cp, "generate_ticks", True))
                dp = DifficultyPoint.create(time, -100.0/sv if sv != 0 else 0, sv)

                if not self.difficulty_points or not dp.is_redundant(self.difficulty_points[-1]):
                    self.difficulty_points.append(dp)

    def attributes(self, mods: PerformanceMods) -> AdjustedBeatmapAttributes:
        return AdjustedBeatmapAttributes.create(
            base_cs=self.base_cs, base_ar=self.base_ar, base_od=self.base_od, base_hp=self.base_hp,
            mode=self.mode, mods=mods
        )

    def bpm(self) -> float:
        last_obj = self.hit_objects[-1] if self.hit_objects else None
        return calculate_bpm(last_obj, self.timing_points)