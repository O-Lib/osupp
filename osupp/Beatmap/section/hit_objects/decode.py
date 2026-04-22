from section.difficulty import Difficulty, DifficultyState, ParseDifficultyError
from section.events import BreakPeriod, Events, EventsState, ParseEventsError
from section.general import CountdownType, GameMode
from section.hit_objects import PathType, CurveBuffers, BASE_SCORING_DIST, HitObject, HitObjectCircle, HitObjectHold, HitObjectKind, HitObjectSlider, HitObjectSpinner, HitObjectType, ParseHitObjectTypeError, PathControlPoint, SliderPath
from section.timing_points import ControlPoints, DifficultyPoint, ParseTimingPointsError, SamplePoint, TimingPoint, TimingPoints, TimingPointsState
from utils import Pos, ParseNumber, ParseNumberError, StrExtra
from beatmap import Beatmap
from hit_samples import HitSoundType, ParseHitSoundTypeError, ParseSampleBankInfoError, SampleBank, SampleBankInfo

from dataclasses import dataclass, field
from typing import List, Optional

class HitObjects:
    # General
    audio_file: str = ""
    audio_lead_in: float = 0.0
    preview_time: int = 0
    default_sample_bank: SampleBank = SampleBank.NORMAL
    default_sample_volume: int = 100
    stack_leniency: float = 0.7
    mode: 'GameMode' = None  # Placeholder para o Enum de GameMode
    letterbox_in_breaks: bool = False
    special_style: bool = False
    widescreen_storyboard: bool = False
    epilepsy_warning: bool = False
    samples_match_playback_rate: bool = False
    countdown: 'CountdownType' = None  # Placeholder
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
    breaks: List['BreakPeriod'] = field(default_factory=list)

    # TimingPoints
    control_points: 'ControlPoints' = field(default_factory=lambda: ControlPoints())

    # HitObjects específicos
    hit_objects: List['HitObject'] = field(default_factory=list)

class ParseHitObjectsError(Exception):
    def __init__(self, message: str, source: Exception = None):
        self.source = source
        super().__init__(message)

    @classmethod
    def difficulty(cls, err: ParseDifficultyError):
        return cls("failed to parse difficulty section", err)

    @classmethod
    def events(cls, err: ParseEventsError):
        return cls("failed to parse events section", err)

    @classmethod
    def hit_object_type(cls, err: ParseHitObjectTypeError):
        return cls("failed to parse hit object type", err)

    @classmethod
    def hit_sound_type(cls, err: ParseHitSoundTypeError):
        return cls("failed to parse hit sound type", err)

    @classmethod
    def invalid_line(cls):
        return cls("invalid line")

    @classmethod
    def invalid_repeat_count(cls, count: int):
        return cls(f"repeat count is way too high: {count}")

    @classmethod
    def number(cls, err: ParseNumberError):
        return cls("failed to parse number", err)

    @classmethod
    def sample_bank_info(cls, err: ParseSampleBankInfoError):
        return cls("invalid sample bank", err)

    @classmethod
    def timing_points(cls, err: ParseTimingPointsError):
        return cls("failed to parse timing points", err)

    @classmethod
    def unknown_hit_object_type(cls, obj_type: 'HitObjectType'):
        return cls(f"unknown hit object type: {obj_type}")

@dataclass
class HitObjectsState:
    last_object: Optional[HitObjectType] = None
    curve_points: List[PathControlPoint] = field(default_factory=list)
    vertices: List[PathControlPoint] = field(default_factory=list)
    events: 'EventsState' = field(default_factory=lambda: EventsState())
    timing_points: 'TimingPointsState' = field(default_factory=lambda: TimingPointsState())
    difficulty: 'DifficultyState' = field(default_factory=lambda: DifficultyState())
    hit_objects: List[HitObject] = field(default_factory=list)
    point_split: List[str] = field(default_factory=list)

    def difficulty_ref(self):
        return self.difficulty.difficulty

    @property
    def first_object(self) -> bool:
        return self.last_object is None

    def last_object_was_spinner(self) -> bool:
        if self.last_object is None:
            return False
        return self.last_object.has_flag(HitObjectType.SPINNER)

    def convert_path_str(self, point_str: str, offset: Pos) -> None:
        points_split = point_str.split('|')

        start_idx = 0
        end_idx = 0
        first = True

        while True:
            end_idx += 1
            if end_idx >= len(points_split):
                break

            is_letter = points_split[end_idx][0].isalpha() if points_split[end_idx] else False
            if not is_letter:
                continue

            end_point = points_split[end_idx + 1] if (end_idx + 1) < len(points_split) else None
            self.convert_points(points_split[start_idx:end_idx], end_point, first, offset)

            start_idx = end_idx
            first = False

        if end_idx > start_idx:
            self.convert_points(points_split[start_idx:end_idx], None, first, offset)

    def convert_points(self, points: List[str], end_point: Optional[str], first: bool, offset: Pos) -> None:
        if not points:
            raise ParseHitObjectsError.invalid_line()

        path_type = PathType.new_from_str(points[0])

        self.vertices.clear()
        if first:
            self.vertices.append(PathControlPoint(Pos(0, 0)))

        for p_str in points[1]:
            self.vertices.append(self._read_point(p_str, offset))

        if end_point:
            self.vertices.append(self._read_point(end_point, offset))

        if path_type == PathType.perfect_curve:
            if len(self.vertices) == 3:
                if self._is_linear(self.vertices[0].pos, self.vertices[1].pos, self.vertices[2].pos):
                    path_type = PathType.linear
            else:
                path_type = PathType.bezier

        if self.vertices:
            self.vertices[0].path_type = path_type

        self._build_curve_points(path_type, bool(end_point))

    def _read_point(self, value: str, start_pos: Pos) -> PathControlPoint:
        try:
            parts = value.split(':')

            x = float(parts[0])
            y = float(parts[1])

            return PathControlPoint(Pos(x, y) - start_pos)
        except (ValueError, IndexError):
            raise ParseHitObjectsError.invalid_line()

    def _is_linear(self, p0: Pos, p1: Pos, p2: Pos) -> bool:
        return abs((p1.y - p0.y) * (p2.x - p0.x) - (p1.x - p0.x) * (p2.y - p0.y)) < 1e-5

    def _build_curve_points(self, path_type: PathType, has_end_point: bool):
        start_idx = 0
        end_idx = 0
        limit = len(self.vertices) - (1 if has_end_point else 0)

        while True:
            end_idx += 1
            if end_idx >= limit:
                break

            if self.vertices[end_idx].pos != self.vertices[end_idx - 1].pos:
                continue
            if path_type == PathType.catmull and end_idx > 1:
                continue
            if end_idx == limit - 1:
                continue

            self.vertices[end_idx - 1].path_type = path_type
            self.curve_points.extend(self.vertices[start_idx:end_idx])
            start_idx = end_idx + 1

        if end_idx > start_idx:
            self.curve_points.extend(self.vertices[start_idx:end_idx])

    @staticmethod
    def post_process_breaks(hit_objects: List[HitObject], events: Any):
        curr_break = 0
        force_new_combo = False

        for h in hit_objects:
            while curr_break < len(events.breaks) and events.breaks[curr_break].end_time < h.start_time:
                force_new_combo = True
                curr_break += 1

            if force_new_combo and hasattr(h.kind, "new_combo"):
                h.kind.new_combo = True
            force_new_combo = False