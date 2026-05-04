from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any, Protocol

from osupp.Beatmap.section.enums import GameMode
from ..model.beatmap.beatmap import TooSuspiciousError
from ..model.model import ConvertError


class CalculateError(Exception):
    def __init__(self, original_error: Exception):
        if isinstance(original_error, ConvertError):
            super().__init__(f"Error calculating attributes (Convert): {original_error}")
        elif isinstance(original_error, TooSuspiciousError):
            super().__init__(f"Error calculating attributes (Suspicion): {original_error}")
        else:
            super().__init__(f"Error calculating attributes: {original_error}")
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
            elif self == HitResult.LARGE_TICK_HIT:
                return 30
            elif self == HitResult.SLIDER_TAIL_HIT:
                return 150
            elif self == HitResult.MEH:
                return 50
            elif self == HitResult.OK:
                return 100
            elif self == HitResult.GOOD:
                return 200
            elif self in (HitResult.GREAT, HitResult.PERFECT):
                return 300
            elif self == HitResult.SMALL_BONUS:
                return 10
            elif self == HitResult.LARGE_BONUS:
                return 50
            return 0
        elif mode == GameMode.Taiko:
            raise NotImplementedError("Base score for Taiko has not yet been implemented.")
        elif mode == GameMode.Catch:
            raise NotImplementedError("Base score for Catch has not yet been implemented.")
        elif mode == GameMode.Mania:
            raise NotImplementedError("Base score for Mania has not yet been implemented.")
        return 0


@dataclass(slots=True)
class ScoreState:
    max_combo: int = 0
    osu_large_tick_hits: int = 0
    osu_small_tick_hits: int = 0
    slider_end_hits: int = 0
    n_geki: int = 0
    n_katu: int = 0
    n300: int = 0
    n100: int = 0
    n50: int = 0
    misses: int = 0
    legacy_total_score: Optional[int] = None

    def total_hits(self, mode: GameMode) -> int:
        amount = self.n300 + self.n100 + self.misses

        if mode != GameMode.Taiko:
            amount += self.n50

            if mode != GameMode.Osu:
                amount += self.n_katu

                if mode != GameMode.Catch:
                    amount += self.n_geki

        return amount


class HitResultPriority(Enum):
    BEST_CASE = 0
    WORST_CASE = 1

class IHitResultGenerator(Protocol):
    @classmethod
    def generate_hitresults(cls, inspect_data: Any) -> Any:
        ...

class FastGenerator(IHitResultGenerator):
    pass

class ClosestGenerator(IHitResultGenerator):
    pass

class StatisticalGenerator(IHitResultGenerator):
    pass

class IgnoreAccuracyGenerator(IHitResultGenerator):
    pass


@dataclass
class DifficultyAttributes:
    stars: float = 0.0
    max_combo: int = 0

@dataclass
class PerformanceAttributes:
    pp: float = 0.0
    difficulty_attributes: DifficultyAttributes = None

    def stars(self) -> float:
        if self.difficulty_attributes:
            return self.difficulty_attributes.stars
        return 0.0

    def max_combo(self) -> int:
        if self.difficulty_attributes:
            return self.difficulty_attributes.max_combo
        return 0


class StrainsBase:
    SECTION_LEN = 400.0

    def section_len(self) -> float:
        return self.SECTION_LEN