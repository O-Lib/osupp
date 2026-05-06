import math
from dataclasses import dataclass
from typing import Any, Optional
from collections.abc import Callable

from ...any.any import HitResultPriority
from ...model.model import GameMods
from ...utils.utils import clamp, erf, erf_inv, logistic, reverse_lerp, smoothstep
from ..osu import (
    OsuDifficultyAttributes,
    OsuHitResults,
    OsuPerformanceAttributes,
    OsuScoreOrigin,
    OsuScoreState,
)
from .hitresult_generator import HitResultGenerator, InspectOsuPerformance

PERFORMANCE_BASE_MULTIPLIER = 1.14


class OsuPerformanceCalculator:
    __slots__ = ("attrs", "mods", "acc", "state", "using_classic_slider_acc")

    def __init__(self, attrs: OsuDifficultyAttributes, mods: GameMods, acc: float, state: OsuScoreState, using_classic_slider_acc: bool):
        self.attrs = attrs
        self.mods = mods
        self.acc = acc
        self.state = state
        self.using_classic_slider_acc = using_classic_slider_acc

    def calculate(self) -> OsuPerformanceAttributes:
        total_hits = getattr(self.attrs, "n_circles", 0) + getattr(self.attrs, "n_sliders", 0) + getattr(self.attrs, "n_spinners", 0)

        if total_hits == 0:
            total_hits = self.attrs.max_combo

        if total_hits == 0:
            return OsuPerformanceAttributes(difficulty=self.attrs)

        combo_based_estimated_miss_count = self._calculate_combo_based_estimated_miss_count()
        score_based_estimated_miss_count = None

        effective_miss_count = combo_based_estimated_miss_count
        if self.using_classic_slider_acc and self.state.legacy_total_score is not None:
            score_based_estimated_miss_count = float(self.state.hitresults.misses)
            effective_miss_count = score_based_estimated_miss_count

        effective_miss_count = max(effective_miss_count, float(self.state.hitresults.misses))
        effective_miss_count = min(effective_miss_count, float(total_hits))

        multiplier = PERFORMANCE_BASE_MULTIPLIER

        if self.mods.nf:
            multiplier *= max(1.0 - 0.02 * effective_miss_count, 0.9)

        if self.mods.so and total_hits > 0.0:
            n_spinners = getattr(self.attrs, "n_spinners", 0)
            multiplier *= 1.0 - math.pow(float(n_spinners) / float(total_hits), 0.85)

        if self.mods.rx:
            od = self.attrs.od
            n100_mult = 0.75 * max(1.0 - od / 13.33, 0.0) if od > 0.0 else 1.0
            n50_mult = max(1.0 - math.pow(od / 13.33, 5.0), 0.0) if od > 0.0 else 1.0

            effective_miss_count = min(
                effective_miss_count + float(self.state.hitresults.n100) * n100_mult + float(self.state.hitresults.n50) * n50_mult,
                float(total_hits)
            )

        speed_deviation = self._calculate_speed_deviation()

        aim_estimated_slider_breaks = [0.0]
        speed_estimated_slider_breaks = [0.0]

        aim_value = self._compute_aim_value(effective_miss_count, aim_estimated_slider_breaks, total_hits)
        speed_value = self._compute_speed_value(speed_deviation, effective_miss_count, speed_estimated_slider_breaks, total_hits)
        acc_value = self._compute_accuracy_value(total_hits)
        flashlight_value = self._compute_flashlight_value(effective_miss_count, total_hits)

        pp = math.pow(
            math.pow(aim_value, 1.1) +
            math.pow(speed_value, 1.1) +
            math.pow(acc_value, 1.1) +
            math.pow(flashlight_value, 1.1),
            1.0 / 1.1
        ) * multiplier

        return OsuPerformanceAttributes(
            difficulty=self.attrs,
            pp=pp, pp_acc=acc_value, pp_aim=aim_value,
            pp_flashlight=flashlight_value, pp_speed=speed_value,
            effective_miss_count=effective_miss_count
        )

    def _compute_aim_value(self, effective_miss_count: float, aim_estimated_slider_breaks: list[float], total_hits: float) -> float:
        if self.mods.ap: return 0.0

        aim_difficulty = self.attrs.aim
        aim_value = 25.0 * math.pow(aim_difficulty, 2.0)

        len_bonus = 0.95 + 0.4 * min(total_hits, 2000.0, 1.0)
        if total_hits > 2000.0:
            len_bonus += math.log10(total_hits, 2000.0) * 0.5
        aim_value *= len_bonus

        if effective_miss_count > 0.0:
            relevant_miss_count = min(effective_miss_count, self._total_imperfect_hits())
            aim_value *= self._calculate_miss_penalty(relevant_miss_count, max(self.attrs.aim_difficult_strain_count, 1.0))

        aim_value *= self.acc
        return aim_value

    def _compute_speed_value(self, speed_deviation: float | None, effective_miss_count: float, speed_estimated_slider_breaks: list[float], total_hits: float) -> float:
        if self.mods.rx: return 0.0

        speed_value = 25.0 * math.pow(self.attrs.speed, 2.0)

        len_bonus = 0.95 + 0.4 * min(total_hits / 2000.0, 1.0)
        if total_hits > 2000.0:
            len_bonus += math.log10(total_hits / 2000.0) * 0.5
        speed_value *= len_bonus

        if effective_miss_count > 0.0:
            relevant_miss_count = min(effective_miss_count, self._total_imperfect_hits())
            speed_value *= self._calculate_miss_penalty(relevant_miss_count, max(self.attrs.speed_difficult_strain_count, 1.0))

        if speed_deviation is not None:
            speed_value *= self._calculate_speed_high_deviation_nerf(speed_deviation, speed_value)

        od = self.attrs.od
        speed_value *= math.pow(self.acc, (14.5 - od) / 2.0)

        return speed_value

    def _compute_accuracy_value(self, total_hits: float) -> float:
        if self.mods.rx: return 0.0

        amount_hit_objects_with_acc = getattr(self.attrs, "n_circles", total_hits)
        if not self.using_classic_slider_acc:
            amount_hit_objects_with_acc += getattr(self.attrs, "n_sliders", 0)

        better_acc_percentage = 0.0
        if amount_hit_objects_with_acc > 0:
            n300_adjusted = self.state.hitresults.n300 - max(int(total_hits) - int(amount_hit_objects_with_acc), 0)
            points = max(n300_adjusted, 0) * 6 + self.state.hitresults.n100 * 2 + self.state.hitresults.n50
            better_acc_percentage = max(float(points) / float(amount_hit_objects_with_acc * 6), 0.0)

        acc_value = math.pow(1.52163, self.attrs.od) * math.pow(better_acc_percentage, 24.0) * 2.83
        acc_value *= min(math.pow(float(amount_hit_objects_with_acc) / 1000.0, 0.3), 1.15)

        if self.mods.hd:
            acc_value *= 1.0 + 0.08 * reverse_lerp(self.attrs.ar, 11.5, 10.0)
        if self.mods.fl:
            acc_value *= 1.02

        return acc_value

    def _compute_flashlight_value(self, effective_miss_count: float, total_hits: float) -> float:
        if not self.mods.fl: return 0.0

        flashlight_value = 25.0 * math.pow(self.attrs.flashlight, 2.0)

        if effective_miss_count > 0.0 and total_hits > 0.0:
            flashlight_value *= 0.97 * math.pow(1.0 - math.pow(effective_miss_count / total_hits, 0.775), math.pow(effective_miss_count, 0.875))

        combo_factor = min(math.pow(float(self.state.max_combo), 0.8) / math.pow(float(max(self.attrs.max_combo, 1)), 0.8), 1.0)
        flashlight_value *= combo_factor
        flashlight_value *= 0.5 + self.acc / 2.0

        return flashlight_value

    def _calculte_combo_based_estimated_miss_count(self) -> float:
        miss_count = float(self.state.hitresults.misses)
        n_sliders = getattr(self.attrs, "n_sliders", 0)

        if n_sliders > 0 and self.using_classic_slider_acc:
            full_combo_threshold = float(self.attrs.max_combo) - 0.1 * float(n_sliders)
            if float(self.state.max_combo) < full_combo_threshold:
                miss_count = max(miss_count, full_combo_threshold / max(float(self.state.max_combo), 1.0))

        return min(miss_count, self._total_imperfect_hits())

    def _calculate_speed_deviation(self) -> float | None:
        if self.mods.rx or self.state.hitresults.n300 + self.state.hitresults.n100 + self.state.hitresults.n50 == 0:
            return None

        n = max(1.0, float(self.state.hitresults.n300 + self.state.hitresults.n100))
        p = float(self.state.hitresults.n300) / n

        Z = 2.32634787404
        p_lower_bound = min((n * p + Z * Z / 2.0) / (n + Z * Z) -Z / (n + Z * Z) * math.sqrt(n * p * (1.0 - p) + Z * Z / 4.0), p)

        great_window = 43.0
        if p_lower_bound > 0.01:
            deviation = great_window / (math.sqrt(2.0) *  erf_inv(p_lower_bound))
        else:
            deviation = 93.0 / math.sqrt(3.0)

        return deviation

    def _calculate_speed_high_deviation_nerf(self, speed_deviation: float, speed_value: float ) -> float:
        excess_speed_cutoff = 100.0 + 220.0 * math.pow(22.0 / speed_deviation, 6.5) if speed_deviation > 0 else float('inf')
        if speed_value <= excess_speed_cutoff:
            return 1.0

        SCALE = 50.0
        adjusted = SCALE * (math.log((speed_value - excess_speed_cutoff) / SCALE + 1.0) + excess_speed_cutoff / SCALE)
        lerp_val = 1.0 - reverse_lerp(speed_deviation, 22.0, 27.0)
        adjusted = adjusted * (1.0 - lerp_val) + speed_value * lerp_val

        return adjusted / max(speed_value, 1e-10)

    @staticmethod
    def _calculate_miss_penalty(miss_count: float, diff_strain_count: float) -> float:
        if diff_strain_count <= 0: return 1.0
        return 0.96 / ((miss_count / (4.0 * math.pow(math.log(diff_strain_count), 0.94))) + 1.0)

    def _total_imperfect_hits(self) -> float:
        return float(self.state.hitresults.n100 + self.state.hitresults.n50 + self.state.hitresults.misses)


class OsuPerformance:
    __slots__ = ("_map_or_attrs", "difficulty", "acc", "combo", "n300", "n100", "n50", "misses", "_hitresult_priority", "_lazer")

    def __init__(self, map_or_attrs: Any):
        self._map_or_attrs = map_or_attrs
        self.difficulty = None
        self.acc = None
        self.combo = None
        self.n300 = None
        self.n100 = None
        self.n50 = None
        self.misses = 0
        self._hitresult_priority = HitResultPriority.BEST_CASE
        self._lazer = True

    def mods(self, mods: GameMods) -> "OsuPerformance":
        if self.difficulty: self.difficulty.mods(mods)
        return self

    def accuracy(self, acc: float) -> "OsuPerformance":
        self.acc = clamp(acc, 0.0, 100.0) / 100.0
        return self

    def set_misses(self, n_misses: int) -> "OsuPerformance":
        self.misses = n_misses
        return self

    def set_combo(self, max_combo: int) -> "OsuPerformance":
        self.combo = max_combo
        return self

    def priority(self, priority: HitResultPriority) -> "OsuPerformance":
        self._hitresult_priority = priority
        return self

    def generate_state(self, total_hits: int) -> OsuScoreState:
        inspect = InspectOsuPerformance(
            total_hits=total_hits,
            misses=self.misses,
            acc=self.acc,
            n300=self.n300,
            n100=self.n100,
            n50=self.n50,
            priority=self._hitresult_priority,
            origin=OsuScoreOrigin.WITH_SLIDER_ACC if self._lazer else OsuScoreOrigin.STABLE
        )

        hitresults = HitResultGenerator.generate_closest(inspect) if self.acc is not None else HitResultGenerator.generate_ignore_accuracy(inspect)

        return OsuScoreState(
            max_combo=self.combo if self.combo is not None else 0,
            hitresults=hitresults,
            legacy_total_score=None
        )

    def calculate(self, attrs: OsuDifficultyAttributes) -> OsuPerformanceAttributes:
        total_hits = getattr(attrs, "n_circles", 0) + getattr(attrs, "n_sliders", 0) + getattr(attrs, "n_spinners", 0)
        if total_hits == 0: total_hits = attrs.max_combo

        state = self.generate_state(total_hits)
        mods = getattr(self.difficulty, "_mods", GameMods()) if self.difficulty else GameMods()
        using_classic_slider_acc = mods.no_slider_head_acc(self._lazer)

        calc = OsuPerformanceCalculator(attrs, mods, self.acc if self.acc is not None else 1.0, state, using_classic_slider_acc)
        return calc.calculate()


class OsuGradualPerformance:
    __slots__ = ("difficulty_iter", "attrs")

    def __init__(self, difficulty_iter: Any):
        self.difficulty_iter = difficulty_iter
        self.attrs = None

    def next(self, state: OsuScoreState) -> OsuPerformanceAttributes | None:
        try:
            self.attrs = next(self.difficulty_iter)
        except StopIteration:
            return None

        calc = OsuPerformanceCalculator(self.attrs, GameMods(), 1.0, state, False)
        return calc.calculate()
