from __future__ import annotations

import math
from collections.abc import Generator
from dataclasses import dataclass, field
from enum import Enum

from section.enums import GameMode, SplineType
from utils import Pos

BEZIER_TOLERANCE = 0.25
CATMULL_DETAIL = 50
CIRCULAR_ARC_TOLERANCE = 0.1


@dataclass(slots=True, eq=True)
class PathType:
    kind: SplineType
    degree: int | None = None

    @classmethod
    def new_from_str(cls, s: str) -> PathType:
        if not s:
            return cls(SplineType.Catmull)

        char = s[0].upper()
        if char == "B":
            if len(s) > 1:
                try:
                    deg = int(s[1:])
                    if deg > 0:
                        return cls(SplineType.BSpline, deg)

                except ValueError:
                    pass
            return cls(SplineType.BSpline)
        elif char == "L":
            return cls(SplineType.Linear)
        elif char == "P":
            return cls(SplineType.PerfectCurve)
        else:
            return cls(SplineType.Catmull)


@dataclass(slots=True, eq=True)
class PathControlPoint:
    pos: Pos
    path_type: PathType | None = None


class Curve:
    def __init__(
        self, mode: GameMode, points: list[PathControlPoint], expected_len: float | None
    ):
        self.path: list[Pos] = []
        self.lengths: list[float] = []

        optimized_len = [0.0]
        self._calculate_path(mode, points, optimized_len)
        self._calculate_length(expected_len, optimized_len[0])

    def dist(self) -> float:
        return self.lengths[-1] if self.lengths else 0.0

    def progress_to_dist(self, progress: float) -> float:
        return max(0.0, min(1.0, progress)) * self.dist()

    def _calculate_path(
        self, mode: GameMode, points: list[PathControlPoint], optimized_len: list[float]
    ):
        vertices = [p.pos for p in points]
        start = 0

        for i in range(len(points)):
            if points[i].path_type is None and i < len(points) - 1:
                continue

            segment_vertices = vertices[start : i + 1]
            if len(segment_vertices) == 1:
                self.path.append(segment_vertices[0])
            elif len(segment_vertices) > 1:
                pt = points[start].path_type
                segment_kind = (
                    pt.kind
                    if pt is not None
                    else SplineType.Linear
                )
                path_len = len(self.path)

                self._calculate_subpath(
                    mode, segment_vertices, segment_kind, optimized_len
                )

                if path_len > 0 and self.path[path_len - 1] == self.path[path_len]:
                    self.path.pop(path_len)

            start = i

    def _calculate_length(self, expected_len: float | None, optimized_len: float):
        calculated_len = optimized_len
        self.lengths.append(0.0)

        for i in range(len(self.path) - 1):
            curr_p = self.path[i]
            next_p = self.path[i + 1]
            calculated_len += (next_p - curr_p).length()
            self.lengths.append(calculated_len)

        if expected_len is not None and abs(calculated_len - expected_len) >= 1e-7:
            if (
                len(self.path) >= 2
                and self.path[-1] == self.path[-2]
                and expected_len > calculated_len
            ):
                self.lengths.append(calculated_len)
                return

            if len(self.lengths) == 1:
                return

            self.lengths.pop()

            last_valid = 0
            for i in range(len(self.lengths) - 1, -1, -1):
                if self.lengths[i] < expected_len:
                    last_valid = i + 1
                    break

            if last_valid < len(self.lengths):
                self.lengths = self.lengths[:last_valid]
                self.path = self.path[: last_valid + 1]

                if not self.lengths:
                    self.lengths.append(0.0)
                    return

                end_idx = len(self.lengths)
                prev_idx = end_idx - 1
                direction = (self.path[end_idx] - self.path[prev_idx]).normalize()

                self.path[end_idx] = self.path[prev_idx] + (
                    direction * float(expected_len - self.lengths[prev_idx])
                )

    def _calculate_subpath(
        self,
        mode: GameMode,
        sub_points: list[Pos],
        path_type: SplineType,
        optimized_len: list[float],
    ):
        if path_type == SplineType.Linear:
            self.path.extend(sub_points)

        elif path_type == SplineType.PerfectCurve:
            if len(sub_points) == 3 and self._approximate_circular_arc(
                sub_points[0], sub_points[1], sub_points[2]
            ):
                return
            self._approximate_bezier(sub_points)

        elif path_type == SplineType.BSpline:
            self._approximate_bezier(sub_points)

        elif path_type == SplineType.Catmull:
            start_len = len(self.path)
            self._approximate_catmull(sub_points)

            if mode != GameMode.Osu:
                return

            sub_path = self.path[start_len:]
            self.path = self.path[:start_len]
            last_start = None
            len_removed_since_start = 0.0

            for i, curr in enumerate(sub_path):
                if last_start is None:
                    self.path.append(curr)
                    last_start = curr
                    continue

                dist_from_start = last_start.distance(curr)
                len_removed_since_start += sub_path[i - 1].distance(curr)

                if (
                    dist_from_start > 6.0
                    or ((i + 1) % (CATMULL_DETAIL * 2)) == 0
                    or i == len(sub_path) - 1
                ):
                    self.path.append(curr)
                    optimized_len[0] += len_removed_since_start - dist_from_start
                    last_start = None
                    len_removed_since_start = 0.0

    def _approximate_bezier(self, points: list[Pos]):
        to_flatten = [list(points)]

        while to_flatten:
            parent = to_flatten.pop()

            limit = BEZIER_TOLERANCE * BEZIER_TOLERANCE * 4.0
            is_flat = True
            for i in range(len(parent) - 2):
                if (parent[i] - (parent[i + 1] * 2.0)) + parent[
                    i + 2
                ].length_squared() > limit:
                    is_flat = False
                    break

            if is_flat:
                left, right = self._bezier_subdivide(parent)
                self.path.append(parent[0])
                lr = left + right[1:]
                for i in range(1, len(lr) - 2, 2):
                    self.path.append((lr[i] + (lr[i + 1] * 2.0) + lr[i + 2]) * 0.25)
            else:
                left, right = self._bezier_subdivide(parent)
                to_flatten.append(right)
                to_flatten.append(left)

        self.path.append(points[-1])

    def _bezier_subdivide(self, points: list[Pos]) -> tuple[list[Pos], list[Pos]]:
        count = len(points)
        midpoints = list(points)
        left = [Pos()] * count
        right = [Pos()] * count

        for i in range(1, count)[::-1]:
            left[count - i - 1] = midpoints[0]
            right[i] = midpoints[i]
            for j in range(i):
                midpoints[j] = (midpoints[j] + midpoints[j + 1]) * 0.5

        left[count - 1] = midpoints[0]
        right[0] = midpoints[0]
        return left, right

    def _approximate_catmull(self, points: list[Pos]):
        if len(points) == 1:
            return
        for i in range(len(points) - 1):
            v1 = points[i - 1] if i > 0 else points[i]
            v2 = points[i]
            v3 = points[i + 1] if i < len(points) - 1 else v2 * 2.0 - v1
            v4 = points[i + 2] if i < len(points) - 2 else v3 * 2.0 - v2

            for c in range(CATMULL_DETAIL):
                t1 = c / float(CATMULL_DETAIL)
                t2 = t1 * t1
                t3 = t2 * t1

                pos = Pos(
                    0.5
                    * (
                        2.0 * v2.x
                        + (-v1.x + v3.x) * t1
                        + (2.0 * v1.x - 5.0 * v2.x + 4.0 * v3.x - v4.x) * t2
                        + (-v1.x + 3.0 * (v2.x - v3.x) + v4.x) * t3
                    ),
                    0.5
                    * (
                        2.0 * v2.y
                        + (-v1.y + v3.y) * t1
                        + (2.0 * v1.y - 5.0 * v2.y + 4.0 * v3.y - v4.y) * t2
                        + (-v1.y + 3.0 * (v2.y - v3.y) + v4.y) * t3
                    ),
                )
                self.path.append(pos)

    def _approximate_circular_arc(self, a: Pos, b: Pos, c: Pos) -> bool:
        if abs((b.y - a.y) * (c.x - a.x) - (b.x - a.x) * (c.y - a.y)) <= 1e-7:
            return False

        d = 2.0 * (a.x * (b - c).y + b.x * (c - a).y + c.x * (a - b).y)
        a_sq, b_sq, c_sq = a.length_squared(), b.length_squared(), c.length_squared()

        centre = Pos(
            (a_sq * (b - c).y + b_sq * (c - a).y + c_sq * (a - b).y) / d,
            (a_sq * (c - b).x + b_sq * (a - c).x + c_sq * (b - a).x) / d,
        )

        radius = (a - centre).length()
        theta_start = math.atan2(a.y - centre.y, a.x - centre.x)
        theta_end = math.atan2(c.y - centre.y, c.x - centre.x)

        while theta_end < theta_start:
            theta_end += 2.0 * math.pi

        direction = 1.0
        theta_range = theta_end - theta_start

        ortho_a_to_c = Pos((c - a).y, -(c - a).x)
        if ortho_a_to_c.dot(b - a) < 0.0:
            direction = -direction
            theta_range = 2.0 * math.pi - theta_range

        val = max(-1.0, min(1.0, 1.0 - (CIRCULAR_ARC_TOLERANCE / radius)))
        sub_points = (
            2
            if (2.0 * radius) <= CIRCULAR_ARC_TOLERANCE
            else max(2, math.ceil(theta_range / (2.0 * math.acos(val))))
        )

        if sub_points >= 1000:
            return False

        for i in range(sub_points):
            fract = i / float(sub_points - 1)
            theta = theta_start + fract * direction * theta_range
            self.path.append(centre + Pos(math.cos(theta), math.sin(theta)) * radius)

        return True


@dataclass(slots=True, eq=True)
class SliderPath:
    mode: GameMode
    control_points: list[PathControlPoint]
    expected_dist: float | None
    _curve: Curve | None = field(default=None, init=False)

    def curve(self) -> Curve:
        if self._curve is None:
            self._curve = Curve(self.mode, self.control_points, self.expected_dist)
        return self._curve


class SliderEventType(Enum):
    Head = 0
    Tick = 1
    Repeat = 2
    LastTick = 3
    Tail = 4


@dataclass(slots=True, eq=True)
class SliderEvent:
    kind: SliderEventType
    span_idx: int
    span_start_time: float
    time: float
    path_progress: float


def generate_slider_events(
    start_time: float,
    span_duration: float,
    velocity: float,
    tick_dist: float,
    total_dist: float,
    span_count: int,
) -> Generator[SliderEvent, None, None]:
    MAX_LEN = 100000.0
    TAIL_LENIENCY = -36.0

    length = min(MAX_LEN, total_dist)
    tick_dist = max(0.0, min(tick_dist, length))
    min_dist_from_end = velocity * 10.0

    yield SliderEvent(SliderEventType.Head, 0, start_time, start_time, 0.0)

    for span in range(span_count):
        reversed_span = span % 2 == 1
        span_start = start_time + span * span_duration
        with_repeat = span < span_count - 1

        span_ticks = []
        d = tick_dist
        if d > 0.0:
            while d <= length:
                if d >= length - min_dist_from_end:
                    break
                progress = d / length
                time_prog = 1.0 - progress if reversed_span else progress
                span_ticks.append(
                    SliderEvent(
                        SliderEventType.Tick,
                        span,
                        span_start,
                        span_start + time_prog * span_duration,
                        progress,
                    )
                )
                d += tick_dist

        if reversed_span:
            yield from reversed(span_ticks)
            if with_repeat:
                yield SliderEvent(
                    SliderEventType.Repeat,
                    span,
                    span_start,
                    span_start + span_duration,
                    float((span + 1) % 2),
                )
        else:
            yield from span_ticks
            if with_repeat:
                yield SliderEvent(
                    SliderEventType.Repeat,
                    span,
                    span_start,
                    span_start + span_duration,
                    float((span + 1) % 2),
                )

    total_duration = span_count * span_duration
    final_span_idx = span_count - 1
    final_span_start = start_time + final_span_idx * span_duration

    last_tick_time = max(
        start_time + total_duration / 2.0,
        final_span_start + span_duration + TAIL_LENIENCY,
    )
    last_tick_progress = (last_tick_time - final_span_start) / span_duration
    if span_count % 2 == 0:
        last_tick_progress = 1.0 - last_tick_progress

    yield SliderEvent(
        SliderEventType.LastTick,
        final_span_idx,
        final_span_start,
        last_tick_time,
        last_tick_progress,
    )
    yield SliderEvent(
        SliderEventType.Tail,
        final_span_idx,
        final_span_start,
        start_time + total_duration,
        float(span_count % 2),
    )
