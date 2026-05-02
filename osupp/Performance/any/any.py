from __future__ import annotations
from enum import Enum
from typing import Optional, Any

from osupp.Beatmap.section.enums import GameMode


class CalculateError(Exception):
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error


class HitResult(Enum):
    NONE = 0
    MISS = 1
    MEH = 2
    OK = 3
    GOOD = 4
    GREAT = 5
    PERFECT = 6
    SMALL_TICK_MISS = 7
    SMALL_TICK_HIT = 8
    LARGE_TICK_MISS = 9
    LARGE_TICK_HIT = 10
    SMALL_BONUS = 11
    LARGE_BONUS = 12
    IGNORE_MISS = 13
    IGNORE_HIT = 14
    COMBO_BREAK = 15
    SLIDER_TAIL_HIT = 16
    LEGACY_COMBO_INCREASE = 17

    def base_score(self, mode: GameMode) -> int:
        if mode == GameMode.Osu:
            if self == HitResult.SMALL_TICK_HIT:
                return 10
            if self == HitResult.LARGE_TICK_HIT:
                return 30
            if self == HitResult.SLIDER_TAIL_HIT:
                return 150
            if self == HitResult.MEH:
                return 50
            if self == HitResult.OK:
                return 100
            if self == HitResult.GOOD:
                return 200
            if self in (HitResult.GREAT, HitResult.PERFECT):
                return 300
            if self == HitResult.SMALL_BONUS:
                return 10
            if self == HitResult.LARGE_BONUS:
                return 50
            return 0
        elif mode == GameMode.Taiko:
            raise NotImplementedError("Base score for taiko not implemented")
        elif mode == GameMode.Catch:
            raise NotImplementedError("Base score for catch not implemented")
        elif mode == GameMode.Mania:
            raise NotImplementedError("Base score for mania not implemented")
        return 0


class HitResultGenerator:
    pass

class Fast(HitResultGenerator):
    pass

class Closest(HitResultGenerator):
    pass

class Statistical(HitResultGenerator):
    pass

class IgnoreAccuracy(HitResultGenerator):
    pass


class ScoreState:
    __slots__ = (
        "max_combo", "osu_large_tick_hits", "osu_small_tick_hits", "slider_end_hits", "n_geki", "n_katu", "n300", "n100", "n50",
        "misses", "legacy_total_score"
    )

    def __init__(self):
        self.max_combo: int = 0
        self.osu_large_tick_hits: int = 0
        self.osu_small_tick_hits: int = 0
        self.slider_end_hits: int = 0
        self.n_geki: int = 0
        self.n_katu: int = 0
        self.n300: int = 0
        self.n100: int = 0
        self.n50: int = 0
        self.misses: int = 0
        self.legacy_total_score: Optional[int] = None

    def total_hits(self, mode: GameMode) -> int:
        amount = self.n300 + self.n100 + self.misses

        if mode != GameMode.Taiko:
            amount += self.n50

            if mode != GameMode.Osu:
                amount += self.n_katu
                if mode != GameMode.Catch:
                    amount += self.n_geki

        return amount


class Strains:
    __slots__ = ("raw_strains", "mode")

    def __init__(self, raw_strains: Any, mode: GameMode):
        self.raw_strains = raw_strains
        self.mode = mode

    def section_len(self) -> float:
        return self.raw_strains.SECTION_LEN


class DifficultyAttributes:
    __slots__ = ("raw_attributes", "mode")

    def __init__(self, raw_attributes: Any, mode: GameMode):
        self.raw_attributes = raw_attributes
        self.mode = mode

    @property
    def stars(self) -> float:
        return self.raw_attributes.stars

    @property
    def max_combo(self) -> int:
        if self.mode == GameMode.Catch:
            return self.raw_attributes.max_combo()
        return self.raw_attributes.max_combo

    def performance(self) -> "Performance":
        from .performance import Performance
        return Performance(self)


class PerformanceAttributes:
    __slots__ = ("raw_attributes", "mode")

    def __init__(self, raw_attributes: Any, mode: GameMode):
        self.raw_attributes = raw_attributes
        self.mode = mode

    @property
    def pp(self) -> float:
        return self.raw_attributes.pp

    @property
    def stars(self) -> float:
        return self.raw_attributes.stars()

    def difficulty_attributes(self) -> "DifficultyAttributes":
        return DifficultyAttributes(self.raw_attributes.difficulty, self.mode)

    @property
    def max_combo(self) -> int:
        if self.mode == GameMode.Catch:
            return self.raw_attributes.difficulty.max_combo()
        return self.raw_attributes.difficulty.max_combo

    def performance(self) -> "Performance":
        from .performance import Performance
        return Performance(self)