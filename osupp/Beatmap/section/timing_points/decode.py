import bisect
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from section.general import CountdownType, GameMode, General, GeneralState
from section.hit_objects.hit_samples import SampleBank
from utils import MAX_PARSE_VALUE, StrExtra

from .control_points.difficulty import DifficultyPoint
from .control_points.effect import EffectPoint
from .control_points.sample import SamplePoint
from .control_points.timing import TimeSignature, TimingPoint
from .effect_flags import EffectFlags


@dataclass
class ControlPoints:
    timing_points: list[TimingPoint] = field(default_factory=list)
    difficulty_points: list[DifficultyPoint] = field(default_factory=list)
    effect_points: list[EffectPoint] = field(default_factory=list)
    sample_points: list[SamplePoint] = field(default_factory=list)

    @classmethod
    def default(cls) -> "ControlPoints":
        return cls()

    def find_at(self, points: list, time: float):
        if not points:
            return None

        idx = bisect.bisect_right(points, time, key=lambda p: p.time)
        return points[idx - 1] if idx > 0 else None

    def difficulty_point_at(self, time: float) -> DifficultyPoint | None:
        return self.find_at(self.difficulty_points, time)

    def effect_point_at(self, time: float) -> EffectPoint | None:
        return self.find_at(self.effect_points, time)

    def sample_point_at(self, time: float) -> SamplePoint | None:
        return self.find_at(self.sample_points, time)

    def timing_point_at(self, time: float) -> TimingPoint | None:
        return self.find_at(self.timing_points, time)

    def add(self, point) -> None:
        if not point.check_already_existing(self):
            point.add_to(self)


class ParseTimingPointsError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class EffectFlagsError(ParseTimingPointsError):
    def __init__(self, source: Exception):
        super().__init__(f"failed to parse effect flags: {source}")


class GeneralSectionError(ParseTimingPointsError):
    def __init__(self, source: Exception):
        super().__init__(f"failed to parse general section: {source}")


class InvalidLineError(ParseTimingPointsError):
    def __init__(self):
        super().__init__("invalid line")


class NumberParseError(ParseTimingPointsError):
    def __init__(self, source: Exception):
        super().__init__(f"failed to parse number: {source}")


class SampleBankParseError(ParseTimingPointsError):
    def __init__(self, source: Exception):
        super().__init__(f"failed to parse sample bank: {source}")


class TimeSignatureParseError(ParseTimingPointsError):
    def __init__(self, source: Exception):
        super().__init__(f"time signature error: {source}")


class TimingControlPointNaNError(ParseTimingPointsError):
    def __init__(self):
        super().__init__("beat length cannot be NaN in a timing control point")


@dataclass
class TimingPoints:
    audio_file: str
    audio_lead_in: float
    preview_time: int
    default_sample_bank: SampleBank
    default_sample_volume: int
    stack_leniency: float
    mode: GameMode
    letterbox_in_breaks: bool
    special_style: bool
    widescreen_storyboard: bool
    epilepsy_warning: bool
    samples_match_playback_rate: bool
    countdown: CountdownType
    countdown_offset: int

    control_points: ControlPoints

    @classmethod
    def default(cls) -> "TimingPoints":
        general = General.default()

        return cls(
            audio_file=general.audio_file,
            audio_lead_in=general.audio_lead_in,
            preview_time=general.preview_time,
            default_sample_bank=general.default_sample_bank,
            default_sample_volume=general.default_sample_volume,
            stack_leniency=general.stack_leniency,
            mode=general.mode,
            letterbox_in_breaks=general.letterbox_in_breaks,
            special_style=general.special_style,
            widescreen_storyboard=general.widescreen_storyboard,
            epilepsy_warning=general.epilepsy_warning,
            samples_match_playback_rate=general.samples_match_playback_rate,
            countdown=general.countdown,
            countdown_offset=general.countdown_offset,
            control_points=ControlPoints.default(),
        )

    @classmethod
    def from_state(cls, state: "TimingPointsState") -> "TimingPoints":
        state.flush_pending_points()

        return cls(
            audio_file=state.general.audio_file,
            audio_lead_in=state.general.audio_lead_in,
            preview_time=state.general.preview_time,
            default_sample_bank=state.general.default_sample_bank,
            default_sample_volume=state.general.default_sample_volume,
            stack_leniency=state.general.stack_leniency,
            mode=state.general.mode,
            letterbox_in_breaks=state.general.letterbox_in_breaks,
            special_style=state.general.special_style,
            widescreen_storyboard=state.general.widescreen_storyboard,
            epilepsy_warning=state.general.epilepsy_warning,
            samples_match_playback_rate=state.general.samples_match_playback_rate,
            countdown=state.general.countdown,
            countdown_offset=state.general.countdown_offset,
            control_points=state.control_points,
        )

    @staticmethod
    def parse_general(state: "TimingPointsState", line: str):
        try:
            General.parse_general(state.general, line)
        except Exception as e:
            raise GeneralSectionError(e)

    @staticmethod
    def parse_editor(state: "TimingPointsState", line: str):
        pass

    @staticmethod
    def parse_metadata(state: "TimingPointsState", line: str):
        pass

    @staticmethod
    def parse_difficulty(state: "TimingPointsState", line: str):
        pass

    @staticmethod
    def parse_events(state: "TimingPointsState", line: str):
        pass

    @staticmethod
    def parse_timing_points(state: "TimingPointsState", line: str):
        line = StrExtra.trim_comment(line)
        if not line:
            return

        parts = line.split(",")
        if len(parts) < 2:
            return

        try:
            time = float(parts[0])

            try:
                beat_len = float(parts[1])
            except ValueError as e:
                raise NumberParseError(e)

            if beat_len < -MAX_PARSE_VALUE:
                raise NumberParseError(Exception("Underflow"))
            elif beat_len > MAX_PARSE_VALUE:
                raise NumberParseError(Exception("Overflow"))

            speed_multipler = 100.0 / -beat_len if beat_len < 0.0 else 1.0

            time_signature = TimeSignature.new_simple_quadruple()
            if len(parts) > 2 and parts[2].strip():
                if not parts[2].startswith("0"):
                    time_signature = TimeSignature.new(int(parts[2]))

            sample_set = state.general.default_sample_bank
            if len(parts) > 3 and parts[3].strip():
                try:
                    val = int(parts[3])
                    sample_set = SampleBank(val) if val > 0 else SampleBank.NORMAL
                except (ValueError, IndexError):
                    pass

            if sample_set == SampleBank.NONE:
                sample_set = SampleBank.NORMAL

            custom_sample_bank = (
                int(parts[4]) if len(parts) > 4 and parts[4].strip() else 0
            )

            sample_volume = state.general.default_sample_volume
            if len(parts) > 5 and parts[5].strip():
                sample_volume = int(parts[5])

            timing_change = (
                parts[6].startswith("1")
                if len(parts) > 6 and parts[6].strip()
                else True
            )

            kiai_mode = False
            omit_first_bar_signature = False
            if len(parts) > 7 and parts[7].strip():
                effects_flags = EffectFlags.parse(parts[7])
                kiai_mode = effects_flags.has_flag(EffectFlags.KIAI)
                omit_first_bar_signature = effects_flags.has_flag(
                    EffectFlags.OMIT_FIRST_BAR_LINE
                )

            if timing_change:
                if math.isnan(beat_len):
                    raise TimingControlPointNaNError

                timing = TimingPoint(
                    time, beat_len, omit_first_bar_signature, time_signature
                )
                state.add_control_point(time, timing, timing_change)

            state.add_control_point(
                time,
                DifficultyPoint(time=time, beat_len=beat_len, speed_multipler=speed_multipler),
                False
            )

            sample = SamplePoint(time, sample_set, sample_volume, custom_sample_bank)
            state.add_control_point(time, sample, timing_change)

            effect = EffectPoint(time=time, kiai_mode=kiai_mode, scroll_speed=1.0)
            if state.mode in (GameMode.Taiko, GameMode.Mania):
                effect.scroll_speed = max(0.01, min(10.0, speed_multipler))

            state.add_control_point(
                time,
                effect,
                False
            )

            state.pending_control_points_time = time

        except (ValueError, IndexError) as e:
            raise ParseTimingPointsError(str(e), e)

    @staticmethod
    def parse_colors(state: "TimingPointsState", line: str):
        pass

    @staticmethod
    def parse_hit_objects(state: "TimingPointsState", line: str):
        pass

    @staticmethod
    def parse_variables(state: "TimingPointsState", line: str):
        pass

    @staticmethod
    def parse_catch_the_beat(state: "TimingPointsState", line: str):
        pass

    @staticmethod
    def parse_mania(state: "TimingPointsState", line: str):
        pass


class ControlPoint(ABC):
    @abstractmethod
    def check_already_existing(self, control_points: "ControlPoints") -> bool:
        pass

    @abstractmethod
    def add_to(self, control_points: "ControlPoints") -> None:
        pass


@dataclass
class TimingPointsState:
    general: GeneralState = field(default_factory=GeneralState)
    pending_control_points_time: float = 0.0

    pending_timing_point: TimingPoint | None = None
    pending_difficulty_point: DifficultyPoint | None = None
    pending_effect_point: EffectPoint | None = None
    pending_sample_point: SamplePoint | None = None

    control_points: ControlPoints = field(default_factory=ControlPoints)

    @classmethod
    def create(cls, version: int) -> "TimingPointsState":
        return cls(
            general=GeneralState.create(version),
            pending_control_points_time=0.0,
            pending_timing_point=None,
            pending_difficulty_point=None,
            pending_effect_point=None,
            pending_sample_point=None,
            control_points=ControlPoints.default(),
        )

    def to_result(self) -> "TimingPoints":
        return self.control_points.timing_points

    @property
    def mode(self) -> GameMode:
        return self.general.mode

    def pending(self, point: Any) -> str:
        if isinstance(point, TimingPoint):
            return "pending_timing_point"
        if isinstance(point, DifficultyPoint):
            return "pending_difficulty_point"
        if isinstance(point, EffectPoint):
            return "pending_effect_point"
        if isinstance(point, SamplePoint):
            return "pending_sample_point"

        raise TypeError(f"Point Type Unknown: {type(point)}")

    def push_front(self, point: Any) -> None:
        slot = self.pending(point)
        if getattr(self, slot) is None:
            setattr(self, slot, point)

    def push_back(self, point: Any) -> None:
        slot = self.pending(point)
        setattr(self, slot, point)

    def add_control_point(self, time: float, point: Any, timing_change: bool) -> None:
        if abs(time - self.pending_control_points_time) >= 1e-15:
            self.flush_pending_points()

        if timing_change:
            self.push_front(point)
        else:
            self.push_back(point)

        self.pending_control_points_time = time

    def flush_pending_points(self) -> None:
        if self.pending_timing_point is not None:
            self.control_points.add(self.pending_timing_point)
            self.pending_timing_point = None

        if self.pending_difficulty_point is not None:
            self.control_points.add(self.pending_difficulty_point)
            self.pending_difficulty_point = None

        if self.pending_effect_point is not None:
            self.control_points.add(self.pending_effect_point)
            self.pending_effect_point = None

        if self.pending_sample_point is not None:
            self.control_points.add(self.pending_sample_point)
            self.pending_sample_point = None
