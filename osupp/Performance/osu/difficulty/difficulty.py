import math
from typing import Optional

from osupp.Mods.game_mods import GameMods
from ...utils.util import clamp, reverse_lerp, lerp

class ScalingFactor:
    def __init__(self, cs: float):
        self.scale = (1.0 - 0.7 * ((cs - 5.0) / 5.0)) / 2.0 * 1.00041
        self.radius = 64.0 * self.scale
        self.factor = 50.0 / self.radius

    def stack_offset(self, stack_height: int):
        offset = stack_height * self.scale * -6.4
        from osupp.Beatmap.utils import Pos
        return Pos(offset, offset)


class OsuDifficultyObject:
    NORMALIZED_RADIUS = 50
    NORMALIZED_DIAMETER = 100
    MIN_DELTA_TIME = 25.0
    MAX_SLIDER_RADIUS = 50 * 2.4
    ASSUMED_SLIDER_RADIUS = 50 * 1.8

    def __init__(
            self,
            hit_object,
            last_object,
            last_diff_obj,
            last_last_diff_obj,
            clock_rate,
            idx,
            scaling_factor
    ):
        self.idx = idx
        self.base = hit_object
        self.start_time = hit_object.start_time / clock_rate
        self.delta_time = (hit_object.start_time - last_object.start_time) / clock_rate
        self.adjusted_delta_time = max(self.delta_time, self.MIN_DELTA_TIME)

        self.lazy_jump_dist = 0.0
        self.lazy_jump_dist = 0.0
        self.min_jump_dist = 0.0
        self.min_jump_time = 0.0
        self.travel_dist = 0.0
        self.travel_time = 0.0
        self.lazy_end_pos = None
        self.lazy_travel_dist = 0.0
        self.lazy_travel_time = 0.0
        self.angle = None

        self.small_circle_bonus = max(1.0, 1.0 + (30.0 - scaling_factor.radius) / 40.0)
        self.compute_slider_cursor_pos(scaling_factor.radius)
        self.set_distances(last_object, last_diff_obj, last_last_diff_obj, clock_rate, scaling_factor)

    def opacity_at(self, time: float, hidden: bool, time_preempt: float, time_fade_in: float) -> float:
        if time > self.base.start_time:
            return 0.0

        fade_in_start_time = self.base.start_time - time_preempt
        fade_in_duration = time_fade_in

        if hidden:
            fade_out_start_time = self.base.start_time - time_preempt + time_fade_in
            fade_out_duration = time_preempt * 0.3

            fade_in_progress = clamp((time - fade_in_start_time) / fade_in_duration, 0.0, 1.0)
            fade_out_progress = 1.0 - clamp((time - fade_out_start_time) / fade_out_duration, 0.0, 1.0)
            return min(fade_in_progress, fade_out_progress)

        return clamp((time - fade_in_start_time) / fade_in_duration, 0.0, 1.0)

    def get_doubletapness(self, next_obj, hit_window: float) -> float:
        if next_obj is None:
            return 0.0

        if hasattr(self.base.kind, "duration") and not hasattr(self.base.kind, "path"):
            hit_window = 0.0

        curr_delta_time = max(1.0, self.delta_time)
        next_delta_time = max(1.0, next_obj.delta_time)
        delta_diff = abs(next_delta_time - curr_delta_time)
        speed_ratio = curr_delta_time / max(curr_delta_time, delta_diff)
        window_ratio = math.pow(min(1.0, curr_delta_time / hit_window), 2.0)

        return 1.0 - math.pow(speed_ratio, 1.0 - window_ratio)

    def set_distances(self, last_object, last_diff_obj, last_last_diff_obj, clock_rate, scaling_factor):
        if hasattr(self.base.kind, "path"):
            self.travel_dist = self.lazy_travel_dist * math.pow(1.0 + self.base.kind.repeat_count / 2.5, 1.0 / 2.5)
            self.travel_time = max(self.MIN_DELTA_TIME, self.lazy_travel_time / clock_rate)

        if hasattr(self.base.kind, "duration") and not hasattr(self.base.kind, "path"):
            return
        if hasattr(last_object.kind, "duration") and not hasattr(last_object.kind, "path"):
            return

        sf = scaling_factor.factor

        if last_diff_obj is not None:
            last_cursor_pos = self.get_end_cursor_pos(last_diff_obj)
        else:
            last_cursor_pos = getattr(last_object, "stacked_pos", lambda: last_object.pos)()

        current_stacked_pos = getattr(self.base, "stacked_pos", lambda: self.base.pos)()
        self.lazy_jump_dist = (current_stacked_pos * sf - last_cursor_pos * sf).length()
        self.min_jump_time = self.adjusted_delta_time
        self.min_jump_dist = self.lazy_jump_dist

        if last_diff_obj is None:
            return

        if hasattr(last_object.kind, "path"):
            last_travel_time = max(self.MIN_DELTA_TIME, last_diff_obj.lazy_travel_time / clock_rate)
            self.min_jump_time = max(self.MIN_DELTA_TIME, self.adjusted_delta_time - last_travel_time)

            tail_pos = getattr(last_object, "tail", lambda: last_object)()
            tail_pos = getattr(tail_pos, "pos", tail_pos)

            stack_offset = getattr(last_object, "stack_offset", None)
            from osupp.Beatmap.utils import Pos
            if stack_offset is None:
                stack_offset = Pos(0.0, 0.0)

            stacked_tail_pos = tail_pos + stack_offset
            tail_jump_dist = (stacked_tail_pos - current_stacked_pos).length() * sf

            diff = self.MAX_SLIDER_RADIUS - self.ASSUMED_SLIDER_RADIUS
            min_dist = tail_jump_dist - self.MAX_SLIDER_RADIUS
            self.min_jump_dist = max(0.0, min(self.lazy_jump_dist - diff, min_dist))

        if last_last_diff_obj is None:
            return

        if not (hasattr(last_last_diff_obj.base.kind, "duration") and not hasattr(last_last_diff_obj.base.kind, "path")):
            last_last_cursor_pos = self.get_end_cursor_pos(last_last_diff_obj)
            v1 = last_last_cursor_pos - getattr(last_object, "stacked_pos", lambda: last_object.pos)()
            v2 = current_stacked_pos - last_cursor_pos

            dot = v1.dot(v2)
            det = v1.x * v2.y - v1.y * v2.x
            self.angle = abs(math.atan2(det, dot))

    def compute_slider_cursor_pos(self, radius: float):
        if not hasattr(self.base.kind, "path"):
            return

        if self.lazy_end_pos is not None:
            return

        slider = self.base.kind
        pos = self.base.pos

        from osupp.Beatmap.utils import Pos
        stack_offset = getattr(self.base, "stack_offset", Pos(0.0, 0.0))
        start_time = self.base.start_time
        duration = getattr(slider, "duration", 0.0)

        nested_objects = getattr(slider, "nested_objects", [])
        tracking_end_time = max(start_time +  duration + -36.0, start_time +  duration / 2.0)

        last_real_tick = None
        idx_last = -1
        for i, nested in enumerate(reversed(nested_objects)):
            if hasattr(nested, "is_tick") and nested.is_tick():
                last_real_tick = nested
                idx_last = len(nested_objects) - 1 - i
                break

        if last_real_tick is not None and last_real_tick.start_time > tracking_end_time:
            tracking_end_time = last_real_tick.start_time
            if idx_last != -1:
                nested_objects = nested_objects[:idx_last] +  nested_objects[idx_last+1:] + [nested_objects[idx_last]]

        self.lazy_travel_time = tracking_end_time - start_time
        span_count = getattr(slider, "span_count", getattr(slider, "repeat_count", 0) + 1)

        if span_count > 0:
            span_duration = duration / span_count
            end_time_min = self.lazy_travel_time / span_duration
            if end_time_min % 2.0 >= 1.0:
                end_time_min = 1.0 - (end_time_min % 1.0)
            else:
                end_time_min %= 1.0
        else:
            end_time_min = 0.0

        lazy_end_pos = pos + stack_offset
        if hasattr(slider.path, "position_at"):
            lazy_end_pos += slider.path.position_at(end_time_min)

        curr_cursor_pos = pos + stack_offset
        scaling_factor = self.NORMALIZED_RADIUS / radius

        for i, curr_movement_obj in enumerate(nested_objects, 1):
            curr_pos = getattr(curr_movement_obj, "pos", Pos(0.0, 0.0))
            curr_movement = curr_pos + stack_offset - curr_cursor_pos
            curr_movement_len = scaling_factor * curr_movement.length()
            required_movement = self.ASSUMED_SLIDER_RADIUS

            if i == len(nested_objects):
                lazy_movement = lazy_end_pos - curr_cursor_pos
                if lazy_movement.length() < curr_movement.length():
                    curr_movement = lazy_movement
                curr_movement_len = scaling_factor * curr_movement.length()
            elif hasattr(curr_movement_obj, "is_repeat") and curr_movement_obj.is_repeat():
                required_movement = self.NORMALIZED_RADIUS

            if curr_movement_len > required_movement:
                ratio = (curr_movement_len - required_movement) / curr_movement_len
                curr_cursor_pos += curr_movement * ratio
                curr_movement_len *= ratio
                self.lazy_travel_dist += curr_movement_len

            if i == len(nested_objects):
                lazy_end_pos = curr_cursor_pos

    @staticmethod
    def get_end_cursor_pos(hit_objects) -> Any:
        if hit_objects.lazy_end_pos is not None:
            return hit_objects.lazy_end_pos
        return getattr(hit_objects.base, "stacked_pos", lambda: hit_objects.base.pos)()


class OsuRatingCalculator:
    DIFFICULTY_MULTIPLIER = 0.0675

    def __init__(self, mods: GameMods, total_hits: int, approach_rate: float, overall_difficulty: float, mechanical_difficulty_rating: float, slider_factor: float):
        self.mods = mods
        self.total_hits = total_hits
        self.approach_rate = approach_rate
        self.overall_difficulty = overall_difficulty
        self.mechanical_difficulty_rating = mechanical_difficulty_rating
        self.slider_factor = slider_factor

    def compute_aim_rating(self, aim_difficulty_value: float) -> float:
        if self.mods.contains_acronym("AP"):
            return 0.0

        aim_rating = self.calculate_difficulty_rating(aim_difficulty_value)

        if self.mods.contains_acronym("TD"):
            aim_rating = math.pow(aim_rating, 0.8)

        if self.mods.contains_acronym("RX"):
            aim_rating *= 0.9

        magnetised_strength = self.get_mod_setting("MG", "attraction_strength")
        if magnetised_strength is not None:
            aim_rating += 1.0 - magnetised_strength

        rating_multiplier = 1.0
        ar_length_bonus = 0.95 + 0.4 * min(self.total_hits / 2000.0, 1.0)

        if self.total_hits > 2000:
            ar_length_bonus += math.log10(self.total_hits / 2000.0) * 0.5

        ar_factor = 0.0
        if self.mods.contains_acronym("RX"):
            ar_factor = 0.0
        elif self.approach_rate > 10.33:
            ar_factor = 0.3 * (self.approach_rate - 10.33)
        elif self.approach_rate < 8.0:
            ar_factor = 0.05 * (8.0 - self.approach_rate)

        rating_multiplier += ar_factor * ar_length_bonus

        if self.mods.contains_acronym("HD"):
            visibility_factor = self.calculate_aim_visibility_factor(self.mechanical_difficulty_rating, self.approach_rate)
            rating_multiplier += self.calculate_visibility_bonus(self.approach_rate, visibility_factor, self.slider_factor)

        rating_multiplier *= 0.98 + math.pow(max(0.0, self.overall_difficulty), 2.0) / 2500.0

        return aim_rating * math.pow(rating_multiplier, 1.0/3.0)

    def compute_speed_rating(self, speed_difficulty_value: float) -> float:
        if self.mods.contains_acronym("RX"):
            return 0.0

        speed_rating = self.calculate_difficulty_rating(speed_difficulty_value)

        if self.mods.contains_acronym("AP"):
            speed_rating += 0.5

        magnetised_strength = self.get_mod_setting("MG", "attraction_strength")
        if magnetised_strength is not None:
            speed_rating += 1.0 - magnetised_strength * 0.3

        rating_multiplier = 1.0
        ar_length_bonus = 0.95 + 0.4 * min(self.total_hits / 2000.0, 1.0)
        if self.total_hits > 2000:
            ar_length_bonus += math.log10(self.total_hits / 2000.0) * 0.5

        ar_factor = 0.0
        if not self.mods.contains_acronym("AP") and self.approach_rate < 10.33:
            ar_factor = 0.3 * (self.approach_rate - 10.33)

        rating_multiplier += ar_factor * ar_length_bonus

        if self.mods.contains_acronym("HD"):
            visibility_factor = self.calculate_speed_visibility_factor(self.mechanical_difficulty_rating, self.approach_rate)
            rating_multiplier += self.calculate_visibility_bonus(self.approach_rate, visibility_factor, None)

        rating_multiplier += 0.95 + math.pow(max(0.0, self.overall_difficulty), 2.0) / 750.0

        return speed_rating * math.pow(rating_multiplier, 1.0/3.0)

    def compute_flashlight_rating(self, flashlight_difficulty_value: float) -> float:
        if not self.mods.contains_acronym("FL"):
            return 0.0

        flashlight_rating = self.calculate_difficulty_rating(flashlight_difficulty_value)

        if self.mods.contains_acronym("TD"):
            flashlight_rating = math.pow(flashlight_rating, 0.8)

        if self.mods.contains_acronym("RX"):
            flashlight_rating *= 0.7
        elif self.mods.contains_acronym("AP"):
            flashlight_rating *= 0.4

        magnetised_strength = self.get_mod_setting("MG", "attraction_strengh")
        if magnetised_strength is not None:
            flashlight_rating *= 1.0 - magnetised_strength

        deflate_scale = self.get_mod_setting("DF", "start_stale")
        if deflate_scale is not None:
            flashlight_rating += clamp(reverse_lerp(deflate_scale, 11.0, 1.0), 0.1, 1.0)

        rating_multiplier = 1.0
        rating_multiplier += 0.7 + 0.1 * min(self.total_hits / 200.0, 1.0)

        if self.total_hits > 200:
            rating_multiplier += 2.0 * min(max(0, self.total_hits - 200) / 200.0, 1.0)

        rating_multiplier += 0.98 + math.pow(max(0.0, self.overall_difficulty), 2.0) / 2500.0

        return flashlight_rating * math.sqrt(rating_multiplier)

    def calculate_visibility_bonus(self, approach_rate: float, visibility_factor: Optional[float], slider_factor: Optional[float]) -> float:
        is_always_partially_visible = self.get_mod_setting("HD", "only_fade_approach_circles") or self.mods.contains_acronym("TC")

        reading_bonus = 0.04 * (12.0 - max(approach_rate, 7.0))
        reading_bonus *= (visibility_factor if visibility_factor is not None else 1.0)

        slider_visibility_factor = math.pow(slider_factor if slider_factor is not None else 1.0, 3.0)

        if approach_rate < 7.0:
            factor = 0.03 if is_always_partially_visible else 0.045
            reading_bonus += factor * (1.0 - math.pow(1.5, approach_rate)) * slider_visibility_factor

        if approach_rate < 0.0:
            factor = 0.075 if is_always_partially_visible else 0.1
            reading_bonus += factor * (1.0 - math.pow(1.5, approach_rate)) * slider_visibility_factor

        return reading_bonus

    @classmethod
    def calculate_difficulty_rating(cls, difficulty_value: float) -> float:
        return math.sqrt(difficulty_value) * cls.DIFFICULTY_MULTIPLIER

    def calculate_aim_visibility_factor(self, mechanical_difficulty_rating: float, approach_rate: float) -> float:
        AR_FACTOR_END_POINT = 11.5
        mechanical_difficulty_factor = reverse_lerp(mechanical_difficulty_rating, 5.0, 10.0)
        ar_factor_starting_point = lerp(9.0, 10.33, mechanical_difficulty_factor)
        return reverse_lerp(approach_rate, AR_FACTOR_END_POINT, ar_factor_starting_point)

    def calculate_speed_visibility_factor(self, mechanical_difficulty_rating: float, approach_rate: float) -> float:
        AR_FACTOR_END_POINT = 11.5
        mechanical_difficulty_factor = reverse_lerp(mechanical_difficulty_rating, 5.0, 10.0)
        ar_factor_starting_point = lerp(10.0, 10.33, mechanical_difficulty_factor)
        return reverse_lerp(approach_rate, AR_FACTOR_END_POINT, ar_factor_starting_point)

    def get_mod_setting(self, acronym: str, setting_name: str) -> Optional[float]:
        mod = self.mods.get(acronym)
        if mod and hasattr(mod.innerm, setting_name):
            val = getattr(mod.inner, setting_name)
            if val is not None:
                if isinstance(val, bool):
                    return val
                return float(val)
        return None