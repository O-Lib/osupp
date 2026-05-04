import math
from typing import Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass, field

from osupp.Mods.game_mods import GameMods
from osupp.Beatmap.beatmap import Beatmap
from osupp.Beatmap.section.enums import GameMode
from osupp.Beatmap.utils import Pos

from ..any.any import CalculateError
from ..any.difficulty import Difficulty
from ..model.model import ConvertError


@dataclass
class OsuDifficultyAttributes:
    aim: float = 0.0
    aim_difficult_slider_count: float = 0.0
    speed: float = 0.0
    flashlight: float = 0.0
    slider_factor: float = 0.0
    aim_top_weighted_slider_factor: float = 0.0
    speed_top_weighted_slider_factor: float = 0.0
    speed_note_count: float = 0.0
    aim_difficult_strain_count: float = 0.0
    speed_difficult_strain_count: float = 0.0
    nested_score_per_object: float = 0.0
    legacy_score_base_multiplier: float = 0.0
    maximum_legacy_combo_score: float = 0.0
    ar: float = 0.0
    great_hit_window: float = 0.0
    ok_hit_window: float = 0.0
    meh_hit_window: float = 0.0
    hp: float = 0.0
    n_circles: int = 0
    n_sliders: int = 0
    n_large_ticks: int = 0
    n_spinners: int = 0
    stars: float = 0.0
    max_combo: int = 0

    def max_combo_val(self) -> int:
        return self.max_combo

    def n_objects(self) -> int:
        return self.n_circles + self.n_sliders + self.n_spinners

    def od(self) -> float:
        return (80.0 - self.great_hit_window) / 6.0

    def performance(self):
        from .performance import OsuPerformance
        return OsuPerformance()


@dataclass
class OsuPerformanceAttributes:
    difficulty: OsuDifficultyAttributes = field(default_factory=OsuDifficultyAttributes)
    pp: float = 0.0
    pp_acc: float = 0.0
    pp_aim: float = 0.0
    pp_flashlight: float = 0.0
    pp_speed: float = 0.0
    effective_miss_count: float = 0.0
    speed_deviation: Optional[float] = None
    combo_based_estimated_miss_count: float = 0.0
    score_based_estimated_miss_count: Optional[float] = None
    aim_estimated_slider_breaks: float = 0.0
    speed_estimated_slider_breaks: float = 0.0

    def stars(self) -> float:
        return self.difficulty.stars

    def pp_val(self) -> float:
        return self.pp

    def max_combo(self) -> int:
        return self.difficulty.max_combo

    def n_objects(self) -> int:
        return self.difficulty.n_objects()

    def performance(self):
        from .performance import OsuPerformance
        return OsuPerformance(self.difficulty)


class OsuScoreOrigin(Enum):
    Stable = 0
    WithSliderAcc = 1
    WithoutSliderAcc = 2

    def tick_scores(
            self,
            large_tick_hits: int,
            small_tick_hits: int,
            slider_end_hits: int,
            max_large_ticks: int = 0,
            max_slider_ends: int = 0,
            max_small_ticks: int = 0
    ) -> Tuple[int, int]:
        if self == OsuScoreOrigin.Stable:
            return (0, 0)
        elif self == OsuScoreOrigin.WithSliderAcc:
            return (
                150 * slider_end_hits + 30 * large_tick_hits,
                150 * max_slider_ends + 30 * max_large_ticks
            )
        elif self == OsuScoreOrigin.WithoutSliderAcc:
            return (
                30 * large_tick_hits + 10 * small_tick_hits,
                30 * max_large_ticks + 10 * max_small_ticks
            )
        return (0, 0)


@dataclass
class OsuHitResults:
    large_tick_hits: int = 0
    small_tick_hits: int = 0
    slider_end_hits: int = 0
    n300: int = 0
    n100: int = 0
    n50: int = 0
    misses: int = 0

    def total_hits(self) -> int:
        return self.n300 + self.n100 + self.n50 + self.misses

    def accuracy(self, origin: OsuScoreOrigin, max_large_ticks: int = 0, max_sliders_ends: int = 0, max_small_ticks: int = 0) -> float:
        numerator = float(6 * self.n300 + 2 * self.n100 + self.n50)
        denominator = float(6 * self.total_hits())

        if origin == OsuScoreOrigin.Stable:
            pass
        elif origin == OsuScoreOrigin.WithSliderAcc:
            slider_end_hits = min(self.slider_end_hits, max_sliders_ends)
            large_tick_hits = min(self.large_tick_hits, max_large_ticks)
            numerator += float(3 * slider_end_hits) + 0.6 * float(large_tick_hits)
            denominator += float(3 * max_sliders_ends) + 0.6 * float(max_large_ticks)
        elif origin == OsuScoreOrigin.WithoutSliderAcc:
            large_tick_hits = min(self.large_tick_hits, max_large_ticks)
            small_tick_hits = min(self.small_tick_hits, max_small_ticks)
            numerator += 0.6 * float(large_tick_hits) + 0.2 * float(small_tick_hits)
            denominator += 0.6 * float(max_large_ticks) + 0.2 * float(max_small_ticks)

        if denominator == 0.0:
            return 0.0
        return numerator / denominator


@dataclass
class OsuScoreState:
    max_combo: int = 0
    hitresults: OsuHitResults = field(default_factory=OsuHitResults)
    legacy_total_score: Optional[int] = None

# TO BE CONTINUED