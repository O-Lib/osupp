import math
from typing import Any, Optional, Tuple

from ..any.any import HitResultPriority, ScoreState


class OsuIgnoreAccuracyGenerator:
    @classmethod
    def generate_hitresults(cls, inspect: Any) -> ScoreState:
        large_tick_hits = getattr(inspect, "large_tick_hits", 0) or 0
        small_tick_hits = getattr(inspect, "small_tick_hits", 0) or 0
        slider_end_hits = getattr(inspect, "slider_end_hits", 0) or 0

        total_hits = inspect.total_hits()
        misses = getattr(inspect, "misses", 0) or 0
        remain = total_hits - misses

        def assign_specified(specified: int | None) -> int | None:
            nonlocal remain
            if specified is None:
                return None
            assigned = min(specified, remain)
            remain -= assigned
            return assigned

        priority = getattr(inspect, "hitresult_priority", HitResultPriority.BEST_CASE)

        if priority == HitResultPriority.BEST_CASE:
            n300 = assign_specified(getattr(inspect, "n300", None))
            n100 = assign_specified(getattr(inspect, "n100", None))
            n50 = assign_specified(getattr(inspect, "n50", None))

            if n300 is None:
                n300 = remain
                remain = 0
            if n100 is None:
                n100 = remain
                remain = 0
            if n50 is None:
                n50 = remain
                remain = 0

            if remain > 0:
                n300 += remain

        else:
            n50 = assign_specified(getattr(inspect, "n50", None))
            n100 = assign_specified(getattr(inspect, "n100", None))
            n300 = assign_specified(getattr(inspect, "n300", None))

            if n50 is None:
                n50 = remain
                remain = 0
            if n100 is None:
                n100 = remain
                remain = 0
            if n300 is None:
                n300 = remain
                remain = 0

            if remain > 0:
                n50 += remain

        state = ScoreState()
        state.n300 = n300
        state.n100 = n100
        state.n50 = n50
        state.misses = misses
        state.osu_large_tick_hits = large_tick_hits
        state.osu_small_tick_hits = small_tick_hits
        state.slider_end_hits = slider_end_hits

        return state


class OsuFastGenerator:
    @classmethod
    def generate_hitresults(cls, inspect: Any) -> ScoreState:
        acc = getattr(inspect, "accuracy", None)
        if acc is None:
            return OsuIgnoreAccuracyGenerator.generate_hitresults(inspect)

        large_tick_hits = getattr(inspect, "large_tick_hits", 0) or 0
        small_tick_hits = getattr(inspect, "small_tick_hits", 0) or 0
        slider_end_hits = getattr(inspect, "slider_end_hits", 0) or 0

        total_hits = inspect.total_hits()
        misses = getattr(inspect, "misses", 0) or 0
        remain = total_hits - misses

        if remain == 0:
            state = ScoreState()
            state.n300 = 0
            state.n100 = 0
            state.n50 = 0
            state.misses = misses
            state.osu_large_tick_hits = large_tick_hits
            state.osu_small_tick_hits = small_tick_hits
            state.slider_end_hits = slider_end_hits
            return state

        tick_score, tick_max = inspect.tick_scores() if hasattr(inspect, "tick_scores") else (0, 0)

        insp_n300 = getattr(inspect, "n300", None)
        insp_n100 = getattr(inspect, "n100", None)
        insp_n50 = getattr(inspect, "n50", None)

        prelim_300 = min(insp_n300, remain) if insp_n300 is not None else 0
        prelim_100 = min(insp_n100, remain - prelim_300) if insp_n100 is not None else 0
        prelim_50 = min(insp_n50, remain - prelim_300 - prelim_100) if insp_n50 is not None else 0

        if insp_n300 is not None and insp_n100 is not None and insp_n50 is not None:
            n300, n100, n50 = prelim_300, prelim_100, prelim_50
        elif insp_n300 is not None and insp_n100 is not None and insp_n50 is None:
            n300, n100, n50 = prelim_300, prelim_100, remain - prelim_300 - prelim_100
        elif insp_n300 is not None and insp_n100 is None and insp_n50 is not None:
            n300, n100, n50 = prelim_300, remain - prelim_300 - prelim_50, prelim_50
        elif insp_n300 is None and insp_n100 is not None and insp_n50 is not None:
            n300, n100, n50 = remain - prelim_100 - prelim_50, prelim_100, prelim_50
        else:
            numerator = float(6 * prelim_300 + 2 * prelim_100 + prelim_50) + float(tick_score) / 50.0
            denominator = float(6 * total_hits) + float(tick_max) / 50.0

            target_total = int(round(max(0.0, acc * denominator - numerator)))

            baseline = remain - prelim_300 - prelim_100 - prelim_50
            delta = max(0, target_total - baseline)

            n300 = min(remain - prelim_100 - prelim_50, insp_n300 if insp_n300 is not None else delta // 5)

            if insp_n300 is None:
                delta = max(0, delta - 5 * n300)

            n100 = min(remain - n300 - prelim_50, insp_n100 if insp_n100 is not None else delta)
            n50 = min(remain - n300 - n100, insp_n50 if insp_n50 is not None else remain)

        state = ScoreState()
        state.n300 = n300
        state.n100 = n100
        state.n50 = n50
        state.misses = misses
        state.osu_large_tick_hits = large_tick_hits
        state.osu_small_tick_hits = small_tick_hits
        state.slider_end_hits = slider_end_hits

        total_hits_state = state.n300 + state.n100 + state.n50 + state.misses
        if total_hits_state < total_hits:
            left = total_hits - total_hits_state
            priority = getattr(inspect, "hitresult_priority", HitResultPriority.BEST_CASE)

            if priority == HitResultPriority.BEST_CASE:
                if insp_n300 is None:
                    state.n300 += left
                elif insp_n100 is None:
                    state.n100 += left
                else:
                    state.n50 += left
            else:
                if insp_n50 is None:
                    state.n50 += left
                elif insp_n100 is None:
                    state.n100 += left
                else:
                    state.n300 += left

        return state


class OsuClosestGenerator:
    @classmethod
    def _accuracy(cls, n300: int, n100: int, n50: int, total_hits: int, tick_score: int, tick_max: int) -> float:
        if total_hits == 0:
            return 0.0
        numerator = float(n300 * 300 + n100 * 100 + n50 * 50 + tick_score)
        denominator = float(total_hits * 300 + tick_max)
        return numerator / denominator

    @classmethod
    def generate_hitresults(cls, inspect: Any) -> ScoreState:
        acc = getattr(inspect, "accuracy", None)
        if acc is None:
            return OsuIgnoreAccuracyGenerator.generate_hitresults(inspect)

        large_tick_hits = getattr(inspect, "large_tick_hits", 0) or 0
        small_tick_hits = getattr(inspect, "small_tick_hits", 0) or 0
        slider_end_hits = getattr(inspect, "slider_end_hits", 0) or 0

        total_hits = inspect.total_hits()
        misses = getattr(inspect, "misses", 0) or 0
        remain = total_hits - misses

        tick_score, tick_max = inspect.tick_scores() if hasattr(inspect, "tick_scores") else (0, 0)
        target_total = acc * float(300 * total_hits + tick_max)

        insp_n300 = getattr(inspect, "n300", None)
        insp_n100 = getattr(inspect, "n100", None)
        insp_n50 = getattr(inspect, "n50", None)

        def compute_n100_n50(n300_val: int) -> tuple[int, int, int]:
            n300_clamped = min(n300_val, remain)
            raw100 = (target_total - float(50 * remain + 250 * n300_clamped + tick_score)) / 50.0

            rem = remain - n300_clamped
            min100 = min(rem, int(max(0.0, math.floor(raw100))))
            max100 = min(rem, int(max(0.0, math.ceil(raw100))))

            best_dist = float('inf')
            best_n100 = 0
            best_n50 = rem

            for new100 in range(min100, max100 + 1):
                new50 = rem - new100
                acc_val = cls._accuracy(n300_clamped, new100, new50, total_hits, tick_score, tick_max)
                dist = abs(acc - acc_val)

                if dist < best_dist:
                    best_dist = dist
                    best_n100 = new100
                    best_n50 = new50

            return n300_clamped, best_n100, best_n50

        def compute_n300_n50(n100_val: int) -> tuple[int, int, int]:
            n100_clamped = min(n100_val, remain)
            raw300 = (target_total - float(50 * remain + 50 * n100_clamped + tick_score)) / 250.0

            rem = remain - n100_clamped
            min300 = min(rem, int(max(0.0, math.floor(raw300))))
            max300 = min(rem, int(max(0.0, math.ceil(raw300))))

            best_dist = float('inf')
            best_n300 = 0
            best_n50 = rem

            for new300 in range(min300, max300 + 1):
                new50 = rem - new300
                acc_val = cls._accuracy(new300, n100_clamped, new50, total_hits, tick_score, tick_max)
                dist = abs(acc - acc_val)

                if dist < best_dist:
                    best_dist = dist
                    best_n300 = new300
                    best_n50 = new50

            return best_n300, n100_clamped, best_n50

        def compute_n300_n100(n50_val: int) -> tuple[int, int, int]:
            n50_clamped = min(n50_val, remain)
            raw300 = (target_total + float(50 * n50_clamped) - float(100 * remain + tick_score)) / 200.0

            rem = remain - n50_clamped
            min300 = min(rem, int(max(0.0, math.floor(raw300))))
            max300 = min(rem, int(max(0.0, math.ceil(raw300))))

            best_dist = float('inf')
            best_n300 = 0
            best_n100 = rem

            for new300 in range(min300, max300 + 1):
                new100 = rem - new300
                acc_val = cls._accuracy(new300, new100, n50_clamped, total_hits, tick_score, tick_max)
                dist = abs(acc - acc_val)

                if dist < best_dist:
                    best_dist = dist
                    best_n300 = new300
                    best_n100 = new100

            return best_n300, best_n100, n50_clamped

        if insp_n300 is not None and insp_n100 is not None and insp_n50 is not None:
            n300 = min(insp_n300, remain)
            n100 = min(insp_n100, remain - n300)
            n50 = min(insp_n50, remain - n300 - n100)
        elif insp_n300 is not None and insp_n100 is not None and insp_n50 is None:
            n300 = min(insp_n300, remain)
            n100 = min(insp_n100, remain - n300)
            n50 = remain - n300 - n100
        elif insp_n300 is not None and insp_n100 is None and insp_n50 is not None:
            n300 = min(insp_n300, remain)
            n50 = min(insp_n50, remain - n300)
            n100 = remain - n300 - n50
        elif insp_n300 is None and insp_n100 is not None and insp_n50 is not None:
            n100 = min(insp_n100, remain)
            n50 = min(insp_n50, remain - n100)
            n300 = remain - n100 - n50
        elif insp_n300 is not None and insp_n100 is None and insp_n50 is None:
            n300, n100, n50 = compute_n100_n50(insp_n300)
        elif insp_n300 is None and insp_n100 is not None and insp_n50 is None:
            n300, n100, n50 = compute_n300_n50(insp_n100)
        elif insp_n300 is None and insp_n100 is None and insp_n50 is not None:
            n300, n100, n50 = compute_n300_n100(insp_n50)
        else:
            raw_min300 = (target_total - float(50 * remain + tick_score)) / 250.0
            raw_max300 = (target_total - float(tick_score)) / 300.0

            min300 = int(max(0.0, math.floor(raw_min300)))
            max300 = min(remain, 1 + int(max(0.0, math.ceil(raw_max300))))

            best_dist = float('inf')
            n300, n100, n50 = 0, 0, remain

            for new300 in range(min300, max300 + 1):
                c_n300, c_n100, c_n50 = compute_n100_n50(new300)
                acc_val = cls._accuracy(c_n300, c_n100, c_n50, total_hits, tick_score, tick_max)
                dist = abs(acc - acc_val)

                if dist < best_dist:
                    best_dist = dist
                    n300, n100, n50 = c_n300, c_n100, c_n50

        state = ScoreState()
        state.n300 = n300
        state.n100 = n100
        state.n50 = n50
        state.misses = misses
        state.osu_large_tick_hits = large_tick_hits
        state.osu_small_tick_hits = small_tick_hits
        state.slider_end_hits = slider_end_hits

        return state
