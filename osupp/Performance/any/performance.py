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
        if hasattr(self._inner, "mods"):
            self._inner = self._inner.mods(mods)
        return self

    def difficulty(self, diff: Difficulty) -> "Performance":
        if hasattr(self._inner, "difficulty"):
            self._inner = self._inner.difficulty(diff)
        return self

    def passed_objects(self, passed_objects: int) -> "Performance":
        if hasattr(self._inner, "passed_objects"):
            self._inner = self._inner.passed_objects(passed_objects)
        return self

    def clock_rate(self, clock_rate: float) -> "Performance":
        if hasattr(self._inner, "clock_rate"):
            self._inner = self._inner.clock_rate(clock_rate)
        return self

    def ar(self, ar: float, fixed: bool) -> "Performance":
        if hasattr(self._inner, "ar"):
            self._inner = self._inner.ar(ar, fixed)
        return self

    def cs(self, cs: float, fixed: bool) -> "Performance":
        if hasattr(self._inner, "cs"):
            self._inner = self._inner.cs(cs, fixed)
        return self

    def hp(self, hp: float, fixed: bool) -> "Performance":
        if hasattr(self._inner, "hp"):
            self._inner = self._inner.hp(hp, fixed)
        return self

    def od(self, od: float, fixed: bool) -> "Performance":
        if hasattr(self._inner, "od"):
            self._inner = self._inner.od(od, fixed)
        return self

    def hardrock_offsets(self, hardrock_offsets: bool) -> "Performance":
        if hasattr(self._inner, "hardrock_offsets"):
            self._inner = self._inner.hardrock_offsets(hardrock_offsets)
        return self

    def state(self, state: ScoreState) -> "Performance":
        if hasattr(self._inner, "state"):
            self._inner = self._inner.state(state)
        return self

    def accuracy(self, acc: float) -> "Performance":
        if hasattr(self._inner, "accuracy"):
            self._inner = self._inner.accuracy(acc)
        return self

    def misses(self, n_misses: int) -> "Performance":
        if hasattr(self._inner, "misses"):
            self._inner = self._inner.misses(n_misses)
        return self

    def combo(self, combo: int) -> "Performance":
        if hasattr(self._inner, "combo"):
            self._inner = self._inner.combo(combo)
        return self

    def hitresult_priority(self, priority: HitResultPriority) -> "Performance":
        if hasattr(self._inner, "hitresult_priority"):
            self._inner = self._inner.hitresult_priority(priority)
        return self

    def hitresult_generator(self, generator: Callable) -> "Performance":
        if hasattr(self._inner, "hitresult_generator"):
            self._inner = self._inner.hitresult_generator(generator)
        return self

    def lazer(self, is_lazer: bool) -> "Performance":
        if hasattr(self._inner, "lazer"):
            self._inner = self._inner.lazer(is_lazer)
        return self

    def large_tick_hits(self, large_tick_hits: int) -> "Performance":
        if hasattr(self._inner, "large_tick_hits"):
            self._inner = self._inner.large_tick_hits(large_tick_hits)
        return self

    def small_tick_hits(self, small_tick_hits: int) -> "Performance":
        if hasattr(self._inner, "small_tick_hits"):
            self._inner = self._inner.small_tick_hits(small_tick_hits)
        return self

    def slider_end_hits(self, slider_end_hits: int) -> "Performance":
        if hasattr(self._inner, "slider_end_hits"):
            self._inner = self._inner.slider_end_hits(slider_end_hits)
        return self

    def n300(self, n300: int) -> "Performance":
        if hasattr(self._inner, "n300"):
            self._inner = self._inner.n300(n300)
        return self

    def n100(self, n100: int) -> "Performance":
        if hasattr(self._inner, "n100"):
            self._inner = self._inner.n100(n100)
        return self

    def n50(self, n50: int) -> "Performance":
        if hasattr(self._inner, "n50"):
            self._inner = self._inner.n50(n50)
        return self

    def n_katu(self, n_katu: int) -> "Performance":
        if hasattr(self._inner, "n_katu"):
            self._inner = self._inner.n_katu(n_katu)
        return self

    def n_geki(self, n_geki: int) -> "Performance":
        if hasattr(self._inner, "n_geki"):
            self._inner = self._inner.n_geki(n_geki)
        return self

    def legacy_total_score(self, legacy_total_score: int) -> "Performance":
        if hasattr(self._inner, "legacy_total_score"):
            self._inner = self._inner.legacy_total_score(legacy_total_score)
        return self

    def calculate(self) -> PerformanceAttributes:
        if self._inner is not None and hasattr(self._inner, "calculate"):
            return self._inner.calculate()
        return PerformanceAttributes()

    def checked_calculate(self) -> PerformanceAttributes:
        if self._inner is not None and hasattr(self._inner, "map_or_attrs"):
            map_or_attrs = self._inner.map_or_attrs
            if hasattr(map_or_attrs, "check_suspicion"):
                try:
                    map_or_attrs.check_suspicion()
                except TooSuspiciousError as e:
                    raise CalculateError(e)

        if self._inner is not None and hasattr(self._inner, "calculate"):
            return self._inner.calculate()
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
