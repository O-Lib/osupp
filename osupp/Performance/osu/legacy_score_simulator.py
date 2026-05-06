import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Any


class AddScoreComboMultiplier(Enum):
    YES = True
    NO = False

class IsBonus(Enum):
    YES = True
    NO = False

class IncreaseCombo(Enum):
    YES = True
    NO = False


@dataclass(slots=True)
class LegacyScoreAttributes:
    accuracy_score: int = 0
    combo_score: int = 0
    bonus_score_ratio: float = 0.0
    bonus_score: int = 0
    max_combo: int = 0


class LegacyScoreSimulatorInner:
    __slots__ = ("legacy_bonus_score", "standardised_bonus_score", "combo")

    def __init__(self):
        self.legacy_bonus_score = 0
        self.standardised_bonus_score = 0
        self.combo = 0

    def unrolled_recursion(
            self,
            attrs: LegacyScoreAttributes,
            add_score: AddScoreComboMultiplier,
            is_bonus: IsBonus,
            increase_combo: IncreaseCombo,
            score_increase: int,
            bonus_base_score: int
    ) -> Optional[float]:
        factor = None

        if add_score == AddScoreComboMultiplier.YES:
            factor = float(max(0, self.combo - 1)) * float(score_increase // 25)

        if is_bonus == IsBonus.YES:
            self.legacy_bonus_score += score_increase
            self.standardised_bonus_score += bonus_base_score
        else:
            attrs.accuracy_score += score_increase

        if increase_combo == IncreaseCombo.YES:
            self.combo += 1

        return factor

    def finalize(self, attrs: LegacyScoreAttributes):
        if self.legacy_bonus_score == 0:
            attrs.bonus_score_ratio = 0.0
        else:
            attrs.bonus_score_ratio = float(self.standardised_bonus_score) / float(self.legacy_bonus_score)

        attrs.bonus_score = self.legacy_bonus_score
        attrs.max_combo = self.combo


class OsuLegacyScoreSimulator:
    __slots__ = ("osu_objects", "passed_objects", "inner", "score_multiplier")

    def __init__(self, osu_objects: list, map_data: Any, passed_objects: int):
        self.osu_objects = osu_objects
        self.passed_objects = passed_objects
        self.inner = LegacyScoreSimulatorInner()
        self.score_multiplier = self._calculate_peppy_stars_multiplier(map_data, min(len(osu_objects), passed_objects))

    def _calculate_peppy_stars_multiplier(self, map_data: Any, object_count: int) -> float:
        return 1.0

    def simulate(self) -> LegacyScoreAttributes:
        attrs = LegacyScoreAttributes()

        for obj in self.osu_objects[:self.passed_objects]:
            self._simulate_hit(obj, attrs)

        self.inner.finalize(attrs)
        return attrs

    def _simulate_hit(self, hit_objects: Any, attrs: LegacyScoreAttributes):
        DEFAULT_BONUS_RESULT = 0
        kind = hit_objects.kind

        if getattr(kind, "is_circle", False) or type(kind).__name__ == "Circle":
            self._unrolled_recursion(attrs, AddScoreComboMultiplier.YES, IsBonus.NO, IncreaseCombo.YES, 300, DEFAULT_BONUS_RESULT)

        elif getattr(kind, "is_slider", False) or type(kind).__name__ == "OsuSlider":
            self._unrolled_recursion(attrs, AddScoreComboMultiplier.NO, IsBonus.NO, IncreaseCombo.YES, 30, DEFAULT_BONUS_RESULT)

            nested_objects = getattr(kind, "nested_objects", [])
            for nested in nested_objects:
                if getattr(nested.kind, "is_repeat", False) or getattr(nested.kind, "is_tail", False):
                    self._unrolled_recursion(attrs, AddScoreComboMultiplier.NO, IsBonus.NO, IncreaseCombo.YES, 30, DEFAULT_BONUS_RESULT)
                elif getattr(nested.kind, "is_tick", False):
                    self._unrolled.recursion(attrs, AddScoreComboMultiplier.NO, IsBonus.NO, IncreaseCombo.YES, 10, DEFAULT_BONUS_RESULT)

            self._unrolled_recursion(attrs, AddScoreComboMultiplier.YES, IsBonus.NO, IncreaseCombo.NO, 300, DEFAULT_BONUS_RESULT)

        elif getattr(kind, "is_spinner", False) or type(kind).__name__ == "Spinner":
            duration = getattr(kind, "duration", 0.0) / 1000.0

            MAXIMUM_ROTATIONS_PER_SECOND = 477.0 / 60.0
            MINIMUM_ROTATIONS_PER_SECOND = 3.0

            total_half_spins_possible = int(duration * MAXIMUM_ROTATIONS_PER_SECOND * 2.0)
            half_spins_required_for_completion = int(duration * MINIMUM_ROTATIONS_PER_SECOND)
            half_spins_required_before_bonus = half_spins_required_for_completion + 3

            for i in range(total_half_spins_possible + 1):
                if i > half_spins_required_before_bonus and (i - half_spins_required_before_bonus) % 2 == 0:
                    self._unrolled_recursion(attrs, AddScoreComboMultiplier.NO, IsBonus.YES, IncreaseCombo.NO, 1100, 50)
                elif i > 1 and i % 2 == 0:
                    self._unrolled_recursion(attrs, AddScoreComboMultiplier.NO, IsBonus.YES, IncreaseCombo.NO, 100, 10)

            # Término do Spinner
            self._unrolled_recursion(attrs, AddScoreComboMultiplier.YES, IsBonus.NO, IncreaseCombo.YES, 300, DEFAULT_BONUS_RESULT)

    def _unrolled_recursion(
            self,
            attrs: LegacyScoreAttributes,
            add_score: AddScoreComboMultiplier,
            is_bonus: IsBonus,
            increase_combo: IncreaseCombo,
            score_increase: int,
            bonus_base_score: int
    ):
        factor = self.inner.unrolled_recursion(attrs, add_score, is_bonus, increase_combo, score_increase, bonus_base_score)
        if factor is not None:
            attrs.combo_score += int(factor * self.score_multiplier)