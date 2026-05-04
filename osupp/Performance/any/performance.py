from typing import Optional, Union

from osupp.Beatmap.beatmap import Beatmap
from osupp.Beatmap.section.enums import GameMode
from osupp.Mods.game_mods import GameMods

from ..model.beatmap.beatmap import TooSuspiciousError
from .any import (
    CalculateError,
    ConvertError,
    DifficultyAttributes,
    HitResultPriority,
    PerformanceAttributes,
    ScoreState,
)
from .difficulty import Difficulty


class IntoPerformance:
    pass


class Performance:
    def __init__(self, map_or_attrs: Beatmap | DifficultyAttributes | PerformanceAttributes):
        self.map_or_attrs = map_or_attrs
        self._mods = GameMods()
        self._difficulty: Difficulty | None = None
        self._passed_objects: int | None = None
        self._clock_rate: float | None = None
        self._hardrock_offsets: bool | None = None
        self._state: ScoreState | None = None
        self._accuracy: float | None = None
        self._misses: int | None = None
        self._combo: int | None = None
        self._hitresult_priority = HitResultPriority.BEST_CASE
        self._lazer: bool | None = None

        self._large_tick_hits: int | None = None
        self._small_tick_hits: int | None = None
        self._slider_end_hits: int | None = None
        self._n300: int | None = None
        self._n100: int | None = None
        self._n50: int | None = None
        self._n_katu: int | None = None
        self._n_geki: int | None = None
        self._legacy_total_score: int | None = None

        self._ar: float | None = None
        self._ar_fixed: bool = False
        self._cs: float | None = None
        self._cs_fixed: bool = False
        self._hp: float | None = None
        self._hp_fixed: bool = False
        self._od: float | None = None
        self._od_fixed: bool = False

    def mods(self, mods: GameMods) -> "Performance":
        self._mods = mods
        return self

    def difficulty(self, diff: Difficulty) -> "Performance":
        self._difficulty = diff
        return self

    def passed_objects(self, passed_objects: int) -> 'Performance':
        self._passed_objects = passed_objects
        return self

    def clock_rate(self, clock_rate: float) -> 'Performance':
        self._clock_rate = clock_rate
        return self

    def ar(self, ar: float, fixed: bool) -> 'Performance':
        self._ar = ar
        self._ar_fixed = fixed
        return self

    def cs(self, cs: float, fixed: bool) -> 'Performance':
        self._cs = cs
        self._cs_fixed = fixed
        return self

    def hp(self, hp: float, fixed: bool) -> 'Performance':
        self._hp = hp
        self._hp_fixed = fixed
        return self

    def od(self, od: float, fixed: bool) -> 'Performance':
        self._od = od
        self._od_fixed = fixed
        return self

    def hardrock_offsets(self, hardrock_offsets: bool) -> 'Performance':
        self._hardrock_offsets = hardrock_offsets
        return self

    def state(self, state: ScoreState) -> 'Performance':
        self._state = state
        return self

    def accuracy(self, acc: float) -> 'Performance':
        self._accuracy = acc
        return self

    def misses(self, n_misses: int) -> 'Performance':
        self._misses = n_misses
        return self

    def combo(self, combo: int) -> 'Performance':
        self._combo = combo
        return self

    def hitresult_priority(self, priority: HitResultPriority) -> 'Performance':
        self._hitresult_priority = priority
        return self

    def lazer(self, is_lazer: bool) -> 'Performance':
        self._lazer = is_lazer
        return self

    def large_tick_hits(self, large_tick_hits: int) -> 'Performance':
        self._large_tick_hits = large_tick_hits
        return self

    def small_tick_hits(self, small_tick_hits: int) -> 'Performance':
        self._small_tick_hits = small_tick_hits
        return self

    def slider_end_hits(self, slider_end_hits: int) -> 'Performance':
        self._slider_end_hits = slider_end_hits
        return self

    def n300(self, n300: int) -> 'Performance':
        self._n300 = n300
        return self

    def n100(self, n100: int) -> 'Performance':
        self._n100 = n100
        return self

    def n50(self, n50: int) -> 'Performance':
        self._n50 = n50
        return self

    def n_katu(self, n_katu: int) -> 'Performance':
        self._n_katu = n_katu
        return self

    def n_geki(self, n_geki: int) -> 'Performance':
        self._n_geki = n_geki
        return self

    def legacy_total_score(self, legacy_total_score: int) -> 'Performance':
        self._legacy_total_score = legacy_total_score
        return self

    def _get_mode(self) -> "GameMode":
        if hasattr(self.map_or_attrs, "mode"):
            return self.map_or_attrs.mode

        type_name = type(self.map_or_attrs).__name__
        if "Osu" in type_name:
            return GameMode.Osu
        elif "Taiko" in type_name:
            return GameMode.Taiko
        elif "Catch" in type_name:
            return GameMode.Catch
        elif "Mania" in type_name:
            return GameMode.Mania

        return GameMode.Osu

    def calculate(self) -> "PerformanceAttributes":
        mode = self._get_mode()

        if mode == GameMode.Osu:
            raise NotImplementedError("Osu Performance Calculator to be implemented.")
        elif mode == GameMode.Taiko:
            raise NotImplementedError("Taiko Performance Calculator to be implemented.")
        elif mode == GameMode.Catch:
            raise NotImplementedError("Catch Performance Calculator to be implemented.")
        elif mode == GameMode.Mania:
            raise NotImplementedError("Mania Performance Calculator to be implemented.")

        return PerformanceAttributes()

    def checked_calculate(self) -> "PerformanceAttributes":
        if hasattr(self.map_or_attrs, "check_suspicion"):
            try:
                self.map_or_attrs.check_suspicion()
            except TooSuspiciousError as e:
                raise CalculateError(e)
        return self.calculate()

    def generate_state(self) -> ScoreState:
        mode = self._get_mode()

        if mode == GameMode.Osu:
            raise NotImplementedError("Osu State Generator to be implemented.")
        elif mode == GameMode.Taiko:
            raise NotImplementedError("Taiko State Generator to be implemented.")
        elif mode == GameMode.Catch:
            raise NotImplementedError("Catch State Generator to be implemented.")
        elif mode == GameMode.Mania:
            raise NotImplementedError("Mania State Generator to be implemented.")

        return ScoreState()


class GradualPerformance:
    def __init__(self, difficulty: Difficulty, map_data: Beatmap):
        self._mode = map_data.mode

        if self._mode == GameMode.Osu:
            pass
        elif self._mode == GameMode.Taiko:
            pass
        elif self._mode == GameMode.Catch:
            pass
        elif self._mode == GameMode.Mania:
            pass
        else:
            raise ConvertError(self._mode, GameMode.Osu)

    @classmethod
    def checked_new(cls, difficulty: Difficulty, map_data: Beatmap) -> "GradualPerformance":
        if hasattr(map_data, "checked_suspicion"):
            map_data.checked_suspicion()
        return cls(difficulty, map_data)

    def next(self, state: ScoreState) -> PerformanceAttributes | None:
        return self.nth(state, 0)

    def last(self, state: ScoreState) -> PerformanceAttributes | None:
        return self.nth(state, int(1e9))

    def nth(self, state: ScoreState, n: int) -> PerformanceAttributes | None:
        if self._mode == GameMode.Osu:
            raise NotImplementedError()
        elif self._mode == GameMode.Taiko:
            raise NotImplementedError()
        elif self._mode == GameMode.Catch:
            raise NotImplementedError()
        elif self._mode == GameMode.Mania:
            raise NotImplementedError()
        return None

    def __len__(self) -> int:
        if self._mode == GameMode.Osu:
            return 0
        return 0
