import math
from dataclasses import dataclass, field

from ...model.model import GameMods
from ...utils.utils import lerp
from .difficulty import OsuDifficultyObject, ScalingFactor
from .evaluators import (
    AimEvaluator,
    FlashlightEvaluator,
    RhythmEvaluator,
    SpeedEvaluator,
)


def calculate_difficulty_value(
    current_strain_peaks: list[float],
    reduced_section_count: int,
    reduced_strain_baseline: float,
    decay_weight: float
) -> float:
    difficulty = 0.0
    weight = 1.0

    peaks = [p for p in current_strain_peaks if p > 0.0]
    peaks.sort(reverse=True)

    for i in range(min(reduced_section_count, len(peaks))):
        clamped = min(max(float(i) / float(reduced_section_count), 0.0), 1.0)
        scale = math.log10(lerp(1.0, 10.0, clamped))
        peaks[i] *= lerp(reduced_strain_baseline, 1.0, scale)

    peaks.sort(reverse=True)

    for strain in peaks:
        difficulty += strain * weight
        weight *= decay_weight

    return difficulty


def count_top_weighted_sliders(slider_strains: list[float], difficulty_value: float) -> float:
    if not slider_strains:
        return 0.0

    consistent_top_strain = difficulty_value / 10.0
    if abs(consistent_top_strain) < 1e-7:
        return 0.0

    return sum(1.0 / (1.0 + math.exp(-(strain / consistent_top_strain * 12.0 - 6.0))) for strain in slider_strains)


@dataclass(slots=True)
class OsuStrainSkill:
    current_section_peak: float = 0.0
    current_section_end: float = 0.0
    strain_peaks: list[float] = field(default_factory=list)

    SECTION_LEN = 400.0
    DECAY_WEIGHT = 0.9
    REDUCED_SECTION_COUNT = 10
    REDUCED_STRAIN_BASELINE = 0.75

    def strain_value_at(self, curr: OsuDifficultyObject, objects: list[OsuDifficultyObject]) -> float:
        return 0.0

    def calculate_initial_strain(self, time: float, curr: OsuDifficultyObject, objects: list[OsuDifficultyObject]) -> float:
        return 0.0

    def process(self, curr: OsuDifficultyObject, objects: list[OsuDifficultyObject]) -> None:
        if self.current_section_end == 0.0:
            self.current_section_end = math.ceil(curr.start_time / self.SECTION_LEN) * self.SECTION_LEN

        while curr.start_time > self.current_section_end:
            self.save_current_peak()
            self.start_new_section_from(self.current_section_end, curr, objects)
            self.current_section_end += self.SECTION_LEN

        self.current_section_peak = max(self.current_section_peak, self.strain_value_at(curr, objects))

    def save_current_peak(self) -> None:
        self.strain_peaks.append(self.current_section_peak)

    def start_new_section_from(self, time: float, curr: OsuDifficultyObject, objects: list[OsuDifficultyObject]) -> None:
        self.current_section_peak = self.calculate_initial_strain(time, curr, objects)

    def difficulty_value(self) -> float:
        return calculate_difficulty_value(self.strain_peaks, self.REDUCED_SECTION_COUNT, self.REDUCED_STRAIN_BASELINE, self.DECAY_WEIGHT)


@dataclass(slots=True)
class Aim(OsuStrainSkill):
    include_sliders: bool = True
    current_strain: float = 0.0
    slider_strains: list[float] = field(default_factory=list)

    SKILL_MULTIPLIER = 26.0
    STRAIN_DECAY_BASE = 0.15

    def calculate_initial_strain(self, time: float, curr: OsuDifficultyObject, objects: list[OsuDifficultyObject]) -> float:
        prev_start_time = objects[curr.idx - 1].start_time if curr.idx > 0 else 0.0
        decay = self.STRAIN_DECAY_BASE ** ((time - prev_start_time) / 1000.0)
        return self.current_strain * decay

    def strain_value_at(self, curr: OsuDifficultyObject, objects: list[OsuDifficultyObject]) -> float:
        self.current_strain *= self.STRAIN_DECAY_BASE ** (curr.delta_time / 1000.0)
        self.current_strain += AimEvaluator.evaluate_diff_of(curr, objects, self.include_sliders) * self.SKILL_MULTIPLIER

        if getattr(curr.base.kind, "is_slider", False):
            self.slider_strains.append(self.current_strain)

        return self.current_strain

    def get_difficulty_sliders(self) -> float:
        if not self.slider_strains:
            return 0.0

        max_slider_strain = max(self.slider_strains)
        if max_slider_strain == 0.0:
            return 0.0

        return sum(1.0 / (1.0 + math.exp(-(strain / max_slider_strain * 12.0 - 6.0))) for strain in self.slider_strains)


@dataclass(slots=True)
class Speed(OsuStrainSkill):
    hit_window: float = 0.0
    has_autopilot_mod: bool = False
    current_strain: float = 0.0
    current_rhythm: float = 0.0
    slider_strains: list[float] = field(default_factory=list)

    SKILL_MULTIPLIER = 1.47
    STRAIN_DECAY_BASE = 0.3
    REDUCED_SECTION_COUNT = 5

    def calculate_initial_strain(self, time: float, curr: OsuDifficultyObject, objects: list[OsuDifficultyObject]) -> float:
        prev_start_time = objects[curr.idx - 1].start_time if curr.idx > 0 else 0.0
        decay = self.STRAIN_DECAY_BASE ** ((time - prev_start_time) / 1000.0)
        return (self.current_strain * self.current_rhythm) * decay

    def strain_value_at(self, curr: OsuDifficultyObject, objects: list[OsuDifficultyObject]) -> float:
        self.current_strain *= self.STRAIN_DECAY_BASE ** (curr.adjusted_delta_time / 1000.0)
        self.current_strain += SpeedEvaluator.evaluate_diff_of(curr, objects, self.hit_window, self.has_autopilot_mod) * self.SKILL_MULTIPLIER
        self.current_rhythm = RhythmEvaluator.evaluate_diff_of(curr, objects, self.hit_window)

        total_strain = self.current_strain * self.current_rhythm

        if getattr(curr.base.kind, "is_slider", False):
            self.slider_strains.append(total_strain)

        return total_strain

    def relevant_note_count(self) -> float:
        if not self.strain_peaks:
            return 0.0

        max_strain = max(self.strain_peaks)
        if max_strain == 0.0:
            return 0.0

        return sum(1.0 / (1.0 + math.exp(-(strain / max_strain * 12.0 - 6.0))) for strain in self.strain_peaks if strain > 0.0)

    def difficulty_value(self) -> float:
        return calculate_difficulty_value(self.strain_peaks, self.REDUCED_SECTION_COUNT, self.REDUCED_STRAIN_BASELINE, self.DECAY_WEIGHT)


@dataclass(slots=True)
class Flashlight(OsuStrainSkill):
    has_hidden_mod: bool = False
    evaluator: FlashlightEvaluator = field(init=False)
    current_strain: float = 0.0

    SKILL_MULTIPLIER = 0.05512
    STRAIN_DECAY_BASE = 0.15

    @classmethod
    def new(cls, mods: GameMods, radius: float, time_preempt: float, time_fade_in: float) -> "Flashlight":
        inst = cls(has_hidden_mod=mods.hd)
        scaling_factor = 52.0 / radius
        inst.evaluator = FlashlightEvaluator(scaling_factor, time_preempt, time_fade_in)
        return inst

    def calculate_initial_strain(self, time: float, curr: OsuDifficultyObject, objects: list[OsuDifficultyObject]) -> float:
        prev_start_time = objects[curr.idx - 1].start_time if curr.idx > 0 else 0.0
        decay = self.STRAIN_DECAY_BASE ** ((time - prev_start_time) / 1000.0)
        return self.current_strain * decay

    def strain_value_at(self, curr: OsuDifficultyObject, objects: list[OsuDifficultyObject]) -> float:
        self.current_strain *= self.STRAIN_DECAY_BASE ** (curr.delta_time / 1000.0)
        self.current_strain += self.evaluator.evaluate_diff_of(curr, objects, self.has_hidden_mod) * self.SKILL_MULTIPLIER
        return self.current_strain

    def difficulty_value(self) -> float:
        return sum(self.strain_peaks)

    @staticmethod
    def difficulty_to_performance(difficulty: float) -> float:
        return 25.0 * (difficulty ** 2.0)


@dataclass(slots=True)
class OsuSkills:
    aim: Aim
    aim_no_sliders: Aim
    speed: Speed
    flashlight: Flashlight

    @classmethod
    def new(cls, mods: GameMods, scaling_factor: ScalingFactor, great_hit_window: float, time_preempt: float) -> "OsuSkills":
        hit_window = 2.0 * great_hit_window

        HD_FADE_IN_DURATION_MULTIPLIER = 0.4
        PREEMPT_MIN = 450.0

        if mods.hd:
            time_fade_in = time_preempt * HD_FADE_IN_DURATION_MULTIPLIER
        else:
            time_fade_in = 400.0 * min(time_preempt / PREEMPT_MIN, 1.0)

        return cls(
            aim=Aim(include_sliders=True),
            aim_no_sliders=Aim(include_sliders=False),
            speed=Speed(hit_window=hit_window, has_autopilot_mod=mods.ap),
            flashlight=Flashlight.new(mods, scaling_factor.radius, time_preempt, time_fade_in)
        )

    def process(self, curr: OsuDifficultyObject, objects: list[OsuDifficultyObject]) -> None:
        self.aim.process(curr, objects)
        self.aim_no_sliders.process(curr, objects)
        self.speed.process(curr, objects)
        self.flashlight.process(curr, objects)
