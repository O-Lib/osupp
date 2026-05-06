from dataclasses import dataclass, field


def calculate_spinner_score(spinner) -> float:
    SPIN_SCORE = 100
    BONUS_SPIN_SCORE = 1000

    MAXIMUM_ROTATIONS_PER_SECOND = 477.0 / 60.0
    MINIMUM_ROTATIONS_PER_SECOND = 3.0

    seconds_duration = spinner.duration / 1000.0

    total_half_spins_possible = int(seconds_duration * MAXIMUM_ROTATIONS_PER_SECOND * 2.0)
    half_spins_required_for_completion = int(seconds_duration * MINIMUM_ROTATIONS_PER_SECOND)
    half_spins_required_before_bonus = half_spins_required_for_completion * 3

    score = 0
    full_spins = total_half_spins_possible // 2

    score += SPIN_SCORE * full_spins
    bonus_spins = (total_half_spins_possible - half_spins_required_before_bonus) // 2
    bonus_spins = max(bonus_spins - (full_spins // 2), 0)

    score += BONUS_SPIN_SCORE * bonus_spins

    return float(score)


@dataclass(slots=True)
class InnerNestedScorePerObject:
    n_sliders: int =  0
    n_repeats: int = 0
    amount_of_small_ticks: int = 0
    spinner_score: float = 0.0
    object_count: int = 0

    def process_next(self, h) -> None:
        self.object_count += 1

        if getattr(h, "is_circle", False):
            pass
        elif getattr(h, "is_slider", False):
            self.n_sliders += 1
            self.n_repeats += getattr(h, "repeat_count", lambda: 0)()
            self.amount_of_small_ticks += getattr(h, "tick_count", lambda: 0)()
        elif getattr(h, "is_spinner", False):
            self.spinner_score += calculate_spinner_score(h.kind)

    def calculate(self) -> float:
        if self.object_count == 0:
            return 0.0

        BIG_TICK_SCORE = 30.0
        SMALL_TICK_SCORE = 10.0

        amount_of_big_ticks = (self.n_sliders * 2) + self.n_repeats

        slider_score = (amount_of_big_ticks * BIG_TICK_SCORE) + (self.amount_of_small_ticks * SMALL_TICK_SCORE)

        return (slider_score + self.spinner_score) / float(self.object_count)


class NestedScorePerObject:
    @staticmethod
    def calculate(objects: list, passed_objects: int) -> float:
        inner = InnerNestedScorePerObject()
        for h in objects[:passed_objects]:
            inner.process_next(h)
        return inner.calculate()


@dataclass(slots=True)
class GradualNestedScorePerObject:
    _inner: InnerNestedScorePerObject = field(default_factory=InnerNestedScorePerObject)

    def calculate_next(self, h) -> float:
        self._inner.process_next(h)
        return self._inner.calculate()
