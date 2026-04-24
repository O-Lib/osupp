import bisect
import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from section.general import GameMode
from utils import Pos

from .path_type import SplineType

if TYPE_CHECKING:
    from .path import PathControlPoint

BEZIER_TOLERANCE = 0.25
CATMULL_DETAIL = 50
CIRCULAR_ARC_TOLERANCE = 0.1


@dataclass
class BezierBuffers:
    left: list[Pos] = field(default_factory=list)
    right: list[Pos] = field(default_factory=list)
    midpoints: list[Pos] = field(default_factory=list)
    left_child: list[Pos] = field(default_factory=list)

    def clear(self):
        self.left.clear()
        self.right.clear()
        self.midpoints.clear()
        self.left_child.clear()

    def extend_exact(self, length: int):
        current_len = len(self.left)
        if length <= current_len:
            return

        additional = length - current_len

        for _ in range(additional):
            self.left.append(Pos())
            self.right.append(Pos())
            self.midpoints.append(Pos())
            self.left_child.append(Pos())


@dataclass
class CurveBuffers:
    path: list[Pos] = field(default_factory=list)
    lengths: list[float] = field(default_factory=list)
    vertices: list[Pos] = field(default_factory=list)
    bezier: BezierBuffers = field(default_factory=BezierBuffers)

    def clear(self):
        self.path.clear()
        self.lengths.clear()
        self.vertices.clear()
        self.bezier.clear()


@dataclass
class CircularArcProperties:
    theta_start: float
    theta_range: float
    direction: float
    radius: float
    centre: Pos


@dataclass
class Curve:
    def __init__(self, path: list[Pos], lengths: list[float]):
        self._path = path
        self._lengths = lengths

    @classmethod
    def new(
        cls,
        mode: "GameMode",
        points: list["PathControlPoint"],
        expected_len: float | None,
        bufs: "CurveBuffers",
    ) -> "Curve":
        optimized_len = [0.0]
        calculate_path(mode, points, bufs, optimized_len)
        calculate_length(bufs, expected_len, optimized_len[0])

        path_result = list(bufs.path)
        lengths_result = list(bufs.lengths)

        bufs.clear()
        return cls(path_result, lengths_result)

    @property
    def path(self) -> list[Pos]:
        return self._path

    @property
    def lengths(self) -> list[float]:
        return self._lengths

    def position_at(self, progress: float) -> Pos:
        return position_at(self._path, self._lengths, progress)

    def progress_to_dist(self, progress: float) -> float:
        return progress_to_dist(self._lengths, progress)

    def dist(self) -> float:
        if not self._lengths:
            return 0.0
        return self._lengths[-1]

    def idx_of_dist(self, d: float) -> int:
        return idx_of_dist(self._lengths, d)

    def interpolate_vertices(self, i: int, d: float) -> Pos:
        return interpolate_vertices(self._path, self._lengths, i, d)

    def as_borrowed_curve(self) -> "BorrowedCurve":
        return BorrowedCurve(self._path, self._lengths)


@dataclass
class BorrowedCurve:
    _path: list[Pos]
    _lengths: list[float]

    @classmethod
    def new(
        cls,
        mode: "GameMode",
        points: list["PathControlPoint"],
        expected_len: float | None,
        bufs: "CurveBuffers",
    ) -> "BorrowedCurve":
        optimized_len = [0.0]
        calculate_path(mode, points, bufs, optimized_len)
        calculate_length(bufs, expected_len, optimized_len[0])

        return cls(bufs.path, bufs.lengths)

    @property
    def path(self) -> list[Pos]:
        return self._path

    @property
    def lengths(self) -> list[float]:
        return self._lengths

    def position_at(self, progress: float) -> Pos:
        return position_at(self._path, self._lengths, progress)

    def progress_to_dist(self, progress: float) -> float:
        return progress_to_dist(self._lengths, progress)

    def dist(self) -> float:
        return dist(self._lengths)

    def idx_of_dist(self, d: float) -> int:
        return idx_of_dist(self._lengths, d)

    def interpolate_vertices(self, i: int, d: float) -> Pos:
        return interpolate_vertices(self._path, self._lengths, i, d)

    def to_owned_curve(self) -> "Curve":
        return Curve(list(self._path), list(self._lengths))


def progress_to_dist(lengths: list[float], progress: float) -> float:
    clamped_progress = max(0.0, min(1.0, progress))
    return clamped_progress * dist(lengths)


def idx_of_dist(lengths: list[float], d: float) -> int:
    return bisect.bisect_left(lengths, d)


def dist(lengths: list[float]) -> float:
    return lengths[-1] if lengths else 0.0


def interpolate_vertices(
    path: list[Pos], lengths: list[float], i: int, d: float
) -> Pos:
    if not path:
        return Pos()

    if i == 0:
        return path[0]

    if i >= len(path):
        return path[-1]

    p1 = path[i]
    p0 = path[i - 1]

    d0 = lengths[i - 1]
    d1 = lengths[i]

    if abs(d0 - d1) <= 2.220446049250313e-16:
        return p0

    w = (d - d0) / (d1 - d0)

    return p0 + (p1 - p0) * float(w)


def position_at(path: list[Pos], lengths: list[float], progress: float) -> Pos:
    d = progress_to_dist(lengths, progress)
    i = idx_of_dist(lengths, d)

    return interpolate_vertices(path, lengths, i, d)


def calculate_path(
    mode: "GameMode",
    points: list["PathControlPoint"],
    bufs: "CurveBuffers",
    optimized_len_ref: list[float],
):
    if not points:
        return

    path = bufs.path
    vertices = bufs.vertices
    bezier_bufs = bufs.bezier

    path.clear()
    optimized_len_ref[0] = 0.0

    vertices.clear()
    for p in points:
        vertices.append(p.pos)

    start = 0

    for i in range(len(points)):
        if points[i].path_type is None and i < len(points) - 1:
            continue

        segment_vertices = vertices[start : i + 1]

        if len(segment_vertices) == 0:
            continue

        elif len(segment_vertices) == 1:
            path.append(segment_vertices[0])

        else:
            segment_kind = SplineType.Linear
            pt = points[start].path_type
            if pt is not None:
                segment_kind = pt.kind

            path_len_before = len(path)

            calculate_subpath(
                mode,
                path,
                segment_vertices,
                segment_kind,
                optimized_len_ref,
                bezier_bufs,
            )

            if path_len_before > 0 and len(path) > path_len_before:
                if path[path_len_before - 1] == path[path_len_before]:
                    path.pop(path_len_before)

            start = i


def calculate_length(
    bufs: "CurveBuffers", expected_len: float | None, optimized_len: float
):
    path = bufs.path
    cumulative_len = bufs.lengths

    cumulative_len.clear()
    calculated_len = optimized_len

    cumulative_len.append(0.0)

    for i in range(len(path) - 1):
        curr_pos = path[i]
        next_pos = path[i + 1]

        diff = next_pos - curr_pos
        calculated_len += float(diff.length())
        cumulative_len.append(calculated_len)

    EPSILON = 2.220446049250313e-16

    if expected_len is not None and abs(calculated_len - expected_len) >= EPSILON:
        if len(path) >= 2 and path[-1] == path[-2] and expected_len > calculated_len:
            cumulative_len.append(calculated_len)
            return

        if len(cumulative_len) == 1:
            return

        cumulative_len.pop()

        last_valid = 0
        for i in range(len(cumulative_len) - 1, -1, -1):
            if cumulative_len[i] < expected_len:
                last_valid = i + 1
                break

        if last_valid < len(cumulative_len):
            cumulative_len = cumulative_len[:last_valid]
            del path[last_valid + 1 :]
            bufs.lengths = cumulative_len

            if not cumulative_len:
                cumulative_len.append(0.0)
                return

        end_idx = len(cumulative_len)
        prev_idx = end_idx - 1

        p_prev = path[prev_idx]
        p_end = path[end_idx]

        dir_vec = (p_end - p_prev).normalize()

        dist_remaining = expected_len - cumulative_len[prev_idx]
        path[end_idx] = p_prev + dir_vec * float(dist_remaining)

        cumulative_len.append(expected_len)


def calculate_subpath(
    mode: "GameMode",
    path: list[Pos],
    sub_points: list[Pos],
    path_type: SplineType,
    optimized_len_ref: list[float],
    bufs: "BezierBuffers",
):
    if path_type == SplineType.Linear:
        approximate_linear(path, sub_points)

    elif path_type == SplineType.PerfectCurve:
        if len(sub_points) == 3:
            if approximate_circular_arc(
                path, sub_points[0], sub_points[1], sub_points[2]
            ):
                return

        approximate_bezier(path, sub_points, bufs)

    elif path_type == SplineType.Catmull:
        start_len = len(path)
        approximate_catmull(path, sub_points)

        if mode != GameMode.Osu:
            return

        sub_path = path[start_len:]
        del path[start_len:]

        last_start = None
        len_removed_since_start = 0.0

        CATMULL_SEGMENT_LEN = CATMULL_DETAIL * 2

        for i, curr in enumerate(sub_path):
            if last_start is None:
                path.append(curr)
                last_start = curr
                continue

            dist_from_start = float(last_start.distance(curr))
            len_removed_since_start += float(sub_path[i - 1].distance(curr))

            if (
                dist_from_start > 6.0
                or ((i + 1) % CATMULL_SEGMENT_LEN) == 0
                or i == len(sub_path) - 1
            ):
                path.append(curr)
                optimized_len_ref[0] += len_removed_since_start - dist_from_start

                last_start = None
                len_removed_since_start = 0.0

    elif path_type == SplineType.BSpline:
        approximate_bezier(path, sub_points, bufs)


def approximate_bezier(path: list[Pos], points: list[Pos], bufs: "BezierBuffers"):
    bufs.extend_exact(len(points))
    approximate_bspline(path, points, bufs)


def approximate_catmull(path: list[Pos], points: list[Pos]):
    if len(points) <= 1:
        return

    v1 = points[0]
    v2 = points[0]
    v3 = points[1] if len(points) > 1 else v2
    v4 = points[2] if len(points) > 2 else (v3 * 2.0 - v2)

    catmull_subpath(path, v1, v2, v3, v4)

    for i in range(2, len(points)):
        v1 = points[i - 2]
        v2 = points[i - 1]
        v3 = points[i]
        v4 = points[i + 1] if i + 1 < len(points) else (v3 * 2.0 - v2)

        catmull_subpath(path, v1, v2, v3, v4)


def approximate_linear(path: list[Pos], points: list[Pos]):
    path.extend(points)


def approximate_circular_arc(path: list[Pos], a: Pos, b: Pos, c: Pos) -> bool:
    pr = circular_arc_properties(a, b, c)
    if pr is None:
        return False

    if 2.0 * pr.radius <= CIRCULAR_ARC_TOLERANCE:
        sub_points = 2
    else:
        divisor = 2.0 * math.acos(1.0 - (CIRCULAR_ARC_TOLERANCE / pr.radius))

        if abs(divisor) <= 1.1920929e-07:
            sub_points = 2
        else:
            sub_points = max(2, int(math.ceil(pr.theta_range / float(divisor))))

    if sub_points >= 1000:
        return False

    directed_range = pr.direction * pr.theta_range
    divisor_val = float(sub_points - 1)

    for i in range(sub_points):
        fract = i / divisor_val
        theta = pr.theta_start + fract * directed_range

        sin_t = math.sin(theta)
        cos_t = math.cos(theta)

        origin = Pos(x=float(cos_t), y=float(sin_t))

        point = pr.centre + origin * pr.radius
        path.append(point)

    return True


def approximate_bspline(path: list[Pos], points: list[Pos], bufs: "BezierBuffers"):
    p = len(points)
    if p == 0:
        return

    to_flatten = [list(points)]
    free_bufs = []

    left = bufs.left
    right = bufs.right
    midpoints = bufs.midpoints
    left_child = bufs.left_child

    while to_flatten:
        parent = to_flatten.pop()

        if bezier_is_flat_enough(parent):
            bezier_approximate(parent, path, left, right, midpoints)

            free_bufs.append(parent)
            continue

        if free_bufs:
            right_child = free_bufs.pop()
        else:
            right_child = [Pos() for _ in range(p)]

        bezier_subdivide(parent, left_child, right_child, midpoints)

        for i in range(p):
            parent[i] = left_child[i]

        to_flatten.append(right_child)
        to_flatten.append(parent)

    path.append(points[p - 1])


def bezier_is_flat_enough(point: list[Pos]) -> bool:
    limit = BEZIER_TOLERANCE * BEZIER_TOLERANCE * 4.0

    for i in range(len(point) - 2):
        prev = point[i]
        curr = point[i + 1]
        next_p = point[i + 2]

        deviation = prev - curr * 2.0 + next_p
        if deviation.length_squared() > limit:
            return False

    return True


def bezier_subdivide(
    points: list[Pos], list_pos: list[Pos], list_pos2: list[Pos], midpoints: list[Pos]
):
    count = len(points)

    for i in range(count):
        midpoints[i] = points[i]

    for i in range(count - 1, 0, -1):
        list_pos[count - i - 1] = midpoints[0]
        list_pos2[i] = midpoints[i]

        for j in range(i):
            midpoints[j] = (midpoints[j] + midpoints[j + 1]) / 2.0

    list_pos[count - 1] = midpoints[0]
    list_pos2[0] = midpoints[0]


def bezier_approximate(
    points: list[Pos],
    path: list[Pos],
    list_pos: list[Pos],
    list_pos2: list[Pos],
    midpoints: list[Pos],
):
    count = len(points)
    if count == 0:
        return

    bezier_subdivide(points, list_pos, list_pos2, midpoints)
    path.append(points[0])
    combined = list_pos[:count] + list_pos2[1:count]

    for i in range(1, len(combined) - 2, 2):
        prev = combined[i]
        curr = combined[i + 1]
        next_p = combined[i + 2]

        smoothed_pos = (prev + curr * 2.0 + next_p) * 0.25
        path.append(smoothed_pos)


def catmull_subpath(path: list[Pos], v1: Pos, v2: Pos, v3: Pos, v4: Pos):
    x1 = 2.0 * v2.x
    x2 = -v1.x * v3.x
    x3 = 2.0 * v1.x - 5.0 * v2.x + 4.0 * v3.x - v4.x
    x4 = -v1.x + 3.0 * (v2.x - v3.x) + v4.x

    y1 = 2.0 * v2.y
    y2 = -v1.y * v3.y
    y3 = 2.0 * v1.y - 5.0 * v2.y + 4.0 * v3.y - v4.y
    y4 = -v1.y + 3.0 * (v2.y - v3.y) + v4.y

    detail_f = float(CATMULL_DETAIL)

    for c in range(CATMULL_DETAIL):
        c_f = float(c)

        t1 = c_f / detail_f
        t2 = t1 * t1
        t3 = t2 * t1

        pos1 = Pos(
            x=0.5 * (x1 + x2 * t1 + x3 * t2 + x4 * t3),
            y=0.5 * (y1 + y2 * t1 + y3 * t2 + y4 * t3),
        )

        t1 = (c_f + 1.0) / detail_f
        t2 = t1 * t1
        t3 = t2 * t1

        pos2 = Pos(
            x=0.5 * (x1 + x2 * t1 + x3 * t2 + x4 * t3),
            y=0.5 * (y1 + y2 * t1 + y3 * t2 + y4 * t3),
        )
        path.append(pos1)
        path.append(pos2)


def circular_arc_properties(a: Pos, b: Pos, c: Pos) -> CircularArcProperties | None:
    if abs((b.y - a.y) * (c.x - a.x) - (b.x - a.x) * (c.y - a.y)) <= 1.1920929e-07:
        return None

    d = 2.0 * (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y))

    a_sq = a.length_squared()
    b_sq = b.length_squared()
    c_sq = c.length_squared()

    centre = Pos(
        x=(a_sq * (b.y - c.y) + b_sq * (c.y - a.y) + c_sq * (a.y - b.y)) / d,
        y=(a_sq * (c.x - b.x) + b_sq * (a.x - c.x) + c_sq * (b.x - a.x)) / d,
    )

    d_a = a - centre
    d_c = c - centre

    radius = float(d_a.length())

    theta_start = math.atan2(float(d_a.y), float(d_a.x))
    theta_end = math.atan2(float(d_c.y), float(d_c.x))

    while theta_end < theta_start:
        theta_end += 2.0 * math.pi

    direction = 1.0
    theta_range = theta_end - theta_start

    ortho_a_to_c = Pos(x=(c.y - a.y), y=-(c.x - a.x))

    if ortho_a_to_c.dot(b - a) < 0.0:
        direction = -direction
        theta_range = 2.0 * math.pi - theta_range

    return CircularArcProperties(
        theta_start=theta_start,
        theta_range=theta_range,
        direction=direction,
        radius=radius,
        centre=centre,
    )
