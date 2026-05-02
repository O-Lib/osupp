import collections
from typing import Optional, List

from osupp.Beatmap.section.enums import GameMode, HitSoundType
from osupp.Beatmap.section.events import BreakPeriod
from ...utils.sort import osu_legacy_sort
from .attributes import BeatmapAttributesBuilder
from osupp.Mods.game_mods import GameMods
from ...any.performance import Performance, GradualPerformance
from ...any.difficulty import Difficulty, GradualDifficulty
from ...catch.catch import Catch
from ...mania.convert.convert import Mania
from ...taiko.taiko import Taiko
from ..model import HitObject
from ..control_points import TimingPoint, DifficultyPoint, EffectPoint


def _round_ties_even(num: float) -> float:
    return round(num)


class BeatLenDuration:
    __slots__ = ("last_time", "map_")

    def __init__(self, last_time: float):
        self.last_time = last_time
        self.map_ = collections.defaultdict(float)

    def add(self, beat_len: float, curr_time: float, next_time: float) -> None:
        b_len = _round_ties_even(1000.0 * beat_len) / 1000.0
        if curr_time <= self.last_time:
            self.map_[b_len] += next_time - curr_time


def get_bpm(last_hit_object: Optional[HitObject], timing_points: List[TimingPoint]) -> float:
    last_time = 0.0
    if last_hit_object is not None:
        if hasattr(last_hit_object, "end_time") and callable(getattr(last_hit_object, "end_time")):
            last_time = last_hit_object.end_time()
        elif hasattr(last_hit_object, "start_time"):
            last_time = last_hit_object.start_time
    elif timing_points:
        last_time = timing_points[-1].time

    bpm_points = BeatLenDuration(last_time)

    if len(timing_points) == 1:
        bpm_points.add(timing_points[0].beat_len, 0.0, last_time)
    elif len(timing_points) >= 2:
        bpm_points.add(timing_points[0].beat_len, 0.0, timing_points[1].time)

    for i in range(1, len(timing_points)):
        curr = timing_points[i]
        next_time = timing_points[i + 1].time if i + 1 < len(timing_points) else last_time
        bpm_points.add(curr.beat_len, curr.time, next_time)

    if not bpm_points.map_:
        return 0.0

    most_common_beat_len = max(bpm_points.map_.items(), key=lambda x: x[1])[0]

    if most_common_beat_len == 0.0:
        return 0.0

    return 60000.0 / most_common_beat_len


class TooSuspicious(Exception):
    DENSITY = "Density"
    LENGTH = "Length"
    OBJECT_COUNT = "ObjectCount"
    RED_FLAG = "RedFlag"
    SLIDER_POSITIONS = "SliderPositions"
    SLIDER_REPEATS = "SliderRepeats"

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"the map seems too suspicious for further calculation (reason={self.reason})")


THRESHOLD_1S = 200
THRESHOLD_10S = 500


class SliderState:
    __slots__ = ("repeats_beyond_threshold", "pos_beyond_threshold")

    def __init__(self):
        self.repeats_beyond_threshold = 0
        self.pos_beyond_threshold = 0

    def eval(self) -> Optional[TooSuspicious]:
        CUTOFF = 128
        if self.pos_beyond_threshold > CUTOFF:
            return TooSuspicious(TooSuspicious.SLIDER_POSITIONS)
        elif self.repeats_beyond_threshold > CUTOFF:
            return TooSuspicious(TooSuspicious.SLIDER_REPEATS)
        return None


def check_suspicion(map_obj: "Beatmap") -> Optional[TooSuspicious]:
    def too_long(hitobjects: List[HitObject]) -> bool:
        DAY_MS = 60 * 60 * 24 * 1000
        if len(hitobjects) < 2:
            return False
        return (hitobjects[-1].start_time - hitobjects[0].start_time) > float(DAY_MS)

    def too_many_objects(map_ref: "Beatmap") -> bool:
        THRESHOLD = 500000
        THRESHOLD_TAIKO = 30000
        if map_ref.mode == GameMode.Taiko:
            return len(map_ref.hit_objects) > THRESHOLD_TAIKO
        return len(map_ref.hit_objects) > THRESHOLD

    if too_many_objects(map_obj):
        return TooSuspicious(TooSuspicious.OBJECT_COUNT)
    elif too_long(map_obj.hit_objects):
        return TooSuspicious(TooSuspicious.LENGTH)

    if map_obj.mode == GameMode.Osu:
        return _check_osu(map_obj)
    elif map_obj.mode == GameMode.Taiko:
        return _check_taiko(map_obj)
    elif map_obj.mode == GameMode.Catch:
        return _check_catch(map_obj)
    elif map_obj.mode == GameMode.Mania:
        return _check_mania(map_obj)

    return None


def _too_dense(hit_objects: List[HitObject], i: int, per_1s: int, per_10s: int) -> bool:
    if len(hit_objects) > i + per_1s and hit_objects[i + per_1s].start_time - hit_objects[i].start_time < 1000.0:
        return True
    if len(hit_objects) > i + per_10s and hit_objects[i + per_10s].start_time - hit_objects[i].start_time < 10000.0:
        return True
    return False


def _suspicious_slider(h: HitObject, state: SliderState) -> bool:
    def check_pos(pos) -> bool:
        THRESHOLD = 10000.0
        return abs(pos.x) > THRESHOLD or abs(pos.y) > THRESHOLD

    def check_repeats(repeats: int) -> bool:
        THRESHOLD = 1000
        return repeats > THRESHOLD

    if h.is_slider():
        if check_repeats(h.kind.repeats):
            if check_pos(h.pos):
                return True
            state.repeats_beyond_threshold += 1
        elif check_pos(h.pos):
            state.pos_beyond_threshold += 1

    return False


def _check_osu(map_obj: "Beatmap") -> Optional[TooSuspicious]:
    state = SliderState()
    per_1s = THRESHOLD_1S
    per_10s = THRESHOLD_10S

    for i, h in enumerate(map_obj.hit_objects):
        if _too_dense(map_obj.hit_objects, i, per_1s, per_10s):
            return TooSuspicious(TooSuspicious.DENSITY)
        elif _suspicious_slider(h, state):
            return TooSuspicious(TooSuspicious.RED_FLAG)

    return state.eval()


def _check_taiko(map_obj: "Beatmap") -> Optional[TooSuspicious]:
    per_1s = THRESHOLD_1S * 2
    per_10s = THRESHOLD_10S * 2

    for i in range(len(map_obj.hit_objects)):
        if _too_dense(map_obj.hit_objects, i, per_1s, per_10s):
            return TooSuspicious(TooSuspicious.DENSITY)
    return None


def _check_catch(map_obj: "Beatmap") -> Optional[TooSuspicious]:
    state = SliderState()
    for h in map_obj.hit_objects:
        if _suspicious_slider(h, state):
            return TooSuspicious(TooSuspicious.RED_FLAG)
    return state.eval()

def _check_mania(map_obj: "Beatmap") -> Optional[TooSuspicious]:
    keys_per_hand = max(1, int(map_obj.cs) // 2)
    per_1s = THRESHOLD_1S * keys_per_hand
    per_10s = THRESHOLD_10S * keys_per_hand

    for i in range(len(map_obj.hit_objects)):
        if _too_dense(map_obj.hit_objects, i, per_1s, per_10s):
            return TooSuspicious(TooSuspicious.DENSITY)
    return None


class ParseBeatmapError(Exception):
    pass


class Beatmap:
    __slots__ = (
        "version", "is_convert", "stack_leniency", "mode", "ar", "cs", "hp", "od", "slider_multiplier", "slider_tick_rate", "breaks",
        "timing_points", "difficulty_points", "effect_points", "hit_objects", "hit_sounds"
    )

    def __init__(self):
        self.version = 14
        self.is_convert = False
        self.stack_leniency = 0.7
        self.mode = GameMode.Osu
        self.ar = 5.0
        self.cs = 5.0
        self.hp = 5.0
        self.od = 5.0
        self.slider_multiplier = 1.4
        self.slider_tick_rate = 1.0

        self.breaks: List[BreakPeriod] = []
        self.timing_points: List[TimingPoint] = []
        self.difficulty_points: List[DifficultyPoint] = []
        self.effect_points: List[EffectPoint] = []
        self.hit_objects: List[HitObject] = []
        self.hit_sounds: List[HitSoundType] = []

    def attributes(self) -> BeatmapAttributesBuilder:
        builder = BeatmapAttributesBuilder()
        builder.map(self)
        return builder

    def bpm(self) -> float:
        last_obj = self.hit_objects[-1] if self.hit_objects else None
        return get_bpm(last_obj, self.timing_points)

    def performance(self) -> Performance:
        return Performance(self)

    def gradual_difficulty(self, difficulty: Difficulty) -> GradualDifficulty:
        return GradualDifficulty(difficulty, self)

    def gradual_performance(self, difficulty: Difficulty) -> GradualPerformance:
        return GradualPerformance(difficulty, self)

    def timing_point_at(self, time: float) -> Optional[TimingPoint]:
        if not self.timing_points:
            return None
        lo, hi = 0, len(self.timing_points)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.timing_points[mid].time <= time:
                lo = mid + 1
            else:
                hi = mid
        return self.timing_points[max(0, lo - 1)]

    def difficulty_point_at(self, time: float) -> Optional[DifficultyPoint]:
        if not self.difficulty_points:
            return None
        lo, hi = 0, len(self.difficulty_points)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.difficulty_points[mid].time <= time:
                lo = mid + 1
            else:
                hi = mid
        return self.difficulty_points[max(0, lo - 1)]

    def effect_point_at(self, time: float) -> Optional[EffectPoint]:
        if not self.effect_points:
            return None
        lo, hi = 0, len(self.effect_points)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.effect_points[mid].time <= time:
                lo = mid + 1
            else:
                hi = mid
        return self.effect_points[max(0, lo - 1)]

    def total_break_time(self) -> float:
        return sum(b.duration() for b in self.breaks)

    def convert(self, mode: GameMode, mods: GameMods) -> "Beatmap":
        self.convert_mut(mode, mods)
        return self

    def convert_mut(self, mode: GameMode, mods: GameMods) -> None:
        if self.mode == mode:
            return
        if self.is_convert:
            raise ValueError("Already Converted")
        if self.mode != GameMode.Osu:
            raise ValueError(f"Cannot convert from {self.mode} to {mode}")

        if mode == GameMode.Taiko:
            Taiko.convert(self)
        elif mode == GameMode.Catch:
            Catch.convert(self)
        elif mode == GameMode.Mania:
            Mania.convert(self, mods)
        elif mode == GameMode.Osu:
            pass

    def mania_hit_objects_legacy_sort(self) -> None:
        def cmp_func(a: HitObject, b: HitObject) -> int:
            a_time = int(_round_ties_even(a.start_time))
            b_time = int(_round_ties_even(b.start_time))
            if a_time < b_time: return -1
            if a_time > b_time: return 1
            return 0

        osu_legacy_sort(self.hit_objects, cmp_func)

    def check_suspicion(self) -> None:
        err = check_suspicion(self)
        if err is not None:
            raise err