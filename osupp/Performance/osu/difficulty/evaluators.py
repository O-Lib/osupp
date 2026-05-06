import math
from dataclasses import dataclass

from ...utils.utils import (
    bpm_to_milliseconds,
    clamp,
    logistic,
    milliseconds_to_bpm,
    reverse_lerp,
    smootherstep,
    smoothstep,
    smoothstep_bell_curve,
)
from .difficulty import OsuDifficultyObject


def _get_previous(idx: int, steps_back: int, diff_objects: list[OsuDifficultyObject]) -> OsuDifficultyObject | None:
    pos = idx - 1 - steps_back
    if pos >= 0:
        return diff_objects[pos]
    return None

def _get_next(idx: int, steps_forwards: int, diff_objects: list[OsuDifficultyObject]) -> OsuDifficultyObject | None:
    pos = idx + 1 + steps_forwards
    if pos < len(diff_objects):
        return diff_objects[pos]
    return None


class AimEvaluator:
    WIDE_ANGLE_MULTIPLIER = 1.5
    ACUTE_ANGLE_MULTIPLIER = 2.55
    SLIDER_MULTIPLIER = 1.35
    VELOCITY_CHANGE_MULTIPLIER = 0.75
    WIGGLE_MULTIPLIER = 1.02

    @staticmethod
    def evaluate_diff_of(curr: OsuDifficultyObject, diff_objects: list[OsuDifficultyObject], with_slider_travel_dist: bool) -> float:
        osu_curr_obj = curr

        osu_last_obj = _get_previous(curr.idx, 0, diff_objects)
        osu_last_last_obj = _get_previous(curr.idx, 1, diff_objects)

        if not osu_last_obj or not osu_last_last_obj:
            return 0.0

        if getattr(curr.base.kind, "is_spinner", False) or getattr(osu_last_obj.base.kind, "is_spinner", False):
            return 0.0

        RADIUS = OsuDifficultyObject.NORMALIZED_RADIUS
        DIAMETER = OsuDifficultyObject.NORMALIZED_RADIUS * 2

        curr_vel = osu_curr_obj.lazy_jump_dist / osu_curr_obj.adjusted_delta_time

        if getattr(osu_last_obj.base.kind, "is_slider", False) and with_slider_travel_dist:
            travel_vel = osu_last_obj.travel_dist / max(1e-10, osu_last_obj.travel_time)
            movement_vel = osu_curr_obj.min_jump_dist / max(1e-10, osu_curr_obj.min_jump_time)
            curr_vel = max(curr_vel, movement_vel + travel_vel)

        prev_vel = osu_last_obj.lazy_jump_dist / osu_last_obj.adjusted_delta_time

        if getattr(osu_last_obj.base.kind, "is_slider", False) and with_slider_travel_dist:
            travel_vel = osu_last_last_obj.travel_dist / max(1e-10, osu_last_last_obj.travel_time)
            movement_vel = osu_last_obj.min_jump_dist / max(1e-10, osu_last_obj.min_jump_time)
            prev_vel = max(prev_vel, movement_vel + travel_vel)

        wide_angle_bonus = 0.0
        acute_angle_bonus = 0.0
        slider_bonus = 0.0
        vel_change_bonus = 0.0
        wiggle_bonus = 0.0

        aim_strain = curr_vel

        if osu_curr_obj.angle is not None and osu_last_obj.angle is not None:
            curr_angle = osu_curr_obj.angle
            last_angle = osu_last_obj.angle

            angle_bonus = min(curr_vel, prev_vel)

            min_delta = min(osu_curr_obj.adjusted_delta_time, osu_last_obj.adjusted_delta_time)
            max_delta = max(osu_curr_obj.adjusted_delta_time, osu_last_obj.adjusted_delta_time)

            if max_delta < 1.25 * min_delta:
                acute_angle_bonus = AimEvaluator.calc_acute_angle_bonus(curr_angle)
                acute_angle_bonus *= 0.08 + 0.92 * (1.0 - min(acute_angle_bonus, AimEvaluator.calc_acute_angle_bonus(last_angle) ** 3.0))

                acute_angle_bonus *= (angle_bonus * smootherstep(milliseconds_to_bpm(osu_curr_obj.adjusted_delta_time, 2), 300.0, 400.0) *
                                      smootherstep(osu_curr_obj.lazy_jump_dist, float(DIAMETER), float(DIAMETER * 2)))

            wide_angle_bonus = AimEvaluator.calc_wide_angle_bonus(curr_angle)
            wide_angle_bonus *= 1.0 - min(wide_angle_bonus, AimEvaluator.calc_wide_angle_bonus(last_angle) ** 3.0)
            wide_angle_bonus *= angle_bonus * smootherstep(osu_curr_obj.lazy_travel_dist, 0.0, float(DIAMETER))

            wiggle_bonus = (angle_bonus * smootherstep(osu_curr_obj.lazy_jump_dist, float(RADIUS), float(DIAMETER)) * (reverse_lerp(osu_curr_obj.lazy_jump_dist, float(DIAMETER * 3), float(DIAMETER)) ** 1.8) *
                            smootherstep(curr_angle, math.radians(110.0), math.radians(60.0)) *
                            smootherstep(osu_last_obj.lazy_jump_dist, float(RADIUS), float(DIAMETER)) *
                            (reverse_lerp(osu_last_obj.lazy_jump_dist, float(DIAMETER * 3), float(DIAMETER)) ** 1.8) *
                            smootherstep(last_angle, math.radians(110.0), math.radians(60.0)))

            osu_last_2_obj = _get_previous(curr.idx, 2, diff_objects)
            if osu_last_2_obj:
                distance = (osu_last_2_obj.base.stacked_pos - osu_last_obj.base.stacked_pos).length()
                if distance < 1.0:
                    wide_angle_bonus *= 1.0 - 0.35 * (1.0 - distance)

        if max(prev_vel, curr_vel) != 0.0:
            prev_vel = (osu_last_obj.lazy_jump_dist + osu_last_last_obj.travel_dist) / max(1e-10, osu_last_obj.adjusted_delta_time)
            curr_vel = (osu_curr_obj.lazy_jump_dist + osu_last_obj.travel_dist) / max(1e-10, osu_curr_obj.adjusted_delta_time)

            max_vel = max(prev_vel, curr_vel)
            dist_ratio = smoothstep(abs(prev_vel - curr_vel) / max_vel if max_vel > 0 else 0.0, 0.0, 1.0)

            overlap_vel_buff = min(float(DIAMETER) * 1.25 / min(osu_curr_obj.adjusted_delta_time, osu_last_obj.adjusted_delta_time). abs(prev_vel - curr_vel))
            vel_change_bonus = overlap_vel_buff * dist_ratio

            bonus_base = min(osu_curr_obj.adjusted_delta_time, osu_last_obj.adjusted_delta_time) / max(osu_curr_obj.adjusted_delta_time, osu_last_obj.adjusted_delta_time)
            vel_change_bonus *= bonus_base ** 2.0

        if getattr(osu_last_obj.base.kind, "is_slider", False):
            slider_bonus = osu_last_obj.travel_dist / max(1e-10, osu_last_obj.travel_time)

        aim_strain += wiggle_bonus * AimEvaluator.WIGGLE_MULTIPLIER
        aim_strain += vel_change_bonus * AimEvaluator.VELOCITY_CHANGE_MULTIPLIER
        aim_strain += max(acute_angle_bonus * AimEvaluator.ACUTE_ANGLE_MULTIPLIER,
                          wide_angle_bonus * AimEvaluator.WIDE_ANGLE_MULTIPLIER)
        aim_strain *= osu_curr_obj.small_circle_bonus

        if with_slider_travel_dist:
            aim_strain += slider_bonus, AimEvaluator.SLIDER_MULTIPLIER

        return aim_strain

    @staticmethod
    def calc_wide_angle_bonus(angle: float) -> float:
        return smoothstep(angle, math.radians(40.0), math.radians(140.0))

    @staticmethod
    def calc_acute_angle_bonus(angle: float) -> float:
        return smoothstep(angle, math.radians(140.0), math.radians(40.0))


class FlashlightEvaluator:
    MAX_OPACITY_BONUS = 0.4
    HIDDEN_BONUS = 0.2
    MIN_VELOCITY = 0.5
    SLIDER_MULTIPLIER = 1.3
    MIN_ANGLE_MULTIPLIER = 0.2

    __slots__ = ("scaling_factor", "time_preempt", "time_fade_in")

    def __init__(self, scaling_factor: float, time_preempt: float, time_fade_in: float):
        self.scaling_factor = scaling_factor
        self.time_preempt = time_preempt
        self.time_fade_in = time_fade_in

    def evaluate_diff_of(self, curr: OsuDifficultyObject, diff_objects: list[OsuDifficultyObject], hidden: bool) -> float:
        if getattr(curr.base.kind, "is_spinner", False):
            return 0.0

        osu_curr = curr
        osu_hit_obj = curr.base

        small_dist_nerf = 1.0
        cumulative_strain_time = 0.0
        result = 0.0
        angle_repeat_count = 0.0
        last_obj = osu_curr

        lookback_limit = min(curr.idx, 10)
        for i in range(lookback_limit):
            curr_obj = _get_previous(curr.idx, i, diff_objects)
            if not curr_obj:
                break

            cumulative_strain_time += last_obj.adjusted_delta_time
            curr_hit_obj = curr_obj.base

            if not getattr(curr_hit_obj.kind, "is_spinner", False):
                jump_dist = (osu_hit_obj.stacked_pos - curr_hit_obj.stacked_end_pos).length()

                if i == 0:
                    small_dist_nerf = min(jump_dist / 75.0, 1.0)

                stack_nerf = min(((curr_obj.lazy_jump_dist / self.scaling_factor) / 25.0), 1.0)

                opacity = getattr(osu_curr, "opacity_at", lambda t, h, p, f: 1.0)(curr_obj.start_time, hidden, self.time_preempt, self.time_fade_in)
                opacity_bonus = 1.0 + self.MAX_OPACITY_BONUS * (1.0 - opacity)

                result += stack_nerf * opacity_bonus * self.scaling_factor * jump_dist / max(1e-10, cumulative_strain_time)

                if curr_obj.angle is not None and osu_curr.angle is not None:
                    if abs(curr_obj.angle - osu_curr.angle) < 0.02:
                        angle_repeat_count += max(1.0 - 0.1 * i, 0.0)

            last_obj = curr_obj

        result = (small_dist_nerf * result) ** 2.0

        if hidden:
            result *= 1.0 + self.HIDDEN_BONUS

        result *= self.MIN_ANGLE_MULTIPLIER + (1.0 - self.MIN_ANGLE_MULTIPLIER) / (angle_repeat_count + 1.0)

        slider_bonus = 0.0
        if getattr(osu_curr.base.kind, "is_slider", False):
            pixel_travel_dist = osu_curr.lazy_travel_dist / self.scaling_factor
            slider_bonus = max(pixel_travel_dist / max(1e-10, osu_curr.travel_time) - self.MIN_VELOCITY, 0.0) ** 0.5
            slider_bonus *= pixel_travel_dist

            repeat_count = getattr(osu_curr.base.kind, "repeat_count", lambda: 0)()
            if repeat_count > 0:
                slider_bonus /= (repeat_count + 1)

        result += slider_bonus * self.SLIDER_MULTIPLIER
        return result


class SpeedEvaluator:
    SINGLE_SPACING_THRESHOLD = 125.0
    MIN_SPEED_BONUS = 200.0
    SPEED_BALACING_FACTOR = 40.0
    DIST_MULTIPLIER = 0.8

    @staticmethod
    def evaluate_diff_of(curr: OsuDifficultyObject, diff_objects: list[OsuDifficultyObject], hit_window: float, autopilot: bool) -> float:
        if getattr(curr.base.kind, "is_spinner", False):
            return 0.0

        osu_curr_obj = curr
        osu_prev_obj = _get_previous(curr.idx, 0, diff_objects)
        osu_next_obj = _get_next(curr.idx, 0, diff_objects)

        strain_time = curr.adjusted_delta_time

        doubletapness = 1.0 - getattr(osu_curr_obj, "get_doubletapness", lambda n, hw: 0.0)(osu_next_obj, hit_window)

        strain_time /= clamp((strain_time / hit_window) / 0.93, 0.92, 1.0)

        speed_bonus = 0.0
        if milliseconds_to_bpm(strain_time, None) > SpeedEvaluator.MIN_SPEED_BONUS:
            base = (bpm_to_milliseconds(SpeedEvaluator.MIN_SPEED_BONUS, None) - strain_time) / SpeedEvaluator.SPEED_BALACING_FACTOR
            speed_bonus = 0.75 * (base ** 2.0)

        travel_dist = osu_prev_obj.travel_dist if osu_prev_obj else 0.0
        dist = travel_dist + osu_curr_obj.min_jump_dist
        dist = min(SpeedEvaluator.SINGLE_SPACING_THRESHOLD, dist)

        dist_bonus = ((dist / SpeedEvaluator.SINGLE_SPACING_THRESHOLD) ** 3.95) * SpeedEvaluator.DIST_MULTIPLIER
        dist_bonus *= math.sqrt(osu_curr_obj.small_circle_bonus)

        if autopilot:
            dist_bonus = 0.0

        difficulty = (1.0 + speed_bonus + dist_bonus) * 1000.0 / strain_time
        return difficulty * doubletapness


@dataclass(slots=True, eq=True)
class RhythmIsland:
    delta_difference_eps: float
    delta: int = 0
    delta_count: int = 0

    @classmethod
    def new(cls, delta_difference_eps: float) -> "RhythmIsland":
        return cls(delta_difference_eps, 0, 0)

    @classmethod
    def new_with_delta(cls, delta: int, delta_difference_eps: float) -> "RhythmIsland":
        return cls(delta_difference_eps, max(delta, 25), 1)

    def add_delta(self, delta: int):
        if self.delta == 0 or self.delta == 2147483647:
            self.delta = max(delta, 25)
        self.delta_count += 1

    def is_similar_polarity(self, other: "RhythmIsland") -> bool:
        return (self.delta_count % 2) == (other.delta_count % 2)

    def is_default(self) -> bool:
        return abs(self.delta_difference_eps) < 1e-7 and (self.delta == 0 or self.delta == 2147483647) and self.delta_count == 0


class RhythmEvaluator:
    HISTORY_TIME_MAX = 5000
    HISTORY_OBJECTS_MAX = 32
    RHYTHM_OVERALL_MULTIPLIER = 1.0
    RHYTHM_RATIO_MULTIPLIER = 15.0

    @staticmethod
    def evaluate_diff_of(curr: OsuDifficultyObject, diff_objects: list[OsuDifficultyObject], hit_window: float) -> float:
        if getattr(curr.base.kind, "is_spinner", False):
            return 0.0

        rhythm_complexity_sum = 0.0
        delta_difference_eps = hit_window * 0.3

        island = RhythmIsland.new(delta_difference_eps)
        prev_island = RhythmIsland.new(delta_difference_eps)
        island_counts: list[tuple[RhythmIsland, int]] = []

        start_ratio = 0.0
        first_delta_switch = False
        historical_note_count = min(curr.idx, RhythmEvaluator.HISTORY_OBJECTS_MAX)
        rhythm_start = 0

        while True:
            prev = _get_previous(curr.idx, rhythm_start, diff_objects)
            if prev and rhythm_start + 2 < historical_note_count and (curr.start_time - prev.start_time < RhythmEvaluator.HISTORY_TIME_MAX):
                rhythm_start += 1
            else:
                break

        prev_obj = _get_previous(curr.idx, rhythm_start, diff_objects)
        last_obj = _get_previous(curr.idx, rhythm_start + 1, diff_objects)

        if prev_obj and last_obj:
            for i in range(rhythm_start, 0, -1):
                curr_obj = _get_previous(curr.idx, i - 1, diff_objects)
                if not curr_obj:
                    break

                time_decay = (RhythmEvaluator.HISTORY_TIME_MAX - (curr.start_time - curr_obj.start_time)) / RhythmEvaluator.HISTORY_TIME_MAX
                note_decay = (historical_note_count - i) / historical_note_count
                curr_historical_decay = min(note_decay, time_decay)

                curr_delta = max(curr_obj.delta_time, 1e-7)
                prev_delta = max(prev_obj.delta_time, 1e-7)
                last_delta = max(last_obj.delta_time, 1e-7)

                delta_difference = max(prev_delta, curr_delta) / min(prev_delta, curr_delta)
                delta_difference_fraction = delta_difference - int(delta_difference)

                curr_ratio = 1.0 + RhythmEvaluator.RHYTHM_RATIO_MULTIPLIER * min(smoothstep_bell_curve(delta_difference_fraction, 0.5, 0.5), 0.5)
                difference_multiplier = clamp(2.0 - delta_difference / 8.0, 0.0, 1.0)
                window_penalty = min(max(abs(prev_delta - curr_delta) - delta_difference_eps, 0.0) / delta_difference_eps, 1.0)

                effective_ratio = window_penalty * curr_ratio * difference_multiplier

                if first_delta_switch:
                    if abs(prev_delta - curr_delta) < delta_difference_eps:
                        island.add_delta(int(curr_delta))
                    else:
                        if getattr(curr_obj.base.kind, "is_slider", False):
                            effective_ratio *= 0.125
                        if getattr(prev_obj.base.kind, "is_slider", False):
                            effective_ratio *= 0.3
                        if island.is_similar_polarity(prev_island):
                            effective_ratio *= 0.5
                        if last_delta > prev_delta + delta_difference_eps and prev_delta > curr_delta + delta_difference_eps:
                            effective_ratio *= 0.125
                        if prev_island.delta_count == island.delta_count:
                            effective_ratio *= 0.5

                        found = False
                        for idx_island, (isl, count) in enumerate(island_counts):
                            if isl == island and not isl.is_default():
                                found = True
                                new_count = count + 1 if prev_island == island else count
                                island_counts[idx_island] = (isl, new_count)

                                power = logistic(float(island.delta), 58.33, 0.24, 2.75)
                                effective_ratio *= min(3.0 / new_count, (1.0 / new_count) ** power)
                                break

                        if not found:
                            island_counts.append((island, 1))

                        doubletapness = getattr(prev_obj, "get_doubletapness", lambda n, hw: 0.0)(curr_obj, hit_window)
                        effective_ratio *= 1.0 - doubletapness * 0.75

                        rhythm_complexity_sum += math.sqrt(effective_ratio * start_ratio) * curr_historical_decay
                        start_ratio = effective_ratio
                        prev_island = island

                        if prev_delta + delta_difference_eps < curr_delta:
                            first_delta_switch = False

                        island = RhythmIsland.new_with_delta(int(curr_delta), delta_difference_eps)

                elif prev_delta > curr_delta + delta_difference_eps:
                    first_delta_switch = True
                    if getattr(curr_obj.base.kind, "is_slider", False):
                        effective_ratio *= 0.6
                    if getattr(prev_obj.base.kind, "is_slider", False):
                        effective_ratio *= 0.6
                    start_ratio = effective_ratio
                    island = RhythmIsland.new_with_delta(int(curr_delta), delta_difference_eps)

                last_obj = prev_obj
                prev_obj = curr_obj

        rhythm_difficulty = math.sqrt(4.0 + rhythm_complexity_sum * RhythmEvaluator.RHYTHM_OVERALL_MULTIPLIER) / 2.0
        doubletapness_curr = getattr(curr, "get_doubletapness", lambda n, hw: 0.0)(_get_next(curr.idx, 0, diff_objects), hit_window)
        rhythm_difficulty *= 1.0 - doubletapness_curr

        return rhythm_difficulty
