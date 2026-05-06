import math
from dataclasses import dataclass, field
from typing import Optional, Iterator, List, Any

from .skills import OsuSkills
from ...utils.utils import reverse_lerp, clamp, almost_eq
from ...model.model import GameMods
from ...model.beatmap.beatmap import Beatmap
from ...any.difficulty import Difficulty
from ...any.any import DifficultyAttributes
from ..osu import OsuDifficultyAttributes, OsuObject, convert_objects


STAR_RATING_MULTIPLIER = 0.0265
DIFFICULTY_MULTIPLIER = 0.0675
PERFORMANCE_BASE_MULTIPLIER = 1.12
BROKEN_GAMEFIELD_ROUNDING_ALLOWANCE = 1.00041


@dataclass(slots=True)
class ScalingFactor:
    factor: float
    radius: float
    scale: float

    @classmethod
    def new(cls, cs: float) -> "ScalingFactor":
        scale = (1.0 - 0.7 * ((cs - 5.0) / 5.0)) / 2.0 * BROKEN_GAMEFIELD_ROUNDING_ALLOWANCE
        radius = 64.0 * scale
        factor = 50.0 / radius
        return cls(factor=factor, radius=radius, scale=scale)


@dataclass(slots=True)
class OsuDifficultyObject:
    idx: int
    base: OsuObject
    start_time: float
    delta_time: float
    adjusted_delta_time: float
    lazy_jump_dist: float
    min_jump_dist: float
    min_jump_time: float
    travel_dist: float
    travel_time: float
    lazy_travel_dist: float
    lazy_travel_time: float
    angle: Optional[float] = None
    small_circle_bonus: float = 0.0

    NORMALIZED_RADIUS: int = 50
    MIN_DELTA_TIME: float = 25.0

    @classmethod
    def new(cls,
            current: OsuObject,
            last: OsuObject,
            last_diff: Optional["OsuDifficultyObject"],
            last_last_diff: Optional["OsuDifficultyObject"],
            clock_rate: float,
            idx: int,
            scaling: ScalingFactor) -> "OsuDifficultyObject":

        delta_time = (current.start_time - last.start_time) / clock_rate
        adjusted_delta_time = max(delta_time, cls.MIN_DELTA_TIME)

        curr_pos = current.stacked_pos * scaling.factor
        last_pos = last.stacked_pos * scaling.factor
        last_end_pos = (last_diff.lazy_end_pos if last_diff and last_diff.lazy_end_pos
                        else last.stacked_pos * scaling.factor)

        lazy_jump_dist = (curr_pos - last_end_pos).length()
        min_jump_time = adjusted_delta_time
        min_jump_dist = lazy_jump_dist

        small_circle_bonus = 1.0
        if scaling.radius < 30.0:
            small_circle_bonus += (30.0 - scaling.radius) / 40.0

        obj = cls(
            idx=idx,
            base=current,
            start_time=current.start_time / clock_rate,
            delta_time=delta_time,
            adjusted_delta_time=adjusted_delta_time,
            lazy_jump_dist=lazy_jump_dist,
            min_jump_dist=min_jump_dist,
            min_jump_time=min_jump_time,
            travel_dist=0.0,
            travel_time=0.0,
            small_circle_bonus=small_circle_bonus
        )

        if getattr(current.kind, "is_slider", False):
            obj._compute_slider_cursor_pos(current, scaling.factor)

        if last_diff:
            last_last_pos = (_get_previous_pos(idx, 1, scaling.factor))
            if last_last_pos:
                v1 = last_last_pos - last_pos
                v2 = curr_pos - last_end_pos
                dot = v1.dot(v2)
                det = v1.x * v2.y - v1.y * v2.x
                obj.angle = abs(math.atan2(det, dot))

        return obj

    def _compute_slider_cursor_pos(self, slider_obj: OsuObject, factor: float):
        self.lazy_end_pos = self.base.stacked_pos * factor

    def get_doubletapness(self, next_obj: Optional["OsuDifficultyObject"], hit_window: float) -> float:
        if not next_obj: return 0.0
        delta = next_obj.delta_time
        return reverse_lerp(delta, hit_window * 0.5, hit_window)

def _get_previous_pos(idx: int, steps: int, diff_objects: list[OsuDifficultyObject]) -> Optional[Any]:
    pos_idx = idx - 1 - steps
    if pos_idx >= 0:
        return diff_objects[pos_idx].base.stacked_pos
    return None


class OsuRatingCalculator:
    __slots__ = ("mods", "total_hits", "approach_rate", "overall_difficulty", "mech_diff_rating", "slider_factor")

    def __init__(self, mods: GameMods, total_hits: int, ar: float, od: float, mech_diff: float, slider_factor: float):
        self.mods = mods
        self.total_hits = total_hits
        self.approach_rate = ar
        self.overall_difficulty = od
        self.mech_diff_rating = mech_diff
        self.slider_factor = slider_factor

    def compute_aim_rating(self, aim_diff_value: float) -> float:
        if self.mods.ap:
            return 0.0

        aim_rating = aim_diff_value ** 0.5 * DIFFICULTY_MULTIPLIER

        if self.mods.td:
            aim_rating = aim_rating ** 0.8

        reading_bonus = self._calculate_reading_bonus(self.approach_rate)
        return aim_rating * (1.0 + reading_bonus)

    def compute_speed_rating(self, speed_diff_value: float) -> float:
        if self.mods.rx:
            return 0.0

        speed_rating = speed_diff_value ** 0.5 * DIFFICULTY_MULTIPLIER
        reading_bonus = self._calculate_reading_bonus(self.approach_rate)
        return speed_rating * (1.0 + reading_bonus)

    def compute_flashlight_rating(self, fl_diff_value: float) -> float:
        if not self.mods.fl:
            return 0.0
        return fl_diff_value ** 0.5 * DIFFICULTY_MULTIPLIER

    def _calculate_reading_bonus(self, ar: float) -> float:
        reading_bonus = 0.0
        if ar > 10.33:
            reading_bonus += 0.075 * (ar - 10.33)
        elif ar < 8.0:
            reading_bonus += 0.1225 + (8.0 - ar)
        return reading_bonus

    @staticmethod
    def calculate_difficulty_rating(val: float) -> float:
        return math.sqrt(val) * DIFFICULTY_MULTIPLIER


def calculate_star_rating(base_performance: float) -> float:
    if base_performance <= 0.00001:
        return 0.0
    return (PERFORMANCE_BASE_MULTIPLIER ** (1/3)) * STAR_RATING_MULTIPLIER * (((100000.0 / (2.0 ** (1.0/1.1)) * base_performance) ** (1/3)) + 4.0)


def calculate_mechanical_difficulty_rating(aim_val: float, speed_val: float) -> float:
    aim_perf = (OsuRatingCalculator.calculate_difficulty_rating(aim_val) * 1.12) ** 3.0
    speed_perf = (OsuRatingCalculator.calculate_difficulty_rating(speed_val) * 1.12) ** 3.0
    total_perf = (aim_perf ** 1.1 + speed_perf ** 1.1) ** (1.0 / 1.1)
    return calculate_star_rating(total_perf)


def calculate_difficulty(difficulty_config: Difficulty, map_data: Beatmap) -> OsuDifficultyAttributes:
    from .skills import OsuSkills

    mods = difficulty_config._mods
    clock_rate = difficulty_config.get_clock_rate()

    cs_value = map_data.circle_size
    od_value = map_data.overall_difficulty

    scaling = ScalingFactor.new(cs_value)
    osu_objects = convert_objects(map_data, mods.reflection())

    hit_windows = map_data.difficulty.get_hit_windows() if hasattr(map_data, "difficulty") else None
    great_window = (80.0 - 6.0 * od_value) / clock_rate

    skills = OsuSkills.new(mods, scaling, great_window, 1200.0 / clock_rate)
    diff_objects = []

    n_circles = 0
    n_sliders = 0
    n_spinners = 0

    for i, current in enumerate(osu_objects):
        if getattr(current.kind, "is_circle", False): n_circles += 1
        elif getattr(current.kind, "is_slider", False): n_sliders += 1
        elif getattr(current.kind, "is_spinner", False): n_spinners += 1

        last = osu_objects[i-1] if i > 0 else None
        last_diff = diff_objects[i-1] if i > 0 else None

        diff_obj = OsuDifficultyObject.new(current, last, last_diff, clock_rate, i, scaling)

        if last_diff and i >= 2:
            last_last_pos = _get_previous_pos(i, 1, diff_objects)
            if last_last_pos:
                last_last_pos_scaled = last_last_pos * scaling.factor
                last_pos_scaled = last.stacked_pos * scaling.factor
                curr_pos_scaled = current.stacked_pos * scaling.factor
                last_end_pos = last_diff.lazy_end_pos if last_diff.lazy_end_pos else last_pos_scaled

                v1 = last_last_pos_scaled - last_pos_scaled
                v2 = curr_pos_scaled - last_end_pos
                dot = v1.dot(v2)
                det = v1.x * v2.y - v1.y * v2.x
                diff_obj.angle = abs(math.atan2(det, dot))

        diff_objects.appead(diff_obj)
        skills.process(diff_obj, diff_objects)

    aim_rating = OsuRatingCalculator.calculate_difficulty_rating(skills.aim.difficulty_value())
    speed_rating = OsuRatingCalculator.calculate_difficulty_rating(skills.speed.difficulty_value())
    flashlight_rating = OsuRatingCalculator.calculate_difficulty_rating(skills.flashlight.difficulty_value())

    stars = calculate_mechanical_difficulty_rating(skills.aim.difficulty_value(), skills.speed.difficulty_value())

    from ..legacy_score_simulator import OsuLegacyScoreSimulator
    legacy_simulator = OsuLegacyScoreSimulator(osu_objects, map_data, len(osu_objects))
    legacy_attrs = legacy_simulator.simulate()

    legacy_score_base_multiplier = legacy_attrs.bonus_score_ratio
    maximum_legacy_combo_score = float(legacy_attrs.combo_score + legacy_attrs.accuracy_score + legacy_attrs.bonus_score)

    return OsuDifficultyAttributes(
        aim=aim_rating,
        speed=speed_rating,
        flashlight=flashlight_rating,
        stars=stars,
        max_combo=len(osu_objects),
        clock_rate=clock_rate,
        n_circles=n_circles,
        n_sliders=n_sliders,
        n_spinners=n_spinners,
        od=od_value,
        cs=cs_value,
        legacy_score_base_multiplier=legacy_score_base_multiplier,
        maximum_legacy_combo_score=maximum_legacy_combo_score
    )

class OsuGradualDifficulty(Iterator[OsuDifficultyAttributes]):
    __slots__ = ("difficulty", "map_data", "idx", "osu_objects", "skills", "scaling_factor")

    def __init__(self, difficulty: Difficulty, map_data: Beatmap):
        self.difficulty = difficulty
        self.map_data = map_data
        self.idx = 0
        self.scaling = ScalingFactor.new(map_data.circle_size)
        self.osu_objects = convert_objects(map_data, difficulty._mods.reflection())
        self.diff_objects = []
        self.skills = OsuSkills.new(difficulty._mods, self.scaling, 50.0, 600.0)

    def __next__(self) -> OsuDifficultyAttributes:
        if self.idx >= len(self.osu_objects):
            raise StopIteration

        current = self.osu_objects[self.idx]
        last = self.osu_objects[self.idx-1] if self.idx > 0 else current
        last_diff = self.diff_objects[self.idx-1] if self.idx > 0 else None

        diff_obj = OsuDifficultyObject.new(current, last, last_diff, self.difficulty.get_clock_rate(), self.idx, self.scaling)
        self.diff_objects.append(diff_obj)
        self.skills.process(diff_obj, self.diff_objects)

        self.idx += 1
        return calculate_difficulty(self.difficulty, self.map_data)