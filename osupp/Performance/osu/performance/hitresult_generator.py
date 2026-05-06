import math
from dataclasses import dataclass
from typing import Optional, Tuple

from ...any.any import HitResultPriority
from ..osu import OsuHitResults, OsuScoreOrigin

@dataclass(slots=True)
class InspectOsuPerformance:
    total_hits: int
    misses: int
    acc: Optional[float] = None
    n300: Optional[int] = None
    n100: Optional[int] = None
    n50: Optional[int] = None
    large_tick_hits: int = 0
    small_tick_hits: int = 0
    slider_end_hits: int = 0
    origin: OsuScoreOrigin = OsuScoreOrigin.STABLE
    priority: HitResultPriority = HitResultPriority.BEST_CASE

    def tick_scores(self) -> Tuple[int, int]:
        if self.origin == OsuScoreOrigin.STABLE:
            return 0, 0

        elif self.origin == OsuScoreOrigin.WITH_SLIDER_ACC:
            score = 150 * self.slider_end_hits + 30 * self.large_tick_hits + 10 * self.small_tick_hits
            return score, score

        return 0, 0


class HitResultGenerator:
    @staticmethod
    def generate_ignore_accuracy(inspect: InspectOsuPerformance) -> OsuHitResults:
        remain = inspect.total_hits - inspect.misses

        n300 = min(inspect.n300 if inspect.n300 is not None else remain, remain)
        remain -= n300

        n100 = min(inspect.n100 if inspect.n100 is not None else remain, remain)
        remain -= n100

        n50 = min(inspect.n50 if inspect.n50 is not None else remain, remain)
        remain -= n50

        if remain > 0:
            if inspect.priority == HitResultPriority.BEST_CASE:
                n300 += remain
            elif inspect.priority == HitResultPriority.WORST_CASE:
                n50 += remain
            else:
                n300 += remain

        return OsuHitResults(
            n300,
            n100,
            n50,
            inspect.misses,
            inspect.large_tick_hits,
            inspect.small_tick_hits,
            inspect.slider_end_hits
        )

    @staticmethod
    def generate_closest(inspect: InspectOsuPerformance) -> OsuHitResults:
        if inspect.acc is None:
            return HitResultGenerator.generate_ignore_accuracy(inspect)

        remain = inspect.total_hits - inspect.misses
        if remain == 0:
            return HitResultGenerator.generate_ignore_accuracy(inspect)

        tick_score, tick_max = inspect.tick_scores()
        target_total = inspect.acc * float(300 * inspect.total_hits + tick_max)

        best_n300, best_n100, best_n50 = 0, 0, 0
        min_error = float('inf')

        start_n300 = min(remain, inspect.n300) if inspect.n300 is not None else remain
        end_n300 = inspect.n300 if inspect.n300 is not None else 0

        for n300 in range(start_n300, end_n300 - 1, -1):
            rem = remain - n300
            rem_score = target_total - (300.0 * n300) - tick_score

            n100_exact = (rem_score - 50.0 * rem) / 50.0
            n100 = int(round(max(0.0, min(float(rem), n100_exact))))

            if inspect.n100 is not None:
                n100 = inspect.n100

            n50 = rem - n100

            if inspect.n50 is not None:
                n50 = inspect.n50
                n100 = rem - n50

            current_score = 300 * n300 + 100 * n100 + 50 * n50 + tick_score
            error = abs(target_total - current_score)

            if error < min_error:
                min_error = error
                best_n300, best_n100, best_n50 = n300, n100, n50

            if min_error == 0:
                break

        return OsuHitResults(
            best_n300,
            best_n100,
            best_n50,
            inspect.misses,
            inspect.large_tick_hits,
            inspect.small_tick_hits,
            inspect.slider_end_hits
        )

    @staticmethod
    def generate_fast(inspect: InspectOsuPerformance) -> OsuHitResults:
        if inspect.acc is None:
            return HitResultGenerator.generate_ignore_accuracy(inspect)

        remain = inspect.total_hits - inspect.misses
        if remain == 0:
            return HitResultGenerator.generate_ignore_accuracy(inspect)

        tick_score, tick_max = inspect.tick_scores()
        target_total = inspect.acc * float(300 * inspect.total_hits + tick_max)

        n300 = int(target_total / 300.0)
        n300 = min(n300, remain)

        rem = remain - n300
        rem_score = target_total - (300.0 * n300) - tick_score

        n100 = int(rem_score / 100.0)
        n100 = max(0, min(rem, n100))

        n50 = rem - n100

        if inspect.n300 is not None: n300 = inspect.n300
        if inspect.n100 is not None: n100 = inspect.n100
        if inspect.n50 is not None: n50 = inspect.n50

        n50 = remain - n300 - n100
        if n50 < 0:
            n100 += n50
            n50 = 0
        if n100 < 0:
            n300 += n100
            n100 = 0

        return OsuHitResults(
            n300,
            n100,
            n50,
            inspect.misses,
            inspect.large_tick_hits,
            inspect.small_tick_hits,
            inspect.slider_end_hits
        )

    