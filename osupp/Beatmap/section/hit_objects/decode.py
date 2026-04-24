from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any

from section.difficulty import Difficulty, DifficultyState
from section.events import BreakPeriod, Events, EventsState
from section.general import CountdownType, GameMode
from section.timing_points import (
    ControlPoints,
    DifficultyPoint,
    TimingPoint,
    TimingPoints,
    TimingPointsState,
)
from utils import Pos

from .circle import HitObjectCircle
from .hit_samples import (
    HitSoundType,
    SampleBank,
    SampleBankInfo,
)
from .hold import HitObjectHold
from .mod import BASE_SCORING_DIST, HitObject, HitObjectType, HitObjectKind
from .slider import (
    CurveBuffers,
    HitObjectSlider,
    PathControlPoint,
    PathType,
    SliderPath,
)
from .spinner import HitObjectSpinner

MAX_COORDINATE_VALUE = 131072


@dataclass
class HitObjects:
    # General
    audio_file: str = ""
    audio_lead_in: float = 0.0
    preview_time: int = 0
    default_sample_bank: SampleBank = SampleBank.NORMAL
    default_sample_volume: int = 100
    stack_leniency: float = 0.7
    mode: GameMode | None = None
    letterbox_in_breaks: bool = False
    special_style: bool = False
    widescreen_storyboard: bool = False
    epilepsy_warning: bool = False
    samples_match_playback_rate: bool = False
    countdown: CountdownType | None = None
    countdown_offset: int = 0

    # Difficulty
    hp_drain_rate: float = 5.0
    circle_size: float = 5.0
    overall_difficulty: float = 5.0
    approach_rate: float = 5.0
    slider_multiplier: float = 1.4
    slider_tick_rate: float = 1.0

    # Events
    background_file: str = ""
    breaks: list[BreakPeriod] = field(default_factory=list)

    # TimingPoints
    control_points: ControlPoints = field(default_factory=lambda: ControlPoints())

    # HitObjects
    hit_objects: list[HitObject] = field(default_factory=list)

    @classmethod
    def default(cls) -> HitObjects:
        return cls()

    @classmethod
    def parse_general(cls, state: HitObjectsState, line: str) -> None:
        try:
            TimingPoints.parse_general(state.timing_points, line)
        except Exception as e:
            raise ParseHitObjectsError.timing_points(e)

    @classmethod
    def parse_editor(cls, state: HitObjectsState, line: str) -> None:
        pass

    @classmethod
    def parse_metadata(cls, state: HitObjectsState, line: str) -> None:
        pass

    @classmethod
    def parse_difficulty(cls, state: HitObjectsState, line: str) -> None:
        try:
            Difficulty.parse_difficulty(state.difficulty, line)
        except Exception as e:
            raise ParseHitObjectsError.difficulty(e)

    @classmethod
    def parse_events(cls, state: HitObjectsState, line: str) -> None:
        try:
            Events.parse_events(state.events, line)
        except Exception as e:
            ParseHitObjectsError.events(e)

    @classmethod
    def parse_timing_points(cls, state: HitObjectsState, line: str) -> None:
        try:
            TimingPoints.parse_timing_points(state.timing_points, line)
        except Exception as e:
            raise ParseHitObjectsError.timing_points(e)

    @classmethod
    def parse_colors(cls, state: HitObjectsState, line: str) -> None:
        pass

    @classmethod
    def parse_hit_objects(cls, state: HitObjectsState, line: str) -> None:
        line = line.split("//")[0].strip()
        if not line:
            return

        parts = line.split(",")
        if len(parts) < 5:
            raise ParseHitObjectsError.invalid_line()

        try:
            x = float(parts[0])
            y = float(parts[1])
            pos = Pos(
                float(int(max(-MAX_COORDINATE_VALUE, min(x, MAX_COORDINATE_VALUE)))),
                float(int(max(-MAX_COORDINATE_VALUE, min(y, MAX_COORDINATE_VALUE)))),
            )

            start_time_raw = float(parts[2])
            start_time = start_time_raw

            raw_type = int(parts[3])
            hit_object_type = HitObjectType(raw_type)
        except ValueError as e:
            raise ParseHitObjectsError.number(e)

        new_combo = hit_object_type.has_flag(HitObjectType.NEW_COMBO)
        combo_offset = (hit_object_type.value & HitObjectType.COMBO_OFFSET) >> 4
        hit_object_type &= ~(HitObjectType.NEW_COMBO | HitObjectType.COMBO_OFFSET)

        try:
            sound_type = HitSoundType(int(parts[4]))
        except ValueError as e:
            raise ParseHitObjectsError.hit_object_type(e)

        bank_info = SampleBankInfo()
        inner_kind = None

        if hit_object_type.has_flag(HitObjectType.CIRCLE):
            if len(parts) > 5:
                bank_info.read_custom_sample_banks(iter(parts[5].split(":")), False)

            inner_kind = HitObjectCircle(
                pos=pos,
                new_combo=state.first_object
                or state.last_object_was_spinner()
                or new_combo,
                combo_offset=combo_offset if new_combo else 0,
            )

        elif hit_object_type.has_flag(HitObjectType.SLIDER):
            if len(parts) < 7:
                raise ParseHitObjectsError.invalid_line()

            points_str = parts[5]
            try:
                repeat_count = int(parts[6])
                if repeat_count > 9000:
                    raise ParseHitObjectsError.invalid_repeat_count(repeat_count)
                repeat_count = max(0, repeat_count - 1)
            except ValueError as e:
                raise ParseHitObjectsError.number(e)

            length = None
            if len(parts) > 7:
                new_len = float(parts[7])
                if abs(new_len) >= 1e-7:
                    length = max(0.0, new_len)

            next_8 = parts[8] if len(parts) > 8 else None
            next_9 = parts[9] if len(parts) > 9 else None

            if len(parts) > 10:
                bank_info.read_custom_sample_banks(iter(parts[10].split(":")), True)

            nodes = repeat_count + 2
            node_bank_infos = [copy.deepcopy(bank_info) for _ in range(nodes)]

            if next_9 and next_9.strip():
                for i, (b_info, s_set) in enumerate(
                    zip(node_bank_infos, next_9.split("|"))
                ):
                    b_info.read_custom_sample_banks(iter(s_set.split(":")), False)

            node_sounds_types: list[HitSoundType] = [
                HitSoundType(sound_type.value) for _ in range(nodes)
            ]
            if next_8 and next_8.strip():
                for i, s_val in enumerate(next_8.split("|")):
                    if i < nodes:
                        try:
                            node_sounds_types[i] = HitSoundType(int(s_val))
                        except ValueError:
                            node_sounds_types[i] = HitSoundType(HitSoundType.NONE)

            node_samples = [
                bi.convert_sound_type(st)
                for bi, st in zip(node_bank_infos, node_sounds_types)
            ]

            state.convert_path_str(points_str, pos)
            control_points = list(state.curve_points)
            state.curve_points.clear()

            inner_kind = HitObjectSlider(
                pos=pos,
                start_time=start_time,
                new_combo=state.first_object
                or state.last_object_was_spinner()
                or new_combo,
                combo_offset=combo_offset if new_combo else 0,
                path=SliderPath(state.timing_points.mode, control_points, length),
                node_samples=node_samples,
                repeat_count=repeat_count,
                velocity=1.0,
            )

        elif hit_object_type.has_flag(HitObjectType.SPINNER):
            try:
                end_time_raw = float(parts[5])
                duration = max(0.0, end_time_raw, start_time)
            except (ValueError, IndexError):
                raise ParseHitObjectsError.invalid_line()

            if len(parts) > 6:
                bank_info.read_custom_sample_banks(iter(parts[6].split(":")), False)

            inner_kind = HitObjectSpinner(
                pos=Pos(256.0, 192.0), duration=duration, new_combo=new_combo
            )

        elif hit_object_type.has_flag(HitObjectType.HOLD):
            end_time = max(start_time, start_time_raw)
            if len(parts) > 5 and parts[5]:
                ss = parts[5].split(":")
                try:
                    end_time = max(start_time, float(ss[0]))
                    if len(ss) > 1:
                        bank_info.read_custom_sample_banks(iter(ss[1:]), False)
                except ValueError:
                    raise ParseHitObjectsError.invalid_line()

            inner_kind = HitObjectHold(pos_x=pos, duration=end_time - start_time)

        else:
            raise ParseHitObjectsError.unknown_hit_object_type(hit_object_type)

        kind_wrapper = HitObjectKind(inner_kind)

        result = HitObject(
            start_time=start_time,
            kind=kind,
            samples=bank_info.convert_sound_type(sound_type),
        )

        state.last_object = hit_object_type
        state.hit_objects.append(result)

    @classmethod
    def parse_variables(cls, state: HitObjectsState, line: str) -> None:
        pass

    @classmethod
    def parse_catch_the_beat(cls, state: HitObjectsState, line: str) -> None:
        pass

    @classmethod
    def parse_mania(cls, state: HitObjectsState, line: str) -> None:
        pass


class ParseHitObjectsError(Exception):
    def __init__(self, message: str, source: Exception | None = None):
        self.source = source
        super().__init__(message)

    @classmethod
    def difficulty(cls, err: Exception) -> ParseHitObjectsError:
        return cls("failed to parse difficulty section", err)

    @classmethod
    def events(cls, err: Exception) -> ParseHitObjectsError:
        return cls("failed to parse events section", err)

    @classmethod
    def hit_object_type(cls, err: Exception) -> ParseHitObjectsError:
        return cls("failed to parse hit object type", err)

    @classmethod
    def hit_sound_type(cls, err: Exception) -> ParseHitObjectsError:
        return cls("failed to parse hit sound type", err)

    @classmethod
    def invalid_line(cls) -> ParseHitObjectsError:
        return cls("invalid line")

    @classmethod
    def invalid_repeat_count(cls, count: int) -> ParseHitObjectsError:
        return cls(f"repeat count is way too high: {count}")

    @classmethod
    def number(cls, err: Exception) -> ParseHitObjectsError:
        return cls("failed to parse number", err)

    @classmethod
    def sample_bank_info(cls, err: Exception) -> ParseHitObjectsError:
        return cls("invalid sample bank", err)

    @classmethod
    def timing_points(cls, err: Exception) -> ParseHitObjectsError:
        return cls("failed to parse timing points", err)

    @classmethod
    def unknown_hit_object_type(cls, obj_type: HitObjectType) -> ParseHitObjectsError:
        return cls(f"unknown hit object type: {obj_type}")


@dataclass
class HitObjectsState:
    last_object: HitObjectType | None = None
    curve_points: list[PathControlPoint] = field(default_factory=list)
    vertices: list[PathControlPoint] = field(default_factory=list)
    events: EventsState = field(default_factory=lambda: EventsState())
    timing_points: TimingPointsState = field(
        default_factory=lambda: TimingPointsState()
    )
    difficulty: DifficultyState = field(default_factory=lambda: DifficultyState())
    hit_objects: list[HitObject] = field(default_factory=list)
    point_split: list[str] = field(default_factory=list)

    @property
    def first_object(self) -> bool:
        return self.last_object is None

    def last_object_was_spinner(self) -> bool:
        if self.last_object is None:
            return False
        return self.last_object.has_flag(HitObjectType.SPINNER)

    def convert_path_str(self, point_str: str, offset: Pos) -> None:
        points_split = point_str.split("|")

        start_idx = 0
        end_idx = 0
        first = True

        while True:
            end_idx += 1
            if end_idx >= len(points_split):
                break

            is_letter = (
                points_split[end_idx][0].isalpha() if points_split[end_idx] else False
            )
            if not is_letter:
                continue

            end_point = (
                points_split[end_idx + 1] if (end_idx + 1) < len(points_split) else None
            )
            self.convert_points(
                points_split[start_idx:end_idx], end_point, first, offset
            )

            start_idx = end_idx
            first = False

        if end_idx > start_idx:
            self.convert_points(points_split[start_idx:end_idx], None, first, offset)

    def convert_points(
        self, points: list[str], end_point: str | None, first: bool, offset: Pos
    ) -> None:
        if not points:
            raise ParseHitObjectsError.invalid_line()

        path_type: PathType = PathType.new_from_str(points[0])

        self.vertices.clear()
        if first:
            self.vertices.append(PathControlPoint(Pos(0, 0)))

        for p_str in points[1:]:
            self.vertices.append(self._read_point(p_str, offset))

        if end_point:
            self.vertices.append(self._read_point(end_point, offset))

        if path_type == PathType.perfect_curve():
            if len(self.vertices) == 3:
                if self._is_linear(
                    self.vertices[0].pos, self.vertices[1].pos, self.vertices[2].pos
                ):
                    path_type = PathType.linear()
            else:
                path_type = PathType.bezier()

        if self.vertices:
            self.vertices[0].path_type = path_type

        self._build_curve_points(path_type, bool(end_point))

    def _read_point(self, value: str, start_pos: Pos) -> PathControlPoint:
        try:
            parts = value.split(":")
            x = float(parts[0])
            y = float(parts[1])
            return PathControlPoint(Pos(x, y) - start_pos)
        except (ValueError, IndexError):
            raise ParseHitObjectsError.invalid_line()

    def _is_linear(self, p0: Pos, p1: Pos, p2: Pos) -> bool:
        return abs((p1.y - p0.y) * (p2.x - p0.x) - (p1.x - p0.x) * (p2.y - p0.y)) < 1e-3

    def _build_curve_points(self, path_type: PathType, has_end_point: bool) -> None:
        start_idx = 0
        end_idx = 0
        limit = len(self.vertices) - (1 if has_end_point else 0)

        while True:
            end_idx += 1
            if end_idx >= limit:
                break

            if self.vertices[end_idx].pos == self.vertices[end_idx - 1].pos:
                continue
            if path_type == PathType.catmull() and end_idx > 1:
                continue
            if end_idx == limit - 1:
                continue

            self.vertices[end_idx - 1].path_type = path_type
            self.curve_points.extend(self.vertices[start_idx:end_idx])
            start_idx = end_idx + 1

        if end_idx > start_idx:
            self.curve_points.extend(self.vertices[start_idx:end_idx])

    @staticmethod
    def post_process_breaks(hit_objects: list[HitObject], events: Any) -> None:
        curr_break = 0
        force_new_combo = False

        for h in hit_objects:
            while (
                curr_break < len(events.breaks)
                and events.breaks[curr_break].end_time < h.start_time
            ):
                force_new_combo = True
                curr_break += 1

            if force_new_combo:
                kind = h.kind
                if isinstance(kind, HitObjectCircle):
                    h.kind = HitObjectCircle(
                        pos=kind.pos,
                        new_combo=True,
                        combo_offset=kind.combo_offset,
                    )
                elif isinstance(kind, HitObjectSpinner):
                    h.kind = HitObjectSpinner(
                        pos=kind.pos,
                        duration=kind.duration,
                        new_combo=True,
                    )
            force_new_combo = False

    @classmethod
    def create(cls, version: int) -> HitObjectsState:
        return cls(
            last_object=None,
            curve_points=[],
            vertices=[],
            point_split=[],
            events=EventsState.create(version),
            timing_points=TimingPointsState.create(version),
            difficulty=DifficultyState.create(version),
            hit_objects=[],
        )


def get_precision_adjusted_beat_len(
    slider_velocity: float, beat_len: float, mode: GameMode
) -> float:
    slider_velocity_as_beat_len = -100.0 / slider_velocity
    if slider_velocity_as_beat_len < 0.0:
        val = -slider_velocity_as_beat_len

        if mode == GameMode.Osu or mode == GameMode.Catch:
            bpm_multiplier = max(10.0, min(val, 10000.0)) / 100.0
        elif mode == GameMode.Taiko or mode == GameMode.Mania:
            bpm_multiplier = max(10.0, min(val, 1000.0)) / 100.0
        else:
            bpm_multiplier = 1.0
    else:
        bpm_multiplier = 1.0

    return beat_len * bpm_multiplier


def finalize_hit_objects(state: HitObjectsState) -> HitObjects:
    CONTROL_POINT_LENIENCY = 5.0

    difficulty = state.difficulty.to_result()
    timing_points = state.timing_points.to_result()
    events = state.events

    hit_objects = state.hit_objects
    hit_objects.sort(key=lambda h: h.start_time)

    HitObjectsState.post_process_breaks(hit_objects, events)

    bufs = CurveBuffers()

    for h in hit_objects:
        if isinstance(h.kind, HitObjectSlider):
            slider = h.kind

            tp = timing_points.control_points.timing_point_at(h.start_time)
            beat_len = tp.beat_len if tp else TimingPoint.DEFAULT_BEAT_LEN

            dp = timing_points.control_points.difficulty_point_at(h.start_time)
            slider_velocity = (
                dp.slider_velocity if dp else DifficultyPoint.DEFAULT_SLIDER_VELOCITY
            )

            slider.velocity = (
                BASE_SCORING_DIST
                * difficulty.slider_multiplier
                / get_precision_adjusted_beat_len(
                    slider_velocity, beat_len, timing_points.mode
                )
            )

            duration = slider.duration_with_bufs(bufs)
            span_count = float(slider.span_count())

            for i, node_samples in enumerate(slider.node_samples):
                time = h.start_time + 1 * duration / span_count + CONTROL_POINT_LENIENCY
                sample_point = timing_points.control_points.sample_point_at(time)

                for sample in node_samples:
                    if sample_point:
                        sample_point.apply(sample)

        end_time = h.end_time_with_bufs(bufs)

        sample_point = timing_points.control_points.sample_point_at(
            end_time + CONTROL_POINT_LENIENCY
        )

        for sample in h.samples:
            if sample_point:
                sample_point.apply(sample)

    return HitObjects(
        audio_file=timing_points.audio_file,
        audio_lead_in=timing_points.audio_lead_in,
        preview_time=timing_points.preview_time,
        default_sample_bank=timing_points.default_sample_bank,
        default_sample_volume=timing_points.default_sample_volume,
        stack_leniency=timing_points.stack_leniency,
        mode=timing_points.mode,
        letterbox_in_breaks=timing_points.letterbox_in_breaks,
        special_style=timing_points.special_style,
        widescreen_storyboard=timing_points.widescreen_storyboard,
        epilepsy_warning=timing_points.epilepsy_warning,
        samples_match_playback_rate=timing_points.samples_match_playback_rate,
        countdown=timing_points.countdown,
        countdown_offset=timing_points.countdown_offset,
        hp_drain_rate=difficulty.hp_drain_rate,
        circle_size=difficulty.circle_size,
        overall_difficulty=difficulty.overall_difficulty,
        approach_rate=difficulty.approach_rate,
        slider_multiplier=difficulty.slider_multiplier,
        slider_tick_rate=difficulty.slider_tick_rate,
        background_file=events.background_file,
        breaks=events.breaks,
        control_points=timing_points.control_points,
        hit_objects=hit_objects,
    )
