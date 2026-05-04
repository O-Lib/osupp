import math
from typing import List

from ...utils import logistic
from ...utils.util import (
    bpm_to_milliseconds,
    milliseconds_to_bpm,
    reverse_lerp,
    smoothstep,
)
from .difficulty import OsuDifficultyObject


class AimEvaluator:
    WIDE_ANGLE_MULTIPLIER = 1.5
    ACUTE_ANGLE_MULTIPLIER = 2.55
    SLIDER_MULTIPLIER = 1.35
    VELOCITY_CHANGE_MULTIPLIER = 0.75
    WIGGLE_MULTIPLIER = 1.02

    @classmethod
    def evaluate_diff_of(cls, curr: OsuDifficultyObject, diff_objects: list[OsuDifficultyObject], with_slider_travel_dist: bool) -> float:
        if curr.idx < 2:
            return 0.0

        osu_curr_obj = curr
        osu_last_obj = diff_objects[curr.idx - 1]
        osu_last_last_obj = diff_objects[curr.idx - 2]

        if getattr(curr.base.kind, "duration", False) and not getattr(curr.base.kind, "path", False):
            return 0.0
        if getattr(osu_last_obj.base.kind, "duration", False) and not getattr(osu_last_obj.base.kind, "path", False):
            return 0.0

        RADIUS = OsuDifficultyObject.NORMALIZED_RADIUS
        DIAMETER = OsuDifficultyObject.NORMALIZED_DIAMETER

        curr_vel = osu_curr_obj.lazy_travel_dist / osu_curr_obj.adjusted_delta_time

        if hasattr(osu_last_obj.base.kind, "path") and with_slider_travel_dist:
            travel_vel = osu_last_obj.travel_dist / max(osu_last_obj.travel_time, 1e-7)
            movement_vel = osu_curr_obj.min_jump_dist / max(osu_curr_obj.min_jump_time, 1e-7)
            curr_vel = max(curr_vel, movement_vel + travel_vel)

        prev_vel = osu_last_obj.lazy_jump_dist / osu_last_obj.adjusted_delta_time

        if hasattr(osu_last_obj.base.kind, "path") and with_slider_travel_dist:
            travel_vel = osu_last_last_obj.travel_dist / max(osu_last_last_obj.travel_time, 1e-7)
            movement_vel = osu_last_obj.min_jump_dist / max(osu_last_obj.min_jump_time, 1e-7)
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

            if max(osu_curr_obj.adjusted_delta_time, osu_last_obj.adjusted_delta_time) < 1.25 * min(osu_curr_obj.adjusted_delta_time, osu_last_obj.adjusted_delta_time):
                acute_angle_bonus = cls.calc_acute_angle_bonus(curr_angle)
                acute_angle_bonus *= 0.08 + 0.92 * (1.0 - min(acute_angle_bonus, math.pow(cls.calc_acute_angle_bonus(last_angle), 3.0)))

                acute_angle_bonus *= angle_bonus * smoothstep(
                    milliseconds_to_bpm(osu_curr_obj.adjusted_delta_time, 2), 300.0, 400.0
                ) * smoothstep(
                    osu_curr_obj.lazy_jump_dist, float(DIAMETER), float(DIAMETER * 2)
                )

            wide_angle_bonus = cls.calc_wide_angle_bonus(curr_angle)
            wide_angle_bonus *= 1.0 - min(wide_angle_bonus, math.pow(cls.calc_wide_angle_bonus(last_angle), 3.0))
            wide_angle_bonus *= angle_bonus * smoothstep(osu_curr_obj.lazy_jump_dist, 0.0, float(DIAMETER))

            wiggle_bonus = angle_bonus * smoothstep(
                osu_curr_obj.lazy_jump_dist, float(RADIUS), float(DIAMETER)
            ) * math.pow(
                reverse_lerp(osu_curr_obj.lazy_jump_dist, float(DIAMETER * 3), float(DIAMETER)), 1.8
            ) * smoothstep(
                curr_angle, math.radians(110.0), math.radians(60.0)
            ) * smoothstep(
                osu_last_obj.lazy_travel_dist, float(RADIUS), float(DIAMETER)
            ) * math.pow(
                reverse_lerp(osu_last_obj.lazy_jump_dist, float(DIAMETER * 3), float(DIAMETER)), 1.8
            ) * smoothstep(
                last_angle, math.radians(110.0), math.radians(60.0)
            )

            if curr.idx >= 2:
                distance = (osu_last_last_obj.base.stacked_pos - osu_last_obj.base.stacked_pos).length()
                if distance < 1.0:
                    wide_angle_bonus *= 1.0 - 0.35 * (1.0 - distance)

        if max(prev_vel, curr_vel) > 1e-7:
            prev_vel = (osu_last_obj.lazy_jump_dist + osu_last_last_obj.travel_dist) / max(osu_last_obj.adjusted_delta_time, 1e-7)
            curr_vel = (osu_curr_obj.lazy_jump_dist + osu_last_obj.travel_dist) / max(osu_curr_obj.adjusted_delta_time, 1e-7)

            dist_ratio = smoothstep(abs(prev_vel - curr_vel) / max(prev_vel, curr_vel), 0.0, 1.0)
            overlap_vel_buff = min(
                float(DIAMETER) * 1.25 / max(min(osu_curr_obj.adjusted_delta_time, osu_last_obj.adjusted_delta_time), 1e-7),
                abs(prev_vel - curr_vel)
            )

            vel_change_bonus = overlap_vel_buff * dist_ratio

            bonus_base = min(osu_curr_obj.adjusted_delta_time, osu_last_obj.adjusted_delta_time) / max(osu_curr_obj.adjusted_delta_time, osu_last_obj.adjusted_delta_time)
            vel_change_bonus *= math.pow(bonus_base, 2.0)

        if hasattr(osu_last_obj.base.kind, "path"):
            slider_bonus = osu_last_obj.travel_dist / max(osu_last_obj.travel_time, 1e-7)

        aim_strain += wiggle_bonus * cls.WIGGLE_MULTIPLIER
        aim_strain += vel_change_bonus * cls.VELOCITY_CHANGE_MULTIPLIER
        aim_strain += max(acute_angle_bonus * cls.ACUTE_ANGLE_MULTIPLIER, wide_angle_bonus * cls.WIDE_ANGLE_MULTIPLIER)
        aim_strain += osu_curr_obj.small_circle_bonus

        if with_slider_travel_dist:
            aim_strain += slider_bonus * cls.SLIDER_MULTIPLIER

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

    def __init__(self, scaling_factor: float, time_preempt: float, time_fade_in: float):
        self.scaling_factor = scaling_factor
        self.time_preempt = time_preempt
        self.time_fade_in = time_fade_in

    def evaluate_diff_of(self, curr: OsuDifficultyObject, diff_objects: list[OsuDifficultyObject], hidden: bool) -> float:
        if getattr(curr.base.kind, "duration", False) and not hasattr(curr.base.kind, "path"):
            return 0.0

        osu_curr = curr
        osu_hit_obj = curr.base

        small_dist_nerf = 1.0
        cumulative_strain_time = 0.0
        result = 0.0
        last_obj = osu_curr
        angle_repeat_count = 0.0

        for i in range(min(curr.idx, 10)):
            curr_obj = diff_objects[curr.idx - 1 - i]
            cumulative_strain_time += last_obj.adjusted_delta_time
            curr_hit_obj = curr_obj.base

            if not (getattr(curr_obj.base.kind, "duration", False) and not hasattr(curr_obj.base.kind, "path")):
                curr_end_pos = getattr(curr_hit_obj, "stacked_end_pos", lambda: curr_hit_obj.stacked_pos)()
                jump_dist = (osu_hit_obj.stacked_pos - curr_end_pos).length()

                if i == 0:
                    small_dist_nerf = min(jump_dist / 75.0, 1.0)

                stack_nerf = min(((curr_obj.lazy_jump_dist / self.scaling_factor) / 25.0), 1.0)

                opacity_bonus = 1.0 + self.MAX_OPACITY_BONUS * (1.0 - osu_curr.opacity_at(
                    curr_hit_obj.start_time, hidden, self.time_preempt, self.time_fade_in
                ))

                result += stack_nerf * opacity_bonus * self.scaling_factor * jump_dist / max(cumulative_strain_time, 1e-7)

                if curr_obj.angle is not None and osu_curr.angle is not None:
                    if abs(curr_obj.angle - osu_curr.angle) < 0.02:
                        angle_repeat_count += max(1.0 - 0.1 * i, 0.0)

            last_obj = curr_obj

        result = math.pow(small_dist_nerf * result, 2.0)

        if hidden:
            result += 1.0 + self.HIDDEN_BONUS

        result *= self.MIN_ANGLE_MULTIPLIER + (1.0 - self.MIN_ANGLE_MULTIPLIER) / (angle_repeat_count + 1-0)

        slider_bonus = 0.0
        if hasattr(osu_curr.base.kind, "path"):
            pixel_travel_dist = osu_curr.lazy_travel_dist / self.scaling_factor
            slider_bonus = math.pow(max(pixel_travel_dist / max(osu_curr.travel_time, 1e-7) - self.MIN_VELOCITY, 0.0), 0.5)
            slider_bonus *= pixel_travel_dist

            repeat_count = osu_curr.base.kind.repeat_count

            if repeat_count > 0:
                slider_bonus /= (repeat_count + 1)

        result += slider_bonus * self.SLIDER_MULTIPLIER
        return result


class RhythmIsland:
    def __init__(self, delta_difference_eps: float, delta: int = 0, delta_count: int = 0):
        self.delta_difference_eps = delta_difference_eps
        self.delta = delta
        self.delta_count = delta_count

    @classmethod
    def new_with_delta(cls, delta: int, delta_difference_eps: float) -> "RhythmIsland":
        MIN_DELTA_TIME = 25
        return cls(delta_difference_eps, max(delta, MIN_DELTA_TIME), 1)

    def add_delta(self, delta: int):
        MIN_DELTA_TIME = 25
        if self.delta == 2147483647:
            self.delta = max(delta, MIN_DELTA_TIME)
        self.delta_count += 1

    def is_similar_polarity(self, other: "RhythmIsland") -> bool:
        return self.delta_count % 2 == other.delta_count % 2

    def is_default(self) -> bool:
        return abs(self.delta_difference_eps) <  1e-7 and self.delta == 2147483647 and self.delta_count == 0

    def __eq__(self, other):
        if not isinstance(other, RhythmIsland):
            return False
        return float(abs(self.delta, other.delta)) <  self.delta_difference_eps and self.delta_count == other.delta_count


def smoothstep_bell_curve(x: float, p: float, width: float) -> float:
    return math.pow(math.sin(math.pi * x), 2.0)


class RhythmEvaluator:
    HISTORY_TIME_MAX = 5000
    HISTORY_OBJECTS_MAX = 32
    RHYTHM_OVERALL_MULTIPLIER = 1.0
    RHYTHM_RATIO_MULTIPLIER = 15.0

    @classmethod
    def evaluate_diff_of(cls, curr: OsuDifficultyObject, diff_objects: list[OsuDifficultyObject], hit_window: float) -> float:
        if getattr(curr.base.kind, "duration", False) and not hasattr(curr.base.kind, "path"):
            return 0.0

        rhythm_complexity_sum = 0.0
        delta_difference_eps = hit_window * 0.3

        island = RhythmIsland(delta_difference_eps)
        prev_island = RhythmIsland(delta_difference_eps)

        island_counts = []
        start_ratio = 0.0
        first_delta_switch = False

        historical_note_count = min(curr.idx, cls.HISTORY_OBJECTS_MAX)
        rhythm_start = 0

        while rhythm_start + 2 < historical_note_count:
            prev = diff_objects[curr.idx - 1 - rhythm_start]
            if curr.start_time - prev.start_time >= float(cls.HISTORY_TIME_MAX):
                break
            rhythm_start += 1

        if curr.idx >= rhythm_start + 1:
            prev_obj = diff_objects[curr.idx - 1 - rhythm_start]
            last_obj = diff_objects[curr.idx - 2 - rhythm_start]

            for i in range(rhythm_start, 0, -1):
                curr_obj = diff_objects[curr.idx - i]

                time_decay = (float(cls.HISTORY_TIME_MAX) - (curr.start_time - curr_obj.start_time)) / float(cls.HISTORY_TIME_MAX)
                note_decay = float(historical_note_count - i) / float(historical_note_count)
                curr_historical_decay = min(note_decay, time_decay)

                curr_delta = max(curr_obj.delta_time, 1e-7)
                prev_delta = max(prev_obj.delta_time, 1e-7)
                last_delta = max(last_obj.delta_time, 1e-7)

                delta_difference = max(prev_delta, curr_delta) / min(prev_delta, curr_delta)
                delta_difference_fraction = delta_difference - int(delta_difference)

                curr_ratio = 1.0 + cls.RHYTHM_RATIO_MULTIPLIER * min(smoothstep_bell_curve(delta_difference_fraction, 0.5, 0.5), 0.5)

                difference_multiplier = max(0.0, min(2.0 - delta_difference / 8.0, 1.0))
                window_penalty = min(max((abs(prev_delta - curr_delta) - delta_difference_eps) / delta_difference_eps, 0.0), 1.0)

                effective_ratio = window_penalty * curr_ratio * difference_multiplier

                if first_delta_switch:
                    if abs(prev_delta - curr_delta) < delta_difference_eps:
                        island.add_delta(int(curr_delta))
                    else:
                        if hasattr(curr_obj.base.kind, "path"):
                            effective_ratio *= 0.125
                        if hasattr(prev_obj.base.kind, "path"):
                            effective_ratio *= 0.3
                        if island.is_similar_polarity(prev_island):
                            effective_ratio *= 0.5
                        if last_delta > prev_delta + delta_difference_eps and prev_delta > curr_delta +  delta_difference_eps:
                            effective_ratio *=0.125
                        if prev_island.delta_count == island.delta_count:
                            effective_ratio *= 0.5

                        found = False
                        for count_entry in island_counts:
                            if count_entry["island"] == island and not island.is_default():
                                if prev_island == island:
                                    count_entry["count"] += 1
                                power = logistic(float(island.delta), 58.33, 0.24, 2.75)
                                effective_ratio *= min(3.0 / float(count_entry["count"]), math.pow(1.0 / float(count_entry["count"]), power))
                                found = True
                                break

                        if not found:
                            island_counts.append({"island": island, "count": 1})

                        doubletapness = prev_obj.get_doubletapness(curr_obj, hit_window)
                        effective_ratio *= 1.0 - doubletapness * 0.75

                        rhythm_complexity_sum += math.sqrt(effective_ratio * start_ratio) * curr_historical_decay
                        start_ratio = effective_ratio
                        prev_island = island

                        if prev_delta + delta_difference_eps < curr_delta:
                            first_delta_switch = False

                        island = RhythmIsland.new_with_delta(int(curr_delta), delta_difference_eps)

                elif prev_delta > curr_delta +  delta_difference_eps:
                    first_delta_switch = True
                    if hasattr(curr_obj.base.kind, "path"):
                        effective_ratio *= 0.6
                    if hasattr(prev_obj.base.kind, "path"):
                        effective_ratio *= 0.6

                    start_ratio = effective_ratio
                    island = RhythmIsland.new_with_delta(int(curr_delta), delta_difference_eps)

                last_obj = prev_obj
                prev_obj = curr_obj

            next_obj = None
            if curr.idx + 1 < len(diff_objects):
                next_obj = diff_objects[curr.idx + 1]

            rhythm_difficulty = math.sqrt(4.0 + rhythm_complexity_sum * cls.RHYTHM_OVERALL_MULTIPLIER) / 2.0
            rhythm_difficulty *= 1.0 - curr.get_doubletapness(next_obj, hit_window)

            return rhythm_difficulty


class SpeedEvaluator:
    SINGLE_SPACING_THRESHOLD = OsuDifficultyObject.NORMALIZED_DIAMETER * 1.25
    MIN_SPEED_BONUS = 200.0
    SPEED_BALACING_FACTOR = 40.0
    DIST_MULTIPLIER = 0.8

    @classmethod
    def evaluate_diff_of(cls, curr: OsuDifficultyObject, diff_objects: list[OsuDifficultyObject], hit_window: float, autopilot: bool) -> float:
        if getattr(curr.base.kind, "duration", False) and not hasattr(curr.base.kind, "path"):
            return 0.0

        osu_curr_obj = curr
        osu_prev_obj = diff_objects[curr.idx - 1] if curr.idx > 0 else None

        next_obj = None
        if curr.idx + 1 < len(diff_objects):
            next_obj = diff_objects[curr.idx + 1]

        strain_time = curr.adjusted_delta_time
        doubletapness = 1.0 - osu_curr_obj.get_doubletapness(next_obj, hit_window)

        strain_time /= max(0.92, min((strain_time / hit_window) / 0.93, 1.0))

        speed_bonus = 0.0
        if milliseconds_to_bpm(strain_time, 4) > cls.MIN_SPEED_BONUS:
            base = (bpm_to_milliseconds(cls.MIN_SPEED_BONUS, 4) - strain_time) / cls.SPEED_BALACING_FACTOR
            speed_bonus = 0.75 * math.pow(base, 2.0)

        travel_dist = osu_prev_obj.travel_dist if osu_prev_obj else 0.0
        dist = min(travel_dist + osu_curr_obj.min_jump_dist, cls.SINGLE_SPACING_THRESHOLD)

        dist_bonus = math.pow(dist / cls.SINGLE_SPACING_THRESHOLD, 3.95) * cls.DIST_MULTIPLIER
        dist_bonus *= math.sqrt(osu_curr_obj.small_circle_bonus)

        if autopilot:
            dist_bonus = 0.0

        difficulty = (1.0 + speed_bonus + dist_bonus) * 1000.0 / strain_time
        return difficulty * doubletapness
