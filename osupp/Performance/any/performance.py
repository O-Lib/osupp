from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, Optional, Union

from osupp.Beatmap.section.enums import GameMode

from ..model.beatmap.beatmap import Beatmap, TooSuspicious
from ..model.model import ConvertError, IGameMode
from .any import HitResultGenerator, PerformanceAttributes, ScoreState
from .difficulty import Difficulty

if TYPE_CHECKING:
    from ..catch.catch import CatchPerformance
    from ..mania.mania import ManiaPerformance
    from ..osu.osu import OsuPerformance
    from ..taiko.taiko import TaikoPerformance


class InspectablePerformance(IGameMode):
    @classmethod
    def inspect_performance(cls, perf: Any, attrs: Any) -> Any:
        raise NotImplementedError


class HitResultPriority(Enum):
    BEST_CASE = 1
    WORST_CASE = 2

    @classmethod
    def default(cls) -> HitResultPriority:
        return cls.BEST_CASE


class Performance:
    __slots__ = ("_mode", "_perf")
    def __init__(self, map_or_attrs: Any):
        self._mode: GameMode | None = None
        self._perf = None

        if isinstance(map_or_attrs, Beatmap):
            self._mode = map_or_attrs.mode
            if self._mode == GameMode.Osu:
                from ..osu.osu import OsuPerformance
                self._perf = OsuPerformance(map_or_attrs)
            elif self._mode == GameMode.Taiko:
                from ..taiko.taiko import TaikoPerformance
                self._perf = TaikoPerformance(map_or_attrs)
            elif self._mode == GameMode.Catch:
                from ..catch.catch import CatchPerformance
                self._perf = CatchPerformance(map_or_attrs)
            elif self._mode == GameMode.Mania:
                from ..mania.mania import ManiaPerformance
                self._perf = ManiaPerformance(map_or_attrs)

        elif hasattr(map_or_attrs, "mode") and hasattr(map_or_attrs, "raw_attributes"):
            self._mode = map_or_attrs.mode
            if isinstance(map_or_attrs, PerformanceAttributes):
                diff_attrs = map_or_attrs.difficulty_attributes()
                self._init_from_raw(diff_attrs.raw_attributes)
            else:
                self._init_from_raw(map_or_attrs.raw_attributes)
        else:
            self._init_from_raw(map_or_attrs)

    def _init_from_raw(self, raw_attrs: Any):
        class_name = type(raw_attrs).__name__

        if "Osu" in class_name:
            from ..osu.osu import OsuPerformance
            self._mode = GameMode.Osu
            if "Performance" in class_name:
                self._perf = OsuPerformance(raw_attrs.difficulty)
            else:
                self._perf = OsuPerformance(raw_attrs)
        elif "Taiko" in class_name:
            from ..taiko.taiko import TaikoPerformance
            self._mode = GameMode.Taiko
            if "Performance" in class_name:
                self._perf = TaikoPerformance(raw_attrs.difficulty)
            else:
                self._perf = TaikoPerformance(raw_attrs)
        elif "Catch" in class_name:
            from ..catch.catch import CatchPerformance
            self._mode = GameMode.Catch
            if "Performance" in class_name:
                self._perf = CatchPerformance(raw_attrs.difficulty)
            else:
                self._perf = CatchPerformance(raw_attrs)
        elif "Mania" in class_name:
            from ..mania.mania import ManiaPerformance
            self._mode = GameMode.Mania
            if "Performance" in class_name:
                self._perf = ManiaPerformance(raw_attrs.difficulty)
            else:
                self._perf = ManiaPerformance(raw_attrs)

        else:
            raise TypeError(f"Unrecognized attribute type: {class_name}")

    def calculate(self) -> PerformanceAttributes:
        raw_res = self._perf.calculate()
        return PerformanceAttributes(raw_res, self._mode)

    def checked_calculate(self) -> PerformanceAttributes:
        raw_res = self._perf.checked_calculate()
        return PerformanceAttributes(raw_res, self._mode)

    def try_mode(self, mode: GameMode) -> Performance:
        if self._mode == GameMode.Osu:
            try:
                self._perf.try_mode(mode)
                self._mode = mode
                return self
            except ConvertError:
                raise ValueError("Incompatible mode conversion.")
        elif self._mode == mode:
            return self
        raise ValueError("Incompatible mode conversion.")

    def mode_or_ignore(self, mode: GameMode) -> Performance:
        if self._mode == GameMode.Osu:
            self._perf.mode_or_ignore(mode)
            self._mode = mode
        return self

    def mods(self, mods: Any | int) -> Performance:
        self._perf.mods(mods)
        return self

    def difficulty(self, difficulty: Difficulty) -> Performance:
        self._perf.difficulty(difficulty)
        return self

    def passed_objects(self, count: int) -> Performance:
        self._perf.passed_objects(count)
        return self

    def clock_rate(self, rate: float) -> Performance:
        self._perf.clock_rate(rate)
        return self

    def ar(self, val: float, fixed: bool) -> Performance:
        if hasattr(self._perf, "ar"):
            self._perf.ar(val, fixed)
        return self

    def cs(self, val: float, fixed: bool) -> Performance:
        if hasattr(self._perf, "cs"):
            self._perf.cs(val, fixed)
        return self

    def hp(self, val: float, fixed: bool) -> Performance:
        self._perf.hp(val, fixed)
        return self

    def od(self, val: float, fixed: bool) -> Performance:
        self._perf.od(val, fixed)
        return self

    def hardrock_offsets(self, hardrock_offsets: bool) -> Performance:
        if hasattr(self._perf, "hardrock_offsets"):
            self._perf.hardrock_offsets(hardrock_offsets)
        return self

    def state(self, state: ScoreState) -> Performance:
        self._perf.state(state)
        return self

    def accuracy(self, acc: float) -> Performance:
        self._perf.accuracy(acc)
        return self

    def misses(self, count: int) -> Performance:
        self._perf.misses(count)
        return self

    def combo(self, combo: int) -> Performance:
        if hasattr(self._perf, "combo"):
            self._perf.combo(combo)
        return self

    def hitresult_priority(self, priority: HitResultPriority) -> Performance:
        if hasattr(self._perf, "hitresult_priority"):
            self._perf.hitresult_priority(priority)
        return self

    def hitresult_generator(self, gen_class: type[HitResultGenerator]) -> Performance:
        self._perf.hitresult_generator(gen_class)
        return self

    def lazer(self, lazer: bool) -> Performance:
        if hasattr(self._perf, "lazer"):
            self._perf.lazer(lazer)
        return self

    def large_tick_hits(self, count: int) -> Performance:
        if hasattr(self._perf, "large_tick_hits"):
            self._perf.large_tick_hits(count)
        return self

    def small_tick_hits(self, count: int) -> Performance:
        if hasattr(self._perf, "small_tick_hits"):
            self._perf.small_tick_hits(count)
        return self

    def slider_end_hits(self, count: int) -> Performance:
        if hasattr(self._perf, "slider_end_hits"):
            self._perf.slider_end_hits(count)
        return self

    def n300(self, count: int) -> Performance:
        if self._mode == GameMode.Catch:
            self._perf.fruits(count)
        else:
            self._perf.n300(count)
        return self

    def n100(self, count: int) -> Performance:
        if self._mode == GameMode.Catch:
            self._perf.droplets(count)
        else:
            self._perf.n100(count)
        return self

    def n50(self, count: int) -> Performance:
        if self._mode == GameMode.Catch:
            self._perf.tiny_droplets(count)
        elif hasattr(self._perf, "n50"):
            self._perf.n50(count)
        return self

    def n_katu(self, count: int) -> Performance:
        if self._mode == GameMode.Catch:
            self._perf.tiny_droplets_misses(count)
        elif self._mode == GameMode.Mania:
            self._perf.n200(count)
        return self

    def n_geki(self, count: int) -> Performance:
        if self._mode == GameMode.Mania:
            self._perf.n320(count)
        return self

    def legacy_total_score(self, score: int) -> Performance:
        if hasattr(self._perf, "legacy_total_score"):
            self._perf.legacy_total_score(score)
        return self

    def generate_state(self) -> ScoreState:
        raw_state = self._perf.generate_state()
        state = ScoreState()

        return _convert_specific_state_to_any(raw_state, self._mode, state)

    def checked_generate_state(self) -> ScoreState:
        raw_state = self._perf.checked_generate_state()
        state = ScoreState()
        return _convert_specific_state_to_any(raw_state, self._mode, state)

def _convert_specified_state_to_any(raw: Any, mode: GameMode, state: ScoreState) -> ScoreState:
    if mode == GameMode.Osu:
        state.max_combo = raw.max_combo
        state.osu_large_tick_hits = raw.hitresults.large_tick_hits
        state.osu_small_tick_hits = raw.hitresults.small_tick_hits
        state.slider_end_hits = raw.hitresults.slider_end_hits
        state.n300 = raw.hitresults.n300
        state.n100 = raw.hitresults.n100
        state.n50 = raw.hitresults.n50
        state.misses = raw.hitresults.misses
        state.legacy_total_score = raw.legacy_total_score
    elif mode == GameMode.Taiko:
        state.max_combo = raw.max_combo
        state.n300 = raw.hitresults.n300
        state.n100 = raw.hitresults.n100
        state.misses = raw.hitresults.misses
    elif mode == GameMode.Catch:
        state.max_combo = raw.max_combo
        state.n300 = raw.hitresults.fruits
        state.n100 = raw.hitresults.droplets
        state.n50 = raw.hitresults.tiny_droplets
        state.n_katu = raw.hitresults.tiny_droplets_misses
        state.misses = raw.hitresults.misses
    elif mode == GameMode.Mania:
        state.n_geki = raw.n320
        state.n_katu = raw.n200
        state.n300 = raw.n300
        state.n100 = raw.n100
        state.n50 = raw.n50
        state.misses = raw.misses
    return state


class GradualPerformance:
    __slots__ = ("_mode", "_gradual")

    def __init__(self, difficulty: Difficulty, map_obj: Beatmap):
        self._mode = map_obj.mode
        self._gradual = None

        if self._mode == GameMode.Osu:
            from ..osu.osu import Osu
            self._gradual = Osu.gradual_performance(difficulty, map_obj)
        elif self._mode == GameMode.Taiko:
            from ..taiko.taiko import Taiko
            self._gradual = Taiko.gradual_performance(difficulty, map_obj)
        elif self._mode == GameMode.Catch:
            from ..catch.catch import Catch
            self._gradual = Catch.gradual_performance(difficulty, map_obj)
        elif self._mode == GameMode.Mania:
            from ..mania.mania import Mania
            self._gradual = Mania.gradual_performance(difficulty, map_obj)

    @classmethod
    def checked_now(cls, diffifculty: Difficulty, map_obj: Beatmap) -> GradualPerformance:
        err = map_obj.check_suspicion()
        if err:
            raise TooSuspicious(err)
        return cls(diffifculty, map_obj)

    def next(self, state: ScoreState) -> PerformanceAttributes | None:
        return self.nth(state, 0)

    def last(self, state: ScoreState) -> PerformanceAttributes | None:
        return self.nth(state, 2147483647)

    def nth(self, state: ScoreState, n: int) -> PerformanceAttributes | None:
        raw_res = self._gradual.nth(state, n)
        if raw_res is None:
            return None
        return PerformanceAttributes(raw_res, self._mode)

    def len(self) -> int:
        return self._gradual.len()
