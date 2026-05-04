from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from osupp.Beatmap.beatmap import Beatmap
from osupp.Beatmap.section.enums import GameMode
from osupp.Beatmap.section.events import BreakPeriod
from osupp.Beatmap.section.hit_objects.hit_objects import (
    HitObject,
    HitObjectCircle,
    HitObjectSlider,
    HitObjectSpinner,
)

from ..any.any import HitResult
from ..model.beatmap.attributes import BeatmapAttributes
from ..utils.util import clamp


def calculate_difficulty_peppy_stars(map_attrs: BeatmapAttributes, object_count: int, drain_len: float) -> int:
    diff_val = map_attrs.hp() + map_attrs.od() + map_attrs.cs() + clamp(map_attrs.ar(), 0.0, 10.0)
    stars = diff_val * 27.0 / 25.0
    return int(round(stars))

def round_time(time: float) -> int:
    return int(round(time))


class AddScoreComboMultiplier(Enum):
    YES = 1
    NO = 0

class IsBonus(Enum):
    YES = 1
    NO = 0

class IncreaseCombo(Enum):
    YES = 1
    NO = 0


@dataclass
class LegacyScoreAttributes:
    accuracy_score: int = 0
    combo_score: int = 0
    bonus_score_ratio: float = 0.0
    bonus_score: int = 0
    max_combo: int = 0


class LegacyScoreSimulatorInner:
    def __init__(self):
        self.legacy_bonus_score: int = 0
        self.standardised_bonus_score: int = 0
        self.combo: int = 0

    def unrolled_recursion(
            self,
            attrs: LegacyScoreAttributes,
            add_score_combo_multiplier: AddScoreComboMultiplier,
            is_bonus: IsBonus,
            increase_combo: IncreaseCombo,
            score_increase: int,
            bonus_result: HitResult
    ) -> float | None:
        factor = None

        if add_score_combo_multiplier == AddScoreComboMultiplier.YES:
            combo_val = max(0, self.combo - 1)
            factor = float(combo_val) * float(score_increase // 25)

        if is_bonus == IsBonus.YES:
            self.legacy_bonus_score += score_increase
            self.standardised_bonus_score += bonus_result.base_score(GameMode.Osu)
        else:
            attrs.accuracy_score += score_increase

        if increase_combo == IncreaseCombo.YES:
            self.combo += 1

        return factor

    def finalize(self, attrs: LegacyScoreAttributes) -> None:
        if self.legacy_bonus_score == 0:
            attrs.bonus_score_ratio = 0.0
        else:
            attrs.bonus_score_ratio = float(self.standardised_bonus_score) / float(self.legacy_bonus_score)

        attrs.bonus_score = self.legacy_bonus_score
        attrs.max_combo = self.combo


class OsuLegacyScoreSimulator:
    def __init__(self, osu_objects: list[HitObject], map_data: Beatmap, passed_objects: int):
        self.osu_objects = osu_objects
        self.passed_objects = passed_objects
        self.inner = LegacyScoreSimulatorInner()

        from ..model.beatmap.attributes import ModStatus

        map_attrs = BeatmapAttributes(
            difficulty=map_data.difficulty,
            mode=map_data.mode,
            clock_rate=1.0,
            is_convert=False,
            classic_and_not_v2=True,
            mod_status=ModStatus.NEITHER
        )
        sm = self.score_multiplier(map_data, map_attrs, passed_objects)
        self.score_multiplier_val = float(sm)

    @staticmethod
    def score_multiplier(map_data: Beatmap, map_attrs: BeatmapAttributes, passed_objects: int) -> int:
        hit_objects = map_data.hit_objects.hit_objects
        object_count = len(hit_objects[:passed_objects])

        drain_len = 0

        if hit_objects:
            first = hit_objects[0]

            last_idx = max(0, passed_objects - 1)
            if last_idx < len(hit_objects):
                last = hit_objects[last_idx]
            else:
                last = hit_objects[-1]

            break_len = 0
            for b in map_data.events.breaks:
                if b.end_time < last.start_time:
                    break_len += round_time(b.end_time) - round_time(b.start_time)
                else:
                    break

            full_len = round_time(last.start_time) - round_time(first.start_time)
            drain_len = (full_len - break_len) // 1000

        return calculate_difficulty_peppy_stars(map_attrs, object_count, float(drain_len))

    def simulate(self) -> "LegacyScoreAttributes":
        attrs = LegacyScoreAttributes()

        limit = min(len(self.osu_objects), self.passed_objects)
        for obj in self.osu_objects[:limit]:
            self.simulate_hit(obj, attrs)

        self.inner.finalize(attrs)
        return attrs

    def simulate_hit(self, hit_objects: HitObject, attrs: LegacyScoreAttributes) -> None:
        DEFAULT_BONUS_RESULT = HitResult.NONE

        if isinstance(hit_objects.kind, HitObjectCircle):
            self.unrolled_recursion(
                attrs,
                AddScoreComboMultiplier.YES,
                IsBonus.NO,
                IncreaseCombo.YES,
                300,
                DEFAULT_BONUS_RESULT
            )

        elif isinstance(hit_objects.kind, HitObjectSlider):
            slider = hit_objects.kind
            self.unrolled_recursion(
                attrs,
                AddScoreComboMultiplier.NO,
                IsBonus.NO,
                IncreaseCombo.YES,
                30,
                DEFAULT_BONUS_RESULT
            )

            tick_dist = 100.0
            if hasattr(slider, "velocity") and slider.velocity > 0:
                pass

            nested_objects = getattr(slider, "nested_objects", [])
            for nested in nested_objects:
                kind = getattr(nested, "kind", None)
                if kind in ("Repeat", "Tail"):
                    self.unrolled_recursion(
                        attrs,
                        AddScoreComboMultiplier.NO,
                        IsBonus.NO,
                        IncreaseCombo.YES,
                        30,
                        DEFAULT_BONUS_RESULT
                    )
                elif kind == "Tick":
                    self.unrolled_recursion(
                        attrs,
                        AddScoreComboMultiplier.NO,
                        IsBonus.NO,
                        IncreaseCombo.YES,
                        10,
                        DEFAULT_BONUS_RESULT
                    )

            self.unrolled_recursion(
                attrs,
                AddScoreComboMultiplier.YES,
                IsBonus.NO,
                IncreaseCombo.NO,
                300,
                DEFAULT_BONUS_RESULT
            )
        elif isinstance(hit_objects.kind, HitObjectSpinner):
            spinner = hit_objects.kind
            MAXIMUM_ROTATIONS_PER_SECOND = 477.0 / 60.0
            MINIMUM_ROTATIONS_PER_SECOND = 3.0

            seconds_duration = spinner.duration / 1000.0

            total_half_spins_possible = int(seconds_duration * MAXIMUM_ROTATIONS_PER_SECOND * 2.0)
            half_spins_required_for_completion = int(seconds_duration * MINIMUM_ROTATIONS_PER_SECOND)
            half_spins_required_before_bonus = half_spins_required_for_completion + 3

            for i in range(total_half_spins_possible + 1):
                if i > half_spins_required_before_bonus and (i - half_spins_required_before_bonus) % 2 == 0:
                    self.unrolled_recursion(
                        AddScoreComboMultiplier.NO,
                        IsBonus.YES,
                        IncreaseCombo.NO,
                        1100,
                        HitResult.LARGE_BONUS
                    )
                elif i > 1 and i % 2 == 0:
                    self.unrolled_recursion(
                        AddScoreComboMultiplier.NO,
                        IsBonus.YES,
                        IncreaseCombo.NO,
                        100,
                        HitResult.SMALL_BONUS
                    )
            self.unrolled_recursion(
                AddScoreComboMultiplier.YES,
                IsBonus.NO,
                IncreaseCombo.YES,
                300,
                DEFAULT_BONUS_RESULT
            )

    def unrolled_recursion(
            self,
            attrs: LegacyScoreAttributes,
            add_score_combo_multiplier: AddScoreComboMultiplier,
            is_bonus: IsBonus,
            increase_combo: IncreaseCombo,
            score_increase: int,
            bonus_result: HitResult
    ) -> None:
        factor = self.inner.unrolled_recursion(
            attrs,
            add_score_combo_multiplier,
            is_bonus,
            increase_combo,
            score_increase,
            bonus_result
        )

        if factor is not None:
            attrs.combo_score += int(factor * self.score_multiplier_val)


class GradualLegacyScoreSimulator:
    def __init__(self, map_data: Beatmap, map_attrs: BeatmapAttributes):
        self.map_attrs = map_attrs

        from ..model.beatmap.attributes import ModStatus

        self.map_attrs_nomod = BeatmapAttributes(
            difficulty=map_data.difficulty,
            mode=map_data.mode,
            clock_rate=1.0,
            is_convert=False,
            classic_and_not_v2=True,
            mod_status=ModStatus.NEITHER
        )

        self.attrs = LegacyScoreAttributes()
        self.inner = LegacyScoreSimulatorInner()
        self.combo_score_factors: list[float] = []

        self.breaks: list[BreakPeriod] = list(map_data.events.breaks)
        self.break_idx = 0

        self.elapsed_curr_break: int | None = None
        self.break_len_prelim: int = 0
        self.object_count: int = 0
        self.start_time: int | None = None

    def break_len(self) -> int:
        elapsed = self.elapsed_curr_break if self.elapsed_curr_break is not None else 0
        return self.break_len_prelim + elapsed

    def score_multiplier(self, obj: HitObject, nomod: bool) -> float:
        start_t = self.start_time if self.start_time is not None else round_time(obj.start_time)
        end_t = round_time(obj.start_time)
        drain_len = (end_t - start_t - self.break_len()) // 1000.0

        m_attrs = self.map_attrs_nomod if nomod else self.map_attrs

        return float(calculate_difficulty_peppy_stars(
            m_attrs,
            self.object_count,
            drain_len
        ))

    def prepare_score_multiplier(self, obj: HitObject) -> None:
        while self.break_idx < len(self.breaks):
            b = self.breaks[self.break_idx]
            if b.start_time >= obj.start_time:
                break

            if b.end_time < obj.start_time:
                self.break_len_prelim += round_time(b.end_time) - round_time(b.start_time)
                self.elapsed_curr_break = None
                self.break_idx += 1
            else:
                period_end = min(round(b.end_time), round_time(obj.start_time))
                self.elapsed_curr_break = period_end - round_time(b.start_time)
                break

        self.object_count += 1
        if self.start_time is None:
            self.start_time = round_time(obj.start_time)

    def simulate_next(self, obj: HitObject) -> LegacyScoreAttributes:
        self.prepare_score_multiplier(obj)
        score_multi = self.score_multiplier(obj, True)

        self.simulate_hit(obj)

        combo_score = 0.0
        for factor in self.combo_score_factors:
            combo_score += factor * score_multi

        self.attrs.combo_score = int(combo_score)
        self.inner.finalize(self.attrs)

        return LegacyScoreAttributes(
            accuracy_score=self.attrs.accuracy_score,
            combo_score=self.attrs.combo_score,
            bonus_score_ratio=self.attrs.bonus_score_ratio,
            bonus_score=self.attrs.bonus_score,
            max_combo=self.attrs.max_combo
        )

    def simulate_hit(self, hit_object: HitObject) -> None:
        DEFAULT_BONUS_RESULT = HitResult.NONE

        if isinstance(hit_object.kind, HitObjectCircle):
            self.unrolled_recursion(
                AddScoreComboMultiplier.YES,
                IsBonus.NO,
                IncreaseCombo.YES,
                300,
                DEFAULT_BONUS_RESULT
            )

        elif isinstance(hit_object.kind, HitObjectSlider):
            slider = hit_object.kind

            self.unrolled_recursion(
                AddScoreComboMultiplier.NO,
                IsBonus.NO,
                IncreaseCombo.YES,
                30,
                DEFAULT_BONUS_RESULT
            )

            nested_objects = getattr(slider, "nested_objects", [])
            for nested in nested_objects:
                kind = getattr(nested, "kind", None)
                if kind in ("Repeat", "Tail"):
                    self.unrolled_recursion(
                        AddScoreComboMultiplier.NO,
                        IsBonus.NO,
                        IncreaseCombo.YES,
                        30,
                        DEFAULT_BONUS_RESULT
                    )
                elif kind == "Tick":
                    self.unrolled_recursion(
                        AddScoreComboMultiplier.NO,
                        IsBonus.NO,
                        IncreaseCombo.YES,
                        10,
                        DEFAULT_BONUS_RESULT
                    )

            self.unrolled_recursion(
                AddScoreComboMultiplier.YES,
                IsBonus.NO,
                IncreaseCombo.NO,
                300,
                DEFAULT_BONUS_RESULT
            )

        elif isinstance(hit_object.kind, HitObjectSpinner):
            spinner = hit_object.kind
            MAXIMUM_ROTATIONS_PER_SECOND = 477.0 / 60.0
            MINIMUM_ROTATIONS_PER_SECOND = 3.0

            seconds_duration = spinner.duration / 1000.0

            total_half_spins_possible = int(seconds_duration * MAXIMUM_ROTATIONS_PER_SECOND * 2.0)
            half_spins_required_for_completion = int(seconds_duration * MINIMUM_ROTATIONS_PER_SECOND)
            half_spins_required_before_bonus = half_spins_required_for_completion + 3

            for i in range(total_half_spins_possible + 1):
                if i > half_spins_required_before_bonus and (i - half_spins_required_before_bonus) % 2 == 0:
                    self.unrolled_recursion(
                        AddScoreComboMultiplier.NO,
                        IsBonus.YES,
                        IncreaseCombo.NO,
                        1100,
                        HitResult.LARGE_BONUS
                    )
                elif i > 1 and i % 2 == 0:
                    self.unrolled_recursion(
                        AddScoreComboMultiplier.NO,
                        IsBonus.YES,
                        IncreaseCombo.NO,
                        100,
                        HitResult.SMALL_BONUS
                    )

            self.unrolled_recursion(
                AddScoreComboMultiplier.YES,
                IsBonus.NO,
                IncreaseCombo.YES,
                300,
                DEFAULT_BONUS_RESULT
            )

    def unrolled_recursion(
            self,
            add_score_combo_multiplier: AddScoreComboMultiplier,
            is_bonus: IsBonus,
            increase_combo: IncreaseCombo,
            score_increase: int,
            bonus_result: HitResult
    ) -> None:
        factor = self.inner.unrolled_recursion(
            self.attrs,
            add_score_combo_multiplier,
            is_bonus,
            increase_combo,
            score_increase,
            bonus_result
        )

        if factor is not None:
            self.combo_score_factors.append(factor)
