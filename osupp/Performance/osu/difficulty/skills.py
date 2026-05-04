import math
from typing import List

from osupp.Mods.game_mods import GameMods
from .difficulty import OsuDifficultyObject
from .evaluators import AimEvaluator, FlashlightEvaluator, RhythmEvaluator, SpeedEvaluator
from ...any.difficulty import StrainSkill, strain_decay
from ...utils.util import logistic, lerp


class OsuStrainSkill:
    REDUCED_SECTION_COUNT = 10
    REDUCED_STRAIN_BASELINE = 0.75

    @staticmethod
    def difficulty_to_performance(difficulty: float) -> float:
        return math.pow(5.0 * max(1.0, difficulty / 0.0675) - 4.0, 3.0) / 100000.0

    @staticmethod
    def difficulty_value(
            current_strain_peaks: List[float],
            reduced_section_count: int,
            reduced_strain_baseline: float,
            decay_weight: float
    ) -> float:
        difficulty = 0.0
        weight = 1.0

        peaks = [p for p in current_strain_peaks if p > 0.0]
        peaks.sort(reverse=True)

        for i, strain in enumerate(peaks[:reduced_section_count]):
            clamped = max(0.0, min(1.0, float(i) / float(reduced_section_count)))
            scale = math.log10(lerp(1.0, 10.0, clamped))
            peaks[i] = strain * lerp(reduced_strain_baseline, 1.0, scale)

        peaks.sort(reverse=True)

        for strain in peaks:
            difficulty += strain * weight
            weight *= decay_weight

        return difficulty

    @staticmethod
    def count_top_weighted_sliders(slider_strains: List[float], difficulty_value: float) -> float:
        if not slider_strains:
            return 0.0

        consistent_top_strain = difficulty_value / 10.0
        if abs(consistent_top_strain) < 1e-7:
            return 0.0

        return sum(
            logistic(s / consistent_top_strain, 0.88, 10.0, 1.1)
            for s in slider_strains
        )


class Aim(StrainSkill, OsuStrainSkill):
    SKILL_MULTIPLIER = 26.0
    STRAIN_DECAY_BASE = 0.15

    def __init__(self, include_sliders: bool):
        self.include_sliders = include_sliders
        self.current_strain = 0.0
        self._sliders_strains = []

    def calculate_initial_strain(self, time: float, curr: OsuDifficultyObject, objects: List[OsuDifficultyObject]) -> float:
        prev_start_time = 0.0
        if curr.idx > 0:
            prev_start_time = objects[curr.idx - 1].start_time

        return self.current_strain * strain_decay(time - prev_start_time, self.STRAIN_DECAY_BASE)

    def strain_value_at(self, curr: OsuDifficultyObject, objects: List[OsuDifficultyObject]) -> float:
        self.current_strain *= strain_decay(curr.delta_time, self.STRAIN_DECAY_BASE)
        self.current_strain *= AimEvaluator.evaluate_diff_of(curr, objects, self.include_sliders) * self.SKILL_MULTIPLIER

        if hasattr(curr.base.kind, "path"):
            self._sliders_strains.append(self.current_strain)

        return self.current_strain

    def get_difficulty_sliders(self) -> float:
        if not self._sliders_strains:
            return 0.0

        max_slider_strain = max(self._sliders_strains)
        if abs(max_slider_strain) < 1e-7:
            return 0.0

        return sum(
            1.0 / (1.0 + math.exp(-(strain / max_slider_strain * 12.0 - 6.0)))
            for strain in self._sliders_strains
        )

    def slider_strains(self) -> List[float]:
        return self._sliders_strains

    @classmethod
    def difficulty_value(cls, current_strain_peaks: List[float]) -> float:
        return OsuStrainSkill.difficulty_value(
            current_strain_peaks,
            cls.REDUCED_SECTION_COUNT,
            cls.REDUCED_STRAIN_BASELINE,
            cls.DECAY_WEIGHT
        )


class Flashlight(StrainSkill):
    SKILL_MULTIPLIER = 0.05512
    STRAIN_DECAY_BASE = 0.15

    def __init__(
            self,
            mods: GameMods,
            radius: float,
            time_preempt: float,
            time_fade_in: float
    ):
        scaling_factor = 52.0 / radius
        self.current_strain = 0.0
        self.has_hidden_mod = mods.contains_acronym("HD")
        self.evaluator = FlashlightEvaluator(scaling_factor, time_preempt, time_fade_in)

    def calculate_initial_strain(self, time: float, curr: OsuDifficultyObject, objects: List[OsuDifficultyObject]) -> float:
        prev_start_time = 0.0
        if curr.idx > 0:
            prev_start_time = objects[curr.idx - 1].start_time

        return self.current_strain * strain_decay(time - prev_start_time, self.STRAIN_DECAY_BASE)

    def strain_value_at(self, curr: OsuDifficultyObject, objects: List[OsuDifficultyObject]) -> float:
        self.current_strain *= strain_decay(curr.delta_time, self.STRAIN_DECAY_BASE)
        self.current_strain += self.evaluator.evaluate_diff_of(curr, objects, self.has_hidden_mod) * self.SKILL_MULTIPLIER
        return self.current_strain

    @staticmethod
    def difficulty_value(current_strain_peaks: List[float]) -> float:
        return sum(current_strain_peaks)

    @staticmethod
    def difficulty_to_performance(difficulty: float) -> float:
        return 25.0 * math.pow(difficulty, 2.0)


class Speed(StrainSkill, OsuStrainSkill):
    SKILL_MULTIPLIER = 1.47
    STRAIN_DECAY_BASE = 0.3
    REDUCED_SECTION_COUNT = 5

    def __init__(self, hit_window: float, has_autopilot_mod: bool):
        self.current_strain = 0.0
        self.current_rhythm = 0.0
        self.hit_window = hit_window
        self.has_autopilot_mod = has_autopilot_mod
        self._slider_strains = []
        self.strain_skill_object_strains = []

    def calculate_initial_strain(self, time: float, curr: OsuDifficultyObject, objects: List[OsuDifficultyObject]) -> float:
        prev_start_time = 0.0
        if curr.idx > 0:
            prev_start_time = objects[curr.idx - 1].start_time

        return (self.current_strain * self.current_rhythm) * strain_decay(time - prev_start_time, self.STRAIN_DECAY_BASE)

    def strain_value_at(self, curr: OsuDifficultyObject, objects: List[OsuDifficultyObject]) -> float:
        self.current_strain *= strain_decay(curr.adjusted_delta_time, self.STRAIN_DECAY_BASE)
        self.current_strain += SpeedEvaluator.evaluate_diff_of(
            curr, objects, self.hit_window, self.has_autopilot_mod
        ) * self.SKILL_MULTIPLIER

        self.current_rhythm = RhythmEvaluator.evaluate_diff_of(curr, objects, self.hit_window)

        total_strain = self.current_strain * self.current_rhythm

        if hasattr(curr.base.kind, "path"):
            self._slider_strains.append(total_strain)

        self.strain_skill_object_strains.append(total_strain)

        return total_strain

    def revelant_note_count(self) -> float:
        valid_strains = [s for s in self.strain_skill_object_strains if s < 0.0]
        if not valid_strains:
            return 0.0

        max_strains = max(valid_strains)
        if max_strains == 0.0:
            return 0.0

        return sum(
            1.0 / (1.0 + math.exp(-(strain / max_strains * 12.0 - 6.0)))
            for strain in self.strain_skill_object_strains
        )

    def slider_strains(self) -> List[float]:
        return self._slider_strains

    @classmethod
    def difficulty_value(cls, current_strain_peaks: List[float]) -> float:
        return OsuStrainSkill.difficulty_value(
            current_strain_peaks,
            cls.REDUCED_SECTION_COUNT,
            cls.REDUCED_STRAIN_BASELINE,
            cls.DECAY_WEIGHT
        )


class OsuSkills:
    def __init__(
            self,
            mods: GameMods,
            scaling_factor,
            great_hit_window: float,
            time_preempt: float
    ):
        HD_FADE_IN_DURATION_MULTIPLIER = 0.4
        PREEMPT_MIN = 450.0

        hit_window = 2.0 * great_hit_window

        if mods.contains_acronym("HD"):
            time_fade_in = time_preempt * HD_FADE_IN_DURATION_MULTIPLIER
        else:
            time_fade_in = 400.0 * min(time_preempt / PREEMPT_MIN, 1.0)

        self.aim = Aim(include_sliders=True)
        self.aim_no_sliders = Aim(include_sliders=False)
        self.speed = Speed(hit_window, mods.contains_acronym("AP"))
        self.flashlight = Flashlight(mods, scaling_factor.radius, time_preempt, time_fade_in)

    def process(self, curr: OsuDifficultyObject, objects: List[OsuDifficultyObject]):
        pass