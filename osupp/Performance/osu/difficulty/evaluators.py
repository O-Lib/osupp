import math
from typing import List, Optional

from .difficulty import OsuDifficultyObject
from ...utils.util import lerp, reverse_lerp, smoothstep, milliseconds_to_bpm, bpm_to_milliseconds


class AimEvaluator:
    WIDE_ANGLE_MULTIPLIER = 1.5
    ACUTE_ANGLE_MULTIPLIER = 2.55
    SLIDER_MULTIPLIER = 1.35
    VELOCITY_CHANGE_MULTIPLIER = 0.75
    WIGGLE_MULTIPLIER = 1.02

    @classmethod
    def evaluate_diff_of(cls, curr: OsuDifficultyObject, diff_objects: List[OsuDifficultyObject], with_slider_travel_dist: bool) -> float:
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