from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, List, Optional, Union
from collections.abc import Iterator

from osupp.Beatmap.section.enums import GameMode

from ..model.beatmap.attributes import (
    AttributeType,
    BeatmapAttribute,
    BeatmapDifficulty,
)
from ..model.beatmap.beatmap import Beatmap, TooSuspicious
from ..model.model import ConvertError, GameMods, IGameMode
from .any import CalculateError, DifficultyAttributes, Strains

if TYPE_CHECKING:
    from .performance import GradualPerformance


class InspectDifficulty:
    __slots__ = ("mods", "passed_objects", "clock_rate", "ar", "cs", "hp", "od", "hardrock_offsets", "lazer")

    def __init__(
            self,
            mods: GameMods,
            passed_objects: int | None,
            clock_rate: float | None,
            ar: BeatmapAttribute,
            cs: BeatmapAttribute,
            hp: BeatmapAttribute,
            od: BeatmapAttribute,
            hardrock_offsets: bool | None,
            lazer: bool | None
    ):
        self.mods = mods
        self.passed_objects = passed_objects
        self.clock_rate = clock_rate
        self.ar = ar
        self.cs = cs
        self.hp = hp
        self.od = od
        self.hardrock_offsets = hardrock_offsets
        self.lazer = lazer

    def into_difficulty(self) -> Difficulty:
        diff = Difficulty().mods(self.mods)

        if self.passed_objects is not None:
            diff = diff.passed_objects(self.passed_objects)
        if self.clock_rate is not None:
            diff = diff.clock_rate(self.clock_rate)

        def set_attr(attr_name: str, attr_val: BeatmapAttribute):
            if attr_val.type == AttributeType.GIVEN:
                getattr(diff, attr_name)(attr_val.value, False)
            elif attr_val.type == AttributeType.FIXED:
                getattr(diff, attr_name)(attr_val.value, True)

        set_attr("ar", self.ar)
        set_attr("cs", self.cs)
        set_attr("hp", self.hp)
        set_attr("od", self.od)

        if self.hardrock_offsets is not None:
            diff = diff.hardrock_offsets(self.hardrock_offsets)
        if self.lazer is not None:
            diff = diff.lazer(self.lazer)

        return diff


class Difficulty:
    def __init__(self):
        self._mods: GameMods = GameMods.default()
        self._passed_objects: int | None = None
        self._clock_rate: float | None = None
        self._map_difficulty: BeatmapDifficulty = BeatmapDifficulty.default()
        self._hardrock_offsets: bool | None = None
        self._lazer: bool | None = None

    def inspect(self) -> InspectDifficulty:
        return InspectDifficulty(
            mods=self._mods,
            passed_objects=self._passed_objects,
            clock_rate=self._clock_rate,
            ar=self._map_difficulty.ar,
            cs=self._map_difficulty.cs,
            hp=self._map_difficulty.hp,
            od=self._map_difficulty.od,
            hardrock_offsets=self._hardrock_offsets,
            lazer=self._lazer
        )

    def mods(self, mods: Any | int) -> Difficulty:
        self._mods = GameMods(mods)
        return self

    def passed_objects(self, count: int) -> Difficulty:
        self._passed_objects = count
        return self

    def clock_rate(self, rate: float) -> Difficulty:
        self._clock_rate = max(0.01, min(rate, 100.0))
        return self

    def ar(self, val: float, fixed: bool) -> Difficulty:
        val = max(-20.0, min(val, 20.0))
        self._map_difficulty.ar = BeatmapAttribute.fixed_type(val) if fixed else BeatmapAttribute.given_type(val)
        return self

    def cs(self, val: float, fixed: bool) -> Difficulty:
        val = max(-20.0, min(val, 20.0))
        self._map_difficulty.cs = BeatmapAttribute.fixed_type(val) if fixed else BeatmapAttribute.given_type(val)
        return self

    def hp(self, val: float, fixed: bool) -> Difficulty:
        val = max(-20.0, min(val, 20.0))
        self._map_difficulty.hp = BeatmapAttribute.fixed_type(val) if fixed else BeatmapAttribute.given_type(val)
        return self

    def od(self, val: float, fixed: bool) -> Difficulty:
        val = max(-20.0, min(val, 20.0))
        self._map_difficulty.od = BeatmapAttribute.fixed_type(val) if fixed else BeatmapAttribute.given_type(val)
        return self

    def hardrock_offsets(self, hardrock_offsets: bool) -> Difficulty:
        self._hardrock_offsets = hardrock_offsets
        return self

    def lazer(self, lazer: bool) -> Difficulty:
        self._lazer = lazer
        return self

    def calculate(self, map_obj: Beatmap) -> DifficultyAttributes:
        if map_obj.mode == GameMode.Osu:
            from ..osu.osu import Osu
            return DifficultyAttributes(Osu.difficulty(self, map_obj), GameMode.Osu)
        elif map_obj.mode == GameMode.Taiko:
            from ..taiko.taiko import Taiko
            return DifficultyAttributes(Taiko.difficulty(self, map_obj), GameMode.Taiko)
        elif map_obj.mode == GameMode.Catch:
            from ..catch.catch import Catch
            return DifficultyAttributes(Catch.difficulty(self, map_obj), GameMode.Catch)
        elif map_obj.mode == GameMode.Mania:
            from ..mania.mania import Mania
            return DifficultyAttributes(Mania.difficulty(self, map_obj), GameMode.Mania)
        raise ConvertError(f"Unsupported game mode: {map_obj.mode}")

    def checked_calculate(self, map_obj: Beatmap) -> DifficultyAttributes:
        err = map_obj.check_suspicion()
        if err:
            raise TooSuspicious(err)
        return self.calculate(map_obj)

    def calculate_for_mode(self, map_obj: Beatmap, mode_class: IGameMode) -> Any:
        return mode_class.difficulty(self, map_obj)

    def checked_calculate_for_mode(self, map_obj: Beatmap, mode_class: IGameMode) -> Any:
        err = map_obj.check_suspicion()
        if err:
            raise CalculateError(err)
        return mode_class.checked_difficulty(self, map_obj)

    def strains(self, map_obj: Beatmap) -> Strains:
        if map_obj.mode == GameMode.Osu:
            from ..osu.osu import Osu
            return Strains(Osu.strains(self, map_obj), GameMode.Osu)
        elif map_obj.mode == GameMode.Taiko:
            from ..taiko.taiko import Taiko
            return Strains(Taiko.strains(self, map_obj), GameMode.Taiko)
        elif map_obj.mode == GameMode.Catch:
            from ..catch.catch import Catch
            return Strains(Catch.strains(self, map_obj), GameMode.Catch)
        elif map_obj.mode == GameMode.Mania:
            from ..mania.mania import Mania
            return Strains(Mania.strains(self, map_obj), GameMode.Mania)
        raise ConvertError(f"Unsupported game mode: {map_obj.mode}")

    def checked_strains(self, map_obj: Beatmap) -> Strains:
        err = map_obj.check_suspicion()
        if err:
            raise TooSuspicious(err)
        return self.strains(map_obj)

    def strains_for_mode(self, map_obj: Beatmap, mode_class: IGameMode) -> Any:
        return mode_class.strains(self, map_obj)

    def gradual_difficulty(self, map_obj: Beatmap) -> GradualDifficulty:
        return GradualDifficulty(self, map_obj)

    def checked_gradual_difficulty(self, map_obj: Beatmap) -> GradualDifficulty:
        err = map_obj.check_suspicion()
        if err:
            raise TooSuspicious(err)
        return self.gradual_difficulty(map_obj)

    def gradual_difficulty_for_mode(self, map_obj: Beatmap, mode_class: IGameMode) -> Any:
        return mode_class.gradual_difficulty(self, map_obj)

    def gradual_performance(self, map_obj: Beatmap) -> GradualPerformance:
        from .performance import GradualPerformance
        return GradualPerformance(self, map_obj)

    def checked_gradual_performance(self, map_obj: Beatmap) -> GradualPerformance:
        err = map_obj.check_suspicion()
        if err:
            raise TooSuspicious(err)
        return self.gradual_performance(map_obj)

    def gradual_performance_for_mode(self, map_obj: Beatmap, mode_class: IGameMode) -> Any:
        return mode_class.gradual_performance(self, map_obj)

    def get_mods(self) -> GameMods:
        return self._mods

    def get_clock_rate(self) -> float:
        if self._clock_rate is not None:
            return self._clock_rate
        return self._mods.clock_rate()

    def get_passed_objects(self) -> int:
        if self._passed_objects is not None:
            return self._passed_objects
        return 2147483647

    def get_map_difficulty(self) -> BeatmapDifficulty:
        return self._map_difficulty

    def get_hardrock_offsets(self) -> bool:
        if self._hardrock_offsets is not None:
            return self._hardrock_offsets
        return self._mods.hardrock_offsets()

    def get_lazer(self) -> bool:
        if self._lazer is not None:
            return self._lazer
        return True


class GradualDifficulty:
    def __init__(self, difficulty: Difficulty, map_obj: Beatmap):
        self.mode = map_obj.mode
        self._gradual = None

        if self.mode == GameMode.Osu:
            from ..osu.osu import Osu
            self._gradual = Osu.gradual_difficulty(difficulty, map_obj)
        elif self.mode == GameMode.Taiko:
            from ..taiko.taiko import Taiko
            self._gradual = Taiko.gradual_difficulty(difficulty, map_obj)
        elif self.mode == GameMode.Catch:
            from ..catch.catch import Catch
            self._gradual = Catch.gradual_difficulty(difficulty, map_obj)
        elif self.mode == GameMode.Mania:
            from ..mania.mania import Mania
            self._gradual = Mania.gradual_difficulty(difficulty, map_obj)

    @classmethod
    def checked_new(cls, difficulty: Difficulty, map_obj: Beatmap) -> GradualDifficulty:
        err = map_obj.check_suspicion()
        if err:
            raise TooSuspicious(err)
        return cls(difficulty, map_obj)

    def __iter__(self) -> Iterator[DifficultyAttributes]:
        return self

    def __next__(self) -> DifficultyAttributes:
        nxt = next(self._gradual, None)
        if nxt is None:
            raise StopIteration
        return DifficultyAttributes(nxt, self.mode)


class IDifficultyObject:
    def idx(self) -> int:
        raise NotImplementedError

    def previous(self, backwards_idx: int, diff_objects: list[Any]) -> Any | None:
        target_idx = self.idx() - (backwards_idx + 1)
        if target_idx >= 0 and target_idx < len(diff_objects):
            return diff_objects[target_idx]
        return None

    def next(self, forwards_idx: int, diff_objects: list[Any]) -> Any | None:
        target_idx = self.idx() + (forwards_idx + 1)
        if target_idx >= 0 and target_idx < len(diff_objects):
            return diff_objects[target_idx]
        return None


def count_top_weighted_strains(object_strains: list[float], difficulty_value: float) -> float:
    if not object_strains:
        return 0.0

    consistent_top_strain = difficulty_value / 10.0

    if consistent_top_strain == 0.0:
        return float(len(object_strains))

    sum_val = 0.0
    for s in object_strains:
        sum_val += 1.1 / (1.0 + math.exp(-10.0 * (s / consistent_top_strain - 0.88)))

    return sum_val

def difficulty_value(current_strain_perks: list[float], decay_weight: float) -> float:
    difficulty = 0.0
    weight = 1.0

    peaks = [p for p in current_strain_perks if p > 0.0]
    peaks.sort(reverse=True)

    for strain in peaks:
        difficulty += strain * weight
        weight *= decay_weight

    return difficulty

def strain_decay(ms: float, strain_decay_base: float) -> float:
    return math.pow(strain_decay_base, ms / 1000.0)
