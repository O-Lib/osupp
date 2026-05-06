import math
from typing import TYPE_CHECKING
from collections.abc import Callable

from osupp.Beatmap.beatmap import Beatmap
from osupp.Beatmap.section.enums import GameMode
from osupp.Mods.game_mods import GameMods

from ..model.beatmap.beatmap import TooSuspiciousError
from .any import CalculateError, HitResultPriority, PerformanceAttributes, ScoreState
from .difficulty import Difficulty


def _get_mode(obj) -> GameMode:
    if hasattr(obj, "mode"):
        return obj.mode

    type_name = type(obj).__name__
    match type_name:
        case name if "Osu" in name:
            return GameMode.Osu
        case name if "Taiko" in name:
            return GameMode.Taiko
        case name if "Catch" in name:
            return GameMode.Catch
        case name if "Taiko" in name:
            return GameMode.Mania
        case _:
            return GameMode.Osu


class Performance:
    __slots__ = ("_inner")

    def __init__(self, map_or_attrs):
        mode = _get_mode(map_or_attrs)

        match mode:
            case GameMode.Osu:
                from ..osu.performance.performance import OsuPerformance
                self._inner = OsuPerformance(map_or_attrs)
            case GameMode.Taiko:
                self._inner = None
            case GameMode.Catch:
                self._inner = None
            case GameMode.Mania:
                self._inner = None
            case _:
                self._inner = None

    def _apply_single(self, attr_name: str, value) -> "Performance":
        if self._inner is not None:
            if hasattr(self._inner, attr_name):
                attr = getattr(self._inner, attr_name)
                if callable(attr):
                    res = attr(value)
                    if res is not None:
                        self._inner = res
                else:
                    setattr(self._inner, attr_name, value)
        return self

    def _apply_double(self, attr_name: str, val1, val2) -> "Performance":
        if self._inner is not None:
            if hasattr(self._inner, attr_name):
                attr = getattr(self._inner, attr_name)
                if callable(attr):
                    res = attr(val1, val2)
                    if res is not None:
                        self._inner = res
                else:
                    setattr(self._inner, attr_name, val1)
        return self

    def mods(self, mods: GameMods) -> "Performance":
        return self._apply_single("mods", mods)

    def difficulty(self, diff: Difficulty) -> "Performance":
        return self._apply_single("difficulty", diff)

    def passed_objects(self, passed_objects: int) -> "Performance":
        return self._apply_single("passed_objects", passed_objects)

    def clock_rate(self, clock_rate: float) -> "Performance":
        if math.isnan(clock_rate) or math.isinf(clock_rate):
            raise ValueError("Clock rate cannot be NaN or Infinity")

        return self._apply_single("clock_rate", clock_rate)

    def ar(self, ar: float, fixed: bool) -> "Performance":
        return self._apply_double("ar", ar, fixed)

    def cs(self, cs: float, fixed: bool) -> "Performance":
        return self._apply_double("cs", cs, fixed)

    def hp(self, hp: float, fixed: bool) -> "Performance":
        return self._apply_double("hp", hp, fixed)

    def od(self, od: float, fixed: bool) -> "Performance":
        return self._apply_double("od", od, fixed)

    def hardrock_offsets(self, hardrock_offsets: bool) -> "Performance":
        return self._apply_single("hardrock_offsets", hardrock_offsets)

    def state(self, state: ScoreState) -> "Performance":
        return self._apply_single("state", state)

    def accuracy(self, acc: float) -> "Performance":
        if math.isnan(acc) or math.isinf(acc):
            raise ValueError("Accuracy cannot be NaN or Infinity")

        return self._apply_single("accuracy", acc)

    def misses(self, n_misses: int) -> "Performance":
        return self._apply_single("misses", n_misses)

    def combo(self, combo: int) -> "Performance":
        return self._apply_single("combo", combo)

    def hitresult_priority(self, priority: HitResultPriority) -> "Performance":
        return self._apply_single("hitresult_priority", priority)

    def hitresult_generator(self, generator: Callable) -> "Performance":
        return self._apply_single("hitresult_generator", generator)

    def lazer(self, is_lazer: bool) -> "Performance":
        return self._apply_single("lazer", is_lazer)

    def large_tick_hits(self, large_tick_hits: int) -> "Performance":
        return self._apply_single("large_tick_hits", large_tick_hits)

    def small_tick_hits(self, small_tick_hits: int) -> "Performance":
        return self._apply_single("small_tick_hits", small_tick_hits)

    def slider_end_hits(self, slider_end_hits: int) -> "Performance":
        return self._apply_single("slider_end_hits", slider_end_hits)

    def n300(self, n300: int) -> "Performance":
        return self._apply_single("n300", n300)

    def n100(self, n100: int) -> "Performance":
        return self._apply_single("n100", n100)

    def n50(self, n50: int) -> "Performance":
        return self._apply_single("n50", n50)

    def n_katu(self, n_katu: int) -> "Performance":
        return self._apply_single("n_katu", n_katu)

    def n_geki(self, n_geki: int) -> "Performance":
        return self._apply_single("n_geki", n_geki)

    def legacy_total_score(self, legacy_total_score: int) -> "Performance":
        return self._apply_single("legacy_total_score", legacy_total_score)

    def calculate(self) -> PerformanceAttributes:
        if self._inner is None:
            raise NotImplementedError("Performance calculation for this mode is not implemnted yet")
        if hasattr(self._inner, "calculate"):
            try:
                return self._inner.calculate()
            except TypeError as e:
                if "'attrs'" in str(e):
                    from .any import DifficultyAttributes
                    map_or_attrs = getattr(self._inner, "map_or_attrs", None)
                    if isinstance(map_or_attrs, DifficultyAttributes):
                        attrs = map_or_attrs
                    elif hasattr(map_or_attrs, "mode"):
                        attrs = Difficulty().calculate(map_or_attrs)
                    else:
                        attrs = DifficultyAttributes()
                    return self._inner.calculate(attrs)
                raise e
        return PerformanceAttributes()

    def checked_calculate(self) -> PerformanceAttributes:
        if self._inner is None:
            raise NotImplementedError("Performance calculation for this mode is not implemnted yet")

        if hasattr(self._inner, "map_or_attrs"):
            map_or_attrs = self._inner.map_or_attrs
            if hasattr(map_or_attrs, "check_suspicion"):
                try:
                    map_or_attrs.check_suspicion()
                except TooSuspiciousError as e:
                    raise CalculateError(e)

        if hasattr(self._inner, "calculate"):
            try:
                return self._inner.calculate()
            except TypeError as e:
                if "'attrs'" in str(e):
                    from .any import DifficultyAttributes
                    map_or_attrs = getattr(self._inner, "map_or_attrs", None)
                    if isinstance(map_or_attrs, DifficultyAttributes):
                        attrs = map_or_attrs
                    elif hasattr(map_or_attrs, "mode"):
                        attrs = Difficulty().calculate(map_or_attrs)
                    else:
                        attrs = DifficultyAttributes()
                    return self._inner.calculate(attrs)
                raise e
        return PerformanceAttributes()

    def generate_state(self) -> ScoreState:
        if self._inner is not None and hasattr(self._inner, "generate_state"):
            return self._inner.generate_state()
        return PerformanceAttributes()

    def checked_generate_state(self) -> ScoreState:
        if self._inner is not None and hasattr(self._inner, "map_or_attrs"):
            map_or_attrs = self._inner.map_or_attrs
            if hasattr(map_or_attrs, "check_suspicion"):
                try:
                    map_or_attrs.check_suspicion()
                except TooSuspiciousError as e:
                    raise CalculateError(e)

        if self._inner is not None and hasattr(self._inner, "generate_state"):
            return self._inner.generate_state()
        return PerformanceAttributes()


class GradualPerformance:
    __slots__ = ("_inner")

    def __init__(self, difficulty: Difficulty, map_data: Beatmap):
        match map_data.mode:
            case GameMode.Osu:
                from ..osu.performance.performance import OsuGradualPerformance
                self._inner = OsuGradualPerformance(difficulty, map_data)
            case GameMode.Taiko:
                self._inner = None
            case GameMode.Catch:
                self._inner = None
            case GameMode.Mania:
                self._inner = None
            case _:
                self._inner = None

    @classmethod
    def checked_new(cls, difficulty: Difficulty, map_data: Beatmap) -> "GradualPerformance":
        if hasattr(map_data, "check_suspicion"):
            map_data.check_suspicion()
        return cls(difficulty, map_data)

    def next(self, state: ScoreState) -> PerformanceAttributes | None:
        return self.nth(state, 0)

    def last(self, state: ScoreState) -> PerformanceAttributes | None:
        return self.nth(state, int(1e9))

    def nth(self, state: ScoreState, n: int) -> PerformanceAttributes | None:
        if self._inner is not None and hasattr(self._inner, "nth"):
            return self._inner.nth(state, n)
        return None

    def __len__(self) -> int:
        if self._inner is not None and hasattr(self._inner, "len"):
            return self._inner.len()
        return 0
