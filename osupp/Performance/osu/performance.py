import math
from typing import Optional
from collections.abc import Callable

from osupp.Beatmap.beatmap import Beatmap
from osupp.Beatmap.section.enums import GameMode
from osupp.Mods.game_mods import GameMods

from ..any.any import HitResultPriority, ScoreState
from ..any.difficulty import Difficulty
from ..utils.util import clamp, logistic, reverse_lerp, smoothstep
from .difficulty.skills import Aim, Flashlight, Speed
from .hitresult_generator import OsuFastGenerator


def erf(x: float) -> float:
    return math.erf(x)

def erf_inv(x: float) -> float:
    x_clamped = clamp(x, -0.99999, 0.99999)
    a = 8.0 * (math.pi - 3.0) / (3.0 * math.pi * (4.0 - math.pi))
    y = math.log(1.0 - x_clamped * x_clamped)
    z = 2.0 / (math.pi * a) + y / 2.0

    inner_sqrt = math.sqrt(max(0.0, z*z - y/a))
    res = math.sqrt(max(0.0, inner_sqrt - z))

    if x < 0:
        return -res
    return res


PERFORMANCE_BASE_MULTIPLIER = 1.14

class OsuPerformanceAttributes:
    def __init__(self):
        self.difficulty = None
        self.pp_acc = 0.0
        self.pp_aim = 0.0
        self.pp_flashlight = 0.0
        self.pp_speed = 0.0
        self.pp = 0.0
        self.effective_miss_count = 0.0
        self.speed_deviation = 0.0
        self.combo_based_estimated_miss_count = 0.0
        self.score_based_estimated_miss_count = None
        self.aim_estimated_slider_breaks = 0.0
        self.speed_estimated_slider_breaks = 0.0


class InspectOsuPerformance:
    def __init__(self, attrs, difficulty: Difficulty, perf_instance):
        self.attrs = attrs
        self.difficulty = difficulty
        self.acc = perf_instance.acc
        self.combo = perf_instance.combo
        self.large_tick_hits = perf_instance.large_tick_hits
        self.small_tick_hits = perf_instance.small_tick_hits
        self.slider_end_hits = perf_instance.slider_end_hits
        self.n300 = perf_instance.n300
        self.n100 = perf_instance.n100
        self.n50 = perf_instance.n50
        self.misses_val = perf_instance.misses
        self.hitresult_priority = perf_instance.hitresult_priority

    def total_hits(self) -> int:
        passed = getattr(self.difficulty, "passed_objects", None)
        if passed is None:
            passed = int(1e9)
        n_objs = getattr(self.attrs, "n_objects", lambda: getattr(self.attrs, "n_circles", 0) + getattr(self.attrs, "n_sliders", 0) + getattr(self.attrs, "n_spinners", 0))()
        return min(passed, n_objs)

    def misses(self) -> int:
        if self.misses_val is not None:
            return min(self.misses_val, self.total_hits())
        return 0

    def lazer(self) -> bool:
        return getattr(self.difficulty, "_lazer", True)

    def using_classic_slider_acc(self) -> bool:
        return getattr(self.difficulty, "_mods", GameMods()).contains_acronym("CL")

    def tick_scores(self) -> tuple[int, int, int]:
        return (0, 0)

    def tick_hits(self) -> tuple[int, int, int]:
        return (0, 0, 0)


class OsuPerformanceCalculator:
    def __init__(
            self,
            attrs,
            mods: GameMods,
            acc: float,
            state: ScoreState,
            using_classic_slider_acc: bool
    ):
        self.attrs = attrs
        self.mods = mods
        self.acc = acc
        self.state = state
        self.using_classic_slider_acc = using_classic_slider_acc

    def calculate(self) -> "OsuPerformanceAttributes":
        total_hits_val = self.total_hits()

        if total_hits_val == 0.0:
            result = OsuPerformanceAttributes()
            result.difficulty = self.attrs
            return result

        combo_based_estimated_miss_count = self.calculate_combo_based_estimated_miss_count()
        score_based_estimated_miss_count = None

        if self.using_classic_slider_acc and self.state.legacy_total_score is not None:
            effective_miss_count = combo_based_estimated_miss_count
        else:
            effective_miss_count = combo_based_estimated_miss_count

        effective_miss_count = max(effective_miss_count, float(self.state.misses))
        effective_miss_count = min(effective_miss_count, total_hits_val)

        multiplier = PERFORMANCE_BASE_MULTIPLIER

        if self.mods.contains_acronym("NF"):
            multiplier *= max(0.9, 1.0 - 0.02 * effective_miss_count)

        if self.mods.contains_acronym("SO") and total_hits_val > 0.0:
            spinner_ratio = float(getattr(self.attrs, "n_spinners", 0)) / total_hits_val
            multiplier *= 1.0 - math.pow(spinner_ratio, 0.85)

        if self.mods.contains_acronym("RX"):
            od = getattr(self.attrs, "od", 0.0)

            if od > 0.0:
                n100_mult = 0.75 * max(0.0, 1.0 - od / 13.33)
                n50_mult = max(0.0, 1.0 - math.pow(od / 13.33, 5.0))
            else:
                n100_mult = 1.0
                n50_mult = 1.0

            rx_misses = effective_miss_count + (float(self.state.n100) * n100_mult) + (float(self.state.n50) * n50_mult)
            effective_miss_count = min(rx_misses, total_hits_val)

        speed_deviation = self.calculate_speed_deviation()

        aim_estimated_slider_breaks = [0.0]
        speed_estimated_slider_breaks = [0.0]

        aim_value = self.compute_aim_value(effective_miss_count, aim_estimated_slider_breaks)
        speed_value = self.compute_speed_value(speed_deviation, effective_miss_count, speed_estimated_slider_breaks)
        acc_value = self.compute_accuracy_value()
        flashlight_value = self.compute_flashlight_value(effective_miss_count)

        pp = math.pow(
            math.pow(aim_value, 1.1) +
            math.pow(speed_value, 1.1) +
            math.pow(acc_value, 1.1) +
            math.pow(flashlight_value, 1.1),
            1.0 / 1.1
        ) * multiplier

        res = OsuPerformanceAttributes()
        res.difficulty = self.attrs
        res.pp_aim = aim_value
        res.pp_acc = acc_value
        res.pp_speed = speed_value
        res.pp_flashlight = flashlight_value
        res.pp = pp
        res.effective_miss_count = effective_miss_count
        res.speed_deviation = speed_deviation if speed_deviation is not None else 0.0
        res.combo_based_estimated_miss_count = combo_based_estimated_miss_count
        res.score_based_estimated_miss_count = score_based_estimated_miss_count
        res.aim_estimated_slider_breaks = aim_estimated_slider_breaks[0]
        res.speed_estimated_slider_breaks = speed_estimated_slider_breaks[0]

        return res

    def compute_aim_value(self, effective_miss_count: float, aim_estimated_slider_breaks: list) -> float:
        if self.mods.contains_acronym("AP"):
            return 0.0

        aim_difficulty = getattr(self.attrs, "aim", 0.0)

        n_sliders = getattr(self.attrs, "n_sliders", 0)
        aim_difficult_slider_count = getattr(self.attrs, "aim_difficult_slider_count", 0.0)

        if n_sliders > 0 and aim_difficult_slider_count > 0.0:
            if self.using_classic_slider_acc:
                maximum_possible_dropped_sliders = self.total_imperfect_hits()
                estimated_improperly_followed = clamp(
                    min(
                        maximum_possible_dropped_sliders,
                        float(getattr(self.attrs, "max_combo", 0) - self.state.max_combo)
                    ),
                    0.0,
                    aim_difficult_slider_count
                )
            else:
                estimated_improperly_followed = clamp(
                    float(self.n_slider_ends_dropped() + self.n_large_tick_miss()),
                    0.0,
                    aim_difficult_slider_count
                )

            slider_factor = getattr(self.attrs, "slider_factor", 1.0)
            slider_nerf_factor = (1.0 - slider_factor) * math.pow(
                1.0 - estimated_improperly_followed / aim_difficult_slider_count,
                3.0
            ) + slider_factor

            aim_difficulty *= slider_nerf_factor

        aim_value = Aim.difficulty_to_performance(aim_difficulty)

        total_hits_val = self.total_hits()

        len_bonus = 0.95 + 0.4 * min(total_hits_val / 2000.0, 1.0) + \
                    (1.0 if total_hits_val > 2000.0 else 0.0) * math.log10(total_hits_val / 2000.0) * 0.5

        aim_value *= len_bonus

        if effective_miss_count > 0.0:
            aim_estimated_slider_breaks[0] = self.calculate_estimated_slider_breaks(
                getattr(self.attrs, "aim_top_weighted_slider_factor", 0.0),
                effective_miss_count
            )

            relevant_miss_count = min(
                effective_miss_count + aim_estimated_slider_breaks[0],
                self.total_imperfect_hits() + float(self.n_large_tick_miss())
            )

            aim_value *= self.calculate_miss_penalty(
                relevant_miss_count,
                getattr(self.attrs, "aim_difficult_strain_count", 0.0)
            )

        if self.mods.contains_acronym("BL"):
            hp = getattr(self.attrs, "hp", 0.0)
            aim_value *= 1.3 + (total_hits_val * (0.0016 / (1.0 + 2.0 * effective_miss_count)) * math.pow(self.acc, 16.0)) * (1.0 - 0.003 * hp * hp)

        elif self.mods.contains_acronym("TC"):
            ar = getattr(self.attrs, "ar", 10.0)
            sf = getattr(self.attrs, "slider_factor", 1.0)

            is_always_partially_visible = self.mods.contains_acronym("HD") or self.mods.contains_acronym("TC")
            reading_bonus = 0.04 * (12.0 - max(ar, 7.0))
            slider_visibility_factor = math.pow(sf, 3.0)

            if ar < 7.0:
                factor = 0.03 if is_always_partially_visible else 0.045
                reading_bonus += factor * (1.0 - math.pow(1.5, ar)) * slider_visibility_factor
            elif ar < 0.0:
                factor = 0.075 if is_always_partially_visible else 0.1
                reading_bonus += factor * (1.0 - math.pow(1.5, ar)) * slider_visibility_factor

            aim_value *= 1.0 + reading_bonus

        aim_value *= self.acc

        return aim_value

    def compute_speed_value(self, speed_deviation: float | None, effective_miss_count: float, speed_estimated_slider_breaks: list) -> float:
        if speed_deviation is None or self.mods.contains_acronym("RX"):
            return 0.0

        speed_value = Speed.difficulty_to_performance(getattr(self.attrs, "speed", 0.0))

        total_hits_val = self.total_hits()

        len_bonus = 0.95 + 0.4 * min(total_hits_val / 2000.0, 1.0) + \
                    (1.0 if total_hits_val > 2000.0 else 0.0) * math.log10(total_hits_val / 2000.0) * 0.5

        speed_value *= len_bonus

        if effective_miss_count > 0.0:
            speed_estimated_slider_breaks[0] = self.calculate_estimated_slider_breaks(
                getattr(self.attrs, "speed_top_weighted_slider_factor", 0.0),
                effective_miss_count
            )

            relevant_miss_count = min(
                effective_miss_count + speed_estimated_slider_breaks[0],
                self.total_imperfect_hits() + float(self.n_large_tick_miss())
            )

            speed_value *= self.calculate_miss_penalty(
                relevant_miss_count,
                getattr(self.attrs, "speed_difficult_strain_count",  0.0)
            )

        if self.mods.contains_acronym("BL"):
            speed_value *= 1.12
        elif self.mods.contains_acronym("TC"):
            ar = getattr(self.attrs, "ar", 10.0)
            is_always_partially_visible = self.mods.contains_acronym("HD") or self.mods.contains_acronym("TC")
            reading_bonus = 0.04 * (12.0 - max(ar, 7.0))
            if ar < 7.0:
                factor = 0.03 if is_always_partially_visible else 0.045
                reading_bonus += factor * (1.0 - math.pow(1.5, ar))
            if ar < 0.0:
                factor = 0.075 if is_always_partially_visible else 1.0
                reading_bonus += factor * (1.0 - math.pow(1.5, ar))

            speed_value *= 1.0 + reading_bonus

        speed_high_deviation_mult = self.calculate_speed_high_deviation_nerf(speed_deviation)
        speed_value *= speed_high_deviation_mult

        speed_note_count = getattr(self.attrs, "speed_note_count", 0.0)
        relevant_total_diff = max(0.0, total_hits_val - speed_note_count)

        relevant_n300 = max(0.0, float(self.state.n300) - relevant_total_diff)
        relevant_n100 = max(0.0, float(self.state.n100) - max(0.0, relevant_total_diff - float(self.state.n300)))
        relevant_n50 = max(0.0, float(self.state.n50) - max(0.0, relevant_total_diff - float(self.state.n300 + self.state.n100)))

        if speed_note_count == 0.0:
            relevant_acc = 0.0
        else:
            relevant_acc = (relevant_n300 * 6.0 + relevant_n100 * 2.0 + relevant_n50) / (speed_note_count * 6.0)

        od = getattr(self.attrs, "od", 0.0)
        speed_value *= math.pow((self.acc + relevant_acc) / 2.0, (14.5 - od) / 2.0)

        return speed_value

    def compute_accuracy_value(self) -> float:
        if self.mods.contains_acronym("RX"):
            return 0.0

        amount_hit_objects_with_acc = getattr(self.attrs, "n_circles", 0)

        if not self.using_classic_slider_acc:
            amount_hit_objects_with_acc += getattr(self.attrs, "n_sliders", 0)

        if amount_hit_objects_with_acc > 0:
            diff = max(self.state.total_hits(GameMode.Osu) - amount_hit_objects_with_acc, 0)
            adjusted_n300 = self.state.n300 - diff
            better_acc_percentage = float(adjusted_n300 * 6 + self.state.n100 * 2 + self.state.n50) / float(amount_hit_objects_with_acc * 6)
        else:
            better_acc_percentage = 0.0

        if better_acc_percentage < 0.0:
            better_acc_percentage = 0.0

        od = getattr(self.attrs, "od", 0.0)
        acc_value = math.pow(1.52163, od) * math.pow(better_acc_percentage, 24.0) * 2.83

        acc_value *= min(math.pow(float(amount_hit_objects_with_acc) / 1000.0, 0.3), 1.15)

        if self.mods.contains_acronym("BL"):
            acc_value *= 1.14
        elif self.mods.contains_acronym("HD") or self.mods.contains_acronym("TC"):
            ar = getattr(self.attrs, "ar", 10.0)
            acc_value *= 1.0 + 0.08 * reverse_lerp(ar, 11.5, 10.0)

        if self.mods.contains_acronym("FL"):
            acc_value *= 1.02

        return acc_value

    def compute_flashlight_value(self, effective_miss_count: float) -> float:
        if not self.mods.contains_acronym("FL"):
            return 0.0

        flashlight_value = Flashlight.difficulty_to_performance(getattr(self.attrs, "flashlight", 0.0))
        total_hits_val = self.total_hits()

        if effective_miss_count > 0.0:
            flashlight_value *= 0.97 * math.pow(
                1.0 - math.pow(effective_miss_count / total_hits_val, 0.775),
                math.pow(effective_miss_count, 0.875)
            )

        flashlight_value *= self.get_combo_scaling_factor()
        flashlight_value *= 0.5 + self.acc / 2.0

        return flashlight_value

    def calculate_combo_based_estimated_miss_count(self) -> float:
        n_sliders = getattr(self.attrs, "n_sliders", 0)
        if n_sliders == 0:
            return float(self.state.misses)

        miss_count = float(self.state.misses)
        max_combo_attr = getattr(self.attrs, "max_combo", 0)

        if self.using_classic_slider_acc:
            full_combo_threshold = float(max_combo_attr) - 0.1 * float(n_sliders)

            if float(self.state.max_combo) < full_combo_threshold:
                miss_count = full_combo_threshold / max(1.0, float(self.state.max_combo))

            miss_count = min(miss_count, self.total_imperfect_hits())

            max_possible_slider_breaks = min(n_sliders, max(0, max_combo_attr - self.state.max_combo) // 2)

            slider_breaks = miss_count - float(self.state.misses)

            if slider_breaks > float(max_possible_slider_breaks):
                miss_count = float(self.state.misses + max_possible_slider_breaks)
        else:
            full_combo_threshold = float(max_combo_attr - self.n_slider_ends_dropped())

            if float(self.state.max_combo) < full_combo_threshold:
                miss_count = full_combo_threshold / max(1.0, float(self.state.max_combo))

            miss_count = min(miss_count, float(self.n_large_tick_miss() + self.state.misses))

        return miss_count

    def calculate_estimated_slider_breaks(self, top_weighted_slider_factor: float, effective_miss_count: float) -> float:
        if not self.using_classic_slider_acc or self.state.n100 == 0:
            return 0.0

        max_combo_attr = getattr(self.attrs, "max_combo", 1)
        missed_combo_percent = 1.0 - float(self.state.max_combo) / float(max_combo_attr)

        estimated_slider_breaks = min(effective_miss_count * top_weighted_slider_factor, float(self.state.n100))

        ok_adjustment = ((float(self.state.n100) - estimated_slider_breaks) + 0.5) / float(self.state.n100)

        estimated_slider_breaks *= smoothstep(effective_miss_count, 1.0, 2.0)

        return estimated_slider_breaks * ok_adjustment * logistic(missed_combo_percent, 0.33, 15.0, 1.0)

    def calculate_speed_deviation(self) -> float | None:
        if self.total_successful_hits() == 0:
            return None

        speed_note_count = getattr(self.attrs, "speed_note_count", 0.0)
        speed_note_count += (float(self.state.total_hits(GameMode.Osu)) - speed_note_count) * 0.1

        relevant_count_miss = min(float(self.state.misses), speed_note_count)
        relevant_count_meh = min(float(self.state.n50), speed_note_count - relevant_count_miss)
        relevant_count_ok = min(float(self.state.n100), speed_note_count - relevant_count_miss - relevant_count_meh)
        relevant_count_great = max(0.0, speed_note_count - relevant_count_miss - relevant_count_meh - relevant_count_ok)

        return self.calculate_deviation(relevant_count_great, relevant_count_ok, relevant_count_meh)

    def calculate_deviation(self, relevant_count_great: float, relevant_count_ok: float, relevant_count_meh: float) -> float | None:
        if relevant_count_great + relevant_count_ok + relevant_count_meh <= 0.0:
            return None

        n = max(1.0, relevant_count_great + relevant_count_ok)
        p = relevant_count_great / n

        Z = 2.32634787404

        p_lower_bound = min(
            p,
            ((n * p +  Z * Z / 2.0) / (n + Z * Z) - Z / (n + Z * Z) * math.sqrt(n * p * (1.0 - p) + Z * Z / 4.0))
        )

        great_hit_window = getattr(self.attrs, "great_hit_window", 0.0)
        ok_hit_window = getattr(self.attrs, "ok_hit_window", 0.0)
        meh_hit_window = getattr(self.attrs, "meh_hit_window", 0.0)

        if p_lower_bound > 0.01:
            deviation = great_hit_window / (math.sqrt(2.0) * erf_inv(p_lower_bound))

            ok_hit_window_tail_amount = math.sqrt(2.0 / math.pi) * ok_hit_window * math.exp(-0.5 * math.pow(ok_hit_window / deviation, 2.0)) \
                / (deviation * erf(ok_hit_window / (math.sqrt(2.0) * deviation)))

            deviation *= math.sqrt(1.0 - ok_hit_window_tail_amount)
        else:
            deviation = ok_hit_window / math.sqrt(3.0)

        meh_variance = (meh_hit_window * meh_hit_window + ok_hit_window * meh_hit_window + ok_hit_window * ok_hit_window) / 3.0

        deviation = math.sqrt(
            ((relevant_count_great + relevant_count_ok) * math.pow(deviation, 2.0) + relevant_count_meh * meh_variance) /
            (relevant_count_great + relevant_count_ok + relevant_count_meh)
        )

        return deviation

    def calculate_speed_high_deviation_nerf(self, speed_deviation: float) -> float:
        speed_value = Speed.difficulty_to_performance(getattr(self.attrs, "speed", 0.0))

        excess_speed_difficulty_cutoff = 100.0 + 220.0 * math.pow(22.0 / speed_deviation, 6.5)

        if speed_value <= excess_speed_difficulty_cutoff:
            return 1.0

        SCALE = 50.0

        adjusted_speed_value = SCALE * (
            math.log((speed_value - excess_speed_difficulty_cutoff) / SCALE + 1.0) +
            excess_speed_difficulty_cutoff / SCALE
        )

        lerp_val = 1.0 - reverse_lerp(speed_deviation, 22.0, 27.0)
        adjusted_speed_value = (adjusted_speed_value * (1.0 - lerp_val)) + (speed_value * lerp_val)

        return adjusted_speed_value / speed_value

    @staticmethod
    def calculate_miss_penalty(miss_count: float, diff_strain_count: float) -> float:
        if diff_strain_count <= 0.0:
            return 1.0
        return 0.96 / ((miss_count / (4.0 * math.pow(math.log(diff_strain_count), 0.94))) + 1.0)

    def get_combo_scaling_factor(self) -> float:
        max_combo_attr = getattr(self.attrs, "max_combo", 0)
        if max_combo_attr == 0:
            return 1.0

        return min(
            1.0,
            math.pow(float(self.state.max_combo), 0.8) / math.pow(float(max_combo_attr), 0.8)
        )

    def total_hits(self) -> float:
        return float(self.state.total_hits(GameMode.Osu))

    def total_successful_hits(self) -> int:
        return self.state.n300 + self.state.n100 + self.state.n50

    def total_imperfect_hits(self) -> float:
        return float(self.state.n100 + self.state.n50 + self.state.misses)

    def n_slider_ends_dropped(self) -> int:
        n_sliders = getattr(self.attrs, "n_sliders", 0)
        return max(0, n_sliders - self.state.slider_end_hits)

    def n_large_tick_miss(self) -> int:
        if self.using_classic_slider_acc:
            return 0
        n_large_ticks = getattr(self.attrs, "n_large_ticks", 0)
        return max(0, n_large_ticks - self.state.osu_large_tick_hits)


class OsuPerformance:
    def __init__(self, map_or_attrs):
        self.map_or_attrs = map_or_attrs
        self.difficulty = Difficulty()
        self.acc: float | None = None
        self.combo: int | None = None
        self.large_tick_hits: int | None = None
        self.small_tick_hits: int | None = None
        self.slider_end_hits: int | None = None
        self.n300: int | None = None
        self.n100: int | None = None
        self.n50: int | None = None
        self.misses: int | None = None
        self.legacy_total_score: int | None = None
        self.hitresult_priority = HitResultPriority.BEST_CASE
        self.hitresult_generator = None

    def mods(self, mods: GameMods) -> "OsuPerformance":
        self.difficulty = self.difficulty.mods(mods)
        return self

    def set_combo(self, combo: int) -> "OsuPerformance":
        self.combo = combo
        return self

    def set_hitresult_priority(self, priority: HitResultPriority) -> "OsuPerformance":
        self.hitresult_priority = priority
        return self

    def set_hitresult_generator(self, generator: Callable) -> "OsuPerformance":
        self.hitresult_generator = generator
        return self

    def set_lazer(self, lazer: bool) -> "OsuPerformance":
        self.difficulty = self.difficulty.lazer(lazer)
        return self

    def set_large_tick_hits(self, large_tick_hits: int) -> "OsuPerformance":
        self.large_tick_hits = large_tick_hits
        return self

    def set_small_tick_hits(self, small_tick_hits: int) -> "OsuPerformance":
        self.small_tick_hits = small_tick_hits
        return self

    def set_slider_end_hits(self, slider_end_hits: int) -> "OsuPerformance":
        self.slider_end_hits = slider_end_hits
        return self

    def set_n300(self, n300: int) -> "OsuPerformance":
        self.n300 = n300
        return self

    def set_n100(self, n100: int) -> "OsuPerformance":
        self.n100 = n100
        return self

    def set_n50(self, n50: int) -> "OsuPerformance":
        self.n50 = n50
        return self

    def set_misses(self, n_misses: int) -> "OsuPerformance":
        self.misses = n_misses
        return self

    def set_difficulty(self, difficulty: Difficulty) -> "OsuPerformance":
        self.difficulty = difficulty
        return self

    def passed_objects(self, passed_objects: int) -> "OsuPerformance":
        self.difficulty = self.difficulty.passed_objects(passed_objects)
        return self

    def clock_rate(self, clock_rate: float) -> "OsuPerformance":
        self.difficulty = self.difficulty.clock_rate(clock_rate)
        return self

    def set_legacy_total_score(self, legacy_total_score: int) -> "OsuPerformance":
        self.legacy_total_score = legacy_total_score
        return self

    def set_state(self, state: ScoreState) -> "OsuPerformance":
        self.combo = state.max_combo
        self.legacy_total_score = state.legacy_total_score
        self.large_tick_hits = state.osu_large_tick_hits
        self.small_tick_hits = state.osu_small_tick_hits
        self.slider_end_hits = state.slider_end_hits
        self.n300 = state.n300
        self.n100 = state.n100
        self.n50 = state.n50
        self.misses = state.misses
        return self

    def accuracy(self, acc: float) -> "OsuPerformance":
        self.acc = clamp(acc, 0.0, 100.0) / 100.0
        return self

    def generate_state(self) -> ScoreState:
        attrs = self.map_or_attrs
        inspect = InspectOsuPerformance(attrs, self.difficulty, self)

        if self.hitresult_generator is not None:
            hitresults = self.hitresult_generator(inspect)
        else:
            hitresults = OsuFastGenerator.generate_hitresults(inspect)

        total_hits = inspect.total_hits()
        remain = max(0, total_hits - hitresults.total_hits(GameMode.Osu))

        if self.hitresult_priority == HitResultPriority.BEST_CASE:
            if self.n300 is None:
                hitresults.n300 += remain
            elif self.n100 is None:
                hitresults.n100 += remain
            elif self.n50 is None:
                hitresults.n50 += remain
            else:
                hitresults.n300 += remain
        else:
            if self.n50 is None:
                hitresults.n50 += remain
            elif self.n100 is None:
                hitresults.n100 += remain
            elif self.n300 is None:
                hitresults.n300 += remain
            else:
                hitresults.n50 += remain

        misses = inspect.misses()
        max_possible_combo = max(0, getattr(attrs, "max_combo", 0) - misses)

        max_combo = min(self.combo, max_possible_combo) if self.combo is not None else max_possible_combo
        self.combo = max_combo

        self.slider_end_hits = hitresults.slider_end_hits
        self.large_tick_hits = hitresults.osu_large_tick_hits
        self.small_tick_hits = hitresults.osu_small_tick_hits
        self.n300 = hitresults.n300
        self.n100 = hitresults.n100
        self.n50 = hitresults.n50
        self.misses = hitresults.misses

        state = ScoreState()
        state.max_combo = max_combo
        state.osu_large_tick_hits = hitresults.osu_large_tick_hits
        state.osu_small_tick_hits = hitresults.osu_small_tick_hits
        state.slider_end_hits = hitresults.slider_end_hits
        state.n300 = hitresults.n300
        state.n100 = hitresults.n100
        state.n50 = hitresults.n50
        state.misses = hitresults.misses
        state.legacy_total_score = self.legacy_total_score
        return state

    def checked_generate_state(self) -> "ScoreState":
        return self.generate_state()

    def calculate(self) -> "OsuPerformanceAttributes":
        state = self.generate_state()
        attrs = self.map_or_attrs

        mods = getattr(self.difficulty, "_mods", GameMods())
        lazer = getattr(self.difficulty, "_lazer", True)
        using_classic_slider_acc = mods.contains_acronym("CL")

        inner = OsuPerformanceCalculator(attrs, mods, self.acc if self.acc is not None else 1.0, state, using_classic_slider_acc)
        return inner.calculate()

    def checked_calculate(self) -> "OsuPerformanceAttributes":
        state = self.checked_generate_state()
        attrs = self.map_or_attrs

        mods = getattr(self.difficulty, "_mods", GameMods())
        lazer = getattr(self.difficulty, "_lazer", True)
        using_classic_slider_acc = mods.contains_acronym("CL")

        inner = OsuPerformanceCalculator(attrs, mods, self.acc if self.acc is not None else 1.0, state, using_classic_slider_acc)
        return inner.calculate()


class OsuGradualPerformance:
    def __init__(self, difficulty: Difficulty, map_data: Beatmap):
        self.lazer = getattr(difficulty, "_lazer", True)
        self.difficulty = difficulty
        self.map_data = map_data

    @classmethod
    def checked_new(cls, difficulty: Difficulty, map_data: Beatmap) -> "OsuGradualPerformance":
        if hasattr(map_data, "check_suspicion"):
            map_data.check_suspicion()
        return cls(difficulty, map_data)

    def next(self, state: ScoreState) -> OsuPerformanceAttributes | None:
        return self.nth(state, 0)

    def last(self, state: ScoreState) -> OsuPerformanceAttributes | None:
        return self.nth(state, int(1e9))

    def nth(self, state: ScoreState, n: int) -> OsuPerformanceAttributes | None:
        return None

    def len(self) -> int:
        return 0
