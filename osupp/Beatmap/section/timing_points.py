from __future__ import annotations

import bisect
import math
from dataclasses import dataclass, field

from utils import (
    MAX_PARSE_VALUE,
    ParseNumberError,
    parse_float,
    parse_int,
    trim_comment,
)

from section.enums import GameMode, SampleBank


class ParseTimingPointsError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


EPSILON = 1e-7


class EffectFlags:
    NONE = 0
    KIAI = 1 << 0
    OMIT_FIRST_BAR_LINE = 1 << 3


@dataclass(slots=True, eq=True)
class TimingPoint:
    time: float = 0.0
    beat_len: float = 60000.0 / 60.0
    omit_first_bar_line: bool = False
    time_signature: int = 4


_DEFAULT_DIFFICULTY = None


@dataclass(slots=True, eq=True)
class DifficultyPoint:
    time: float = 0.0
    slider_velocity: float = 1.0
    generate_ticks: bool = True

    def is_redundant(self, existing: DifficultyPoint) -> bool:
        return (
            self.generate_ticks == existing.generate_ticks
            and abs(self.slider_velocity - existing.slider_velocity) < EPSILON
        )


_DEFAULT_DIFFICULTY = DifficultyPoint()


@dataclass(slots=True, eq=True)
class SamplePoint:
    time: float = 0.0
    sample_bank: SampleBank = SampleBank.Normal
    sample_volume: int = 100
    custom_sample_bank: int = 0

    def is_redundant(self, existing: SamplePoint) -> bool:
        return (
            self.sample_bank == existing.sample_bank
            and self.sample_volume == existing.sample_volume
            and self.custom_sample_bank == existing.custom_sample_bank
        )


@dataclass(slots=True, eq=True)
class EffectPoint:
    time: float = 0.0
    kiai: bool = False
    scroll_speed: float = 1.0

    def is_redundant(self, existing: EffectPoint) -> bool:
        return (
            self.kiai == existing.kiai
            and abs(self.scroll_speed - existing.scroll_speed) < EPSILON
        )


@dataclass(slots=True, eq=True)
class ControlPoints:
    timing_points: list[TimingPoint] = field(default_factory=list)
    difficulty_points: list[DifficultyPoint] = field(default_factory=list)
    effect_points: list[EffectPoint] = field(default_factory=list)
    sample_points: list[SamplePoint] = field(default_factory=list)

    def difficulty_point_at(self, time: float) -> DifficultyPoint:
        idx = bisect.bisect_right(self.difficulty_points, time, key=lambda x: x.time)
        return (
            self.difficulty_points[max(0, idx - 1)]
            if self.difficulty_points
            else DifficultyPoint()
        )

    def effect_point_at(self, time: float) -> EffectPoint:
        idx = bisect.bisect_right(self.effect_points, time, key=lambda x: x.time)
        return (
            self.effect_points[max(0, idx - 1)] if self.effect_points else EffectPoint()
        )

    def sample_point_at(self, time: float) -> SamplePoint:
        idx = bisect.bisect_right(self.sample_points, time, key=lambda x: x.time)
        return (
            self.sample_points[max(0, idx - 1)] if self.sample_points else SamplePoint()
        )

    def timing_point_at(self, time: float) -> TimingPoint:
        idx = bisect.bisect_right(self.timing_points, time, key=lambda x: x.time)
        return (
            self.timing_points[max(0, idx - 1)] if self.timing_points else TimingPoint()
        )

    def add_timing(self, point: TimingPoint) -> None:
        idx = bisect.bisect_left(self.timing_points, point.time, key=lambda x: x.time)
        if (
            idx < len(self.timing_points)
            and abs(self.timing_points[idx].time - point.time) < EPSILON
        ):
            self.timing_points[idx] = point
        else:
            self.timing_points.insert(idx, point)

    def add_difficulty(self, point: DifficultyPoint) -> None:
        existing_at = self._exact_at(self.difficulty_points, point.time)
        if existing_at is not None:
            if point.is_redundant(existing_at):
                return

            idx = bisect.bisect_left(
                self.difficulty_points,
                point.time,
                key=lambda x: x.time,
            )
            self.difficulty_points[idx] = point
            return

        if self.difficulty_points:
            active = self.difficulty_point_at(point.time)
            if point.is_redundant(active):
                return
        elif point.is_redundant(_DEFAULT_DIFFICULTY):
            return

        idx = bisect.bisect_left(
            self.difficulty_points,
            point.time,
            key=lambda x: x.time,
        )
        self.difficulty_points.insert(idx, point)

    def add_effect(self, point: EffectPoint) -> None:
        existing_at = self._exact_at(self.effect_points, point.time)
        if existing_at is not None:
            if point.is_redundant(existing_at):
                return

            idx = bisect.bisect_left(
                self.effect_points,
                point.time,
                key=lambda x: x.time,
            )
            self.effect_points[idx] = point
            return

        if self.effect_points:
            active = self.effect_point_at(point.time)
            if point.is_redundant(active):
                return
        elif point.is_redundant(EffectPoint()):
            return

        idx = bisect.bisect_left(
            self.effect_points,
            point.time,
            key=lambda x: x.time,
        )
        self.effect_points.insert(idx, point)

    def add_sample(self, point: SamplePoint) -> None:
        existing_at = self._exact_at(self.sample_points, point.time)
        if existing_at is not None:
            if point.is_redundant(existing_at):
                return

            idx = bisect.bisect_left(
                self.sample_points,
                point.time,
                key=lambda x: x.time,
            )
            self.sample_points[idx] = point
            return

        if self.sample_points:
            active = self.sample_point_at(point.time)
            if point.is_redundant(active):
                return

        idx = bisect.bisect_left(
            self.sample_points,
            point.time,
            key=lambda x: x.time,
        )
        self.sample_points.insert(idx, point)

    @staticmethod
    def _exact_at(points: list, time: float):
        if not points:
            return None
        idx = bisect.bisect_left(points, time, key=lambda x: x.time)
        if idx < len(points) and abs(points[idx].time - time) < EPSILON:
            return points[idx]
        return None


class TimingPointsState:
    __slots__ = (
        "general_mode",
        "general_default_sample_bank",
        "general_default_sample_volume",
        "pending_time",
        "pending_timing",
        "pending_difficulty",
        "pending_effect",
        "pending_sample",
        "control_points",
    )

    def __init__(self, mode: GameMode, default_bank: SampleBank, default_volume: int):
        self.general_mode = mode
        self.general_default_sample_bank = default_bank
        self.general_default_sample_volume = default_volume

        self.pending_time: float = 0.0
        self.pending_timing: TimingPoint | None = None
        self.pending_difficulty: DifficultyPoint | None = None
        self.pending_effect: EffectPoint | None = None
        self.pending_sample: SamplePoint | None = None
        self.control_points = ControlPoints()

    def flush_pending(self) -> None:
        if self.pending_timing is not None:
            self.control_points.add_timing(self.pending_timing)
        if self.pending_difficulty is not None:
            self.control_points.add_difficulty(self.pending_difficulty)
        if self.pending_effect is not None:
            self.control_points.add_effect(self.pending_effect)
        if self.pending_sample is not None:
            self.control_points.add_sample(self.pending_sample)

        self.pending_timing = None
        self.pending_difficulty = None
        self.pending_effect = None
        self.pending_sample = None

    def push_point(self, time: float, point, timing_change: bool) -> None:
        if abs(time - self.pending_time) >= EPSILON:
            self.flush_pending()

        if isinstance(point, TimingPoint):
            if timing_change or self.pending_timing is None:
                self.pending_timing = point
        elif isinstance(point, DifficultyPoint):
            if not timing_change or self.pending_difficulty is None:
                self.pending_difficulty = point
        elif isinstance(point, EffectPoint):
            if not timing_change or self.pending_effect is None:
                self.pending_effect = point
        elif isinstance(point, SamplePoint):
            if not timing_change or self.pending_sample is None:
                self.pending_sample = point

        self.pending_time = time

    def parse_timing_points(self, line: str) -> None:
        clean_line = trim_comment(line)
        parts = [p.strip() for p in clean_line.split(",")]
        if len(parts) < 2:
            raise ParseTimingPointsError("invalid line")

        try:
            time = parse_float(parts[0])
            beat_len_raw = parts[1]
            try:
                beat_len = float(beat_len_raw)
            except ValueError:
                raise ParseNumberError("invalid float")

            if not math.isnan(beat_len):
                if beat_len < -MAX_PARSE_VALUE:
                    raise ParseNumberError(ParseNumberError.Underflow)
                if beat_len > MAX_PARSE_VALUE:
                    raise ParseNumberError(ParseNumberError.Overflow)

            speed_multiplier = 100.0 / -beat_len if beat_len < 0.0 else 1.0

            time_signature = 4
            if len(parts) > 2 and parts[2] and not parts[2].startswith("0"):
                time_signature = parse_int(parts[2])

            sample_set = self.general_default_sample_bank
            if len(parts) > 3:
                try:
                    val = parse_int(parts[3])
                    if val in (1, 2, 3):
                        sample_set = SampleBank(val)
                except ParseNumberError:
                    pass

            try:
                custom_sample_bank = parse_int(parts[4]) if len(parts) > 4 else 0
            except ParseNumberError:
                custom_sample_bank = 0

            try:
                sample_volume = (
                    parse_int(parts[5])
                    if len(parts) > 5
                    else self.general_default_sample_volume
                )
            except ParseNumberError:
                sample_volume = self.general_default_sample_volume

            timing_change = parts[6].startswith("1") if len(parts) > 6 else True

            kiai_mode = False
            omit_first_bar = False
            if len(parts) > 7:
                try:
                    flags = parse_int(parts[7])
                    kiai_mode = (flags & EffectFlags.KIAI) != 0
                    omit_first_bar = (flags & EffectFlags.OMIT_FIRST_BAR_LINE) != 0
                except ParseNumberError:
                    pass

            if sample_set == SampleBank.None_:
                sample_set = SampleBank.Normal

            if timing_change:
                if math.isnan(beat_len):
                    return
                timing = TimingPoint(
                    time,
                    max(6.0, min(60000.0, beat_len)),
                    omit_first_bar,
                    time_signature,
                )
                self.push_point(time, timing, timing_change)

            generate_ticks = not math.isnan(beat_len)
            difficulty = DifficultyPoint(
                time,
                max(0.1, min(10.0, speed_multiplier)) if generate_ticks else 1.0,
                generate_ticks,
            )
            self.push_point(time, difficulty, timing_change)

            sample = SamplePoint(
                time, sample_set, max(0, min(100, sample_volume)), custom_sample_bank
            )
            self.push_point(time, sample, timing_change)

            effect = EffectPoint(
                time,
                kiai_mode,
                max(0.01, min(10.0, speed_multiplier))
                if self.general_mode in (GameMode.Taiko, GameMode.Mania)
                else 1.0,
            )
            self.push_point(time, effect, timing_change)

        except ParseNumberError as e:
            raise ParseTimingPointsError(f"failed to parse number: {e}")
