from typing import List
from osupp.Beatmap.section.hit_objects.hit_objects import HitObject, HitObjectSlider, HitObjectSpinner


def _calculate_spinner_score(spinner: HitObjectSpinner) -> int:
    SPIN_SCORE = 100
    BONUS_SPIN_SCORE = 1000
    MAXIMUM_ROTATIONS_PER_SECOND = 477.0 / 60.0
    MINIMUM_ROTATIONS_PER_SECOND = 3.0

    seconds_duration = spinner.duration / 1000.0

    total_half_spins_possible = int(seconds_duration * MAXIMUM_ROTATIONS_PER_SECOND * 2.0)
    half_spins_required_for_completion = int(seconds_duration * MINIMUM_ROTATIONS_PER_SECOND)
    half_spins_required_before_bonus = half_spins_required_for_completion + 3

    score = 0
    full_spins = total_half_spins_possible // 2
    score += SPIN_SCORE * full_spins

    bonus_spins = (total_half_spins_possible - half_spins_required_before_bonus) // 2
    bonus_spins = max(bonus_spins - (full_spins // 2), 0)

    score += BONUS_SPIN_SCORE * bonus_spins

    return score


class InnerNestedScorePerObject:
    def __init__(self):
        self.n_sliders = 0
        self.n_repeats = 0
        self.amount_of_small_ticks = 0
        self.spinner_score = 0.0
        self.object_count = 0

    def process_next(self, h: HitObject) -> None:
        self.object_count += 1

        if isinstance(h.kind, HitObjectSlider):
            self.n_sliders += 1
            self.n_repeats += h.kind.repeat_count

            nested_objects = getattr(h.kind, "nested_objects", [])
            ticks = sum(1 for nested in nested_objects if getattr(nested, "kind", None) == "Tick")

            self.amount_of_small_ticks += ticks

        elif isinstance(h.kind, HitObjectSpinner):
            self.spinner_score += _calculate_spinner_score(h.kind)

    def calculate(self) -> float:
        if self.object_count == 0:
            return 0.0
        BIG_TICK_SCORE = 30.0
        SMALL_TICK_SCORE = 10.0

        amount_of_big_ticks = self.n_sliders * 2
        amount_of_big_ticks += self.n_repeats

        slider_score = (float(amount_of_big_ticks) * BIG_TICK_SCORE) + (float(self.amount_of_small_ticks) * SMALL_TICK_SCORE)

        return float(slider_score + self.spinner_score) / float(self.object_count)


class NestedScorePerObject:
    @staticmethod
    def calculate(objects: List[HitObject], passed_objects: int) -> float:
        inner = InnerNestedScorePerObject()

        limit = min(len(objects), passed_objects)
        for i in range(limit):
            inner.process_next(objects[i])

        return inner.calculate()


class GradualNestedScorePerObject:
    def __init__(self):
        self.inner = InnerNestedScorePerObject()

    def calculate_next(self, h: HitObject) -> float:
        self.inner.process_next(h)
        return self.inner.calculate()