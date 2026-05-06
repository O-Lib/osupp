import math
from typing import TypeVar, Generic

EPSILON = 1e-7

def almost_eq(a: float, b: float, acceptable_difference: float = EPSILON) -> bool:
    return abs(a - b) <= acceptable_difference


def lerp(value1: float, value2: float, amount: float) -> float:
    return (value1 * (1.0 - amount)) + (value2 * amount)


def bpm_to_milliseconds(bpm: float, delimiter: int | None = None) -> float:
    d = delimiter if delimiter is not None else 4
    return 60000.0 / d / bpm


def milliseconds_to_bpm(ms: float, delimiter: int | None = None) -> float:
    d = delimiter if delimiter is not None else 4
    return 60000.0 / (ms * d)


def logistic(x: float, midpoint_offset: float, multiplier: float, max_value: float | None = None) -> float:
    m = max_value if max_value is not None else 1.0
    try:
        return m / (1.0 + math.exp(multiplier * (midpoint_offset - x)))
    except OverflowError:
        return 0.0


def logistic_exp(exp_val: float, max_value: float | None = None) -> float:
    m = max_value if max_value is not None else 1.0
    try:
        return m / (1.0 + math.exp(exp_val))
    except OverflowError:
        return 0.0


def norm(p: float, values: list[float]) -> float:
    return sum(math.pow(x, p) for x in values) ** (1.0 / p)


def bell_curve(x: float, mean: float, width: float, multiplier: float | None = None) -> float:
    m = multiplier if multiplier is not None else 1.0
    return m * math.exp(math.e * -(math.pow(x - mean, 2.0) / math.pow(width, 2.0)))


def smoothstep_bell_curve(x: float, mean: float, width: float) -> float:
    new_x = x - mean
    new_x = width - new_x if new_x > 0.0 else width + new_x
    return smoothstep(new_x, 0.0, width)

def smoothstep(x: float, start: float, end: float) -> float:
    t = reverse_lerp(x, start, end)
    return t * t * (3.0 - 2.0 * t)


def smootherstep(x: float, start: float, end: float) -> float:
    t = reverse_lerp(x, start, end)
    return t * t * t * (t * (6.0 * t - 15.0) + 10.0)


def reverse_lerp(x: float, start: float, end: float) -> float:
    if start == end:
        return 0.0
    return clamp((x - start) / (end - start), 0.0, 1.0)

def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, value))

def erf(x: float) -> float:
    if almost_eq(x, 0.0):
        return 0.0
    if math.isinf(x):
        return 1.0 if x > 0.0 else -1.0
    if math.isnan(x):
        return math.nan

    t = 1.0 / (1.0 + 0.3275911 * abs(x))
    tau = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))))

    res = 1.0 - tau * math.exp(-x * x)
    return res if x >= 0.0 else -res


def erf_inv(x: float) -> float:
    if x <= -1.0:
        return float('-inf')
    if x >= 1.0:
        return float('inf')
    if almost_eq(x, 0.0):
        return 0.0

    A = 0.147
    sgn = math.copysign(1.0, x)
    x = abs(x)

    ln = math.log(1.0 - x * x)
    t1 = 2.0 / (math.pi * A) + ln / 2.0
    t2 = ln / A
    base_approx = math.sqrt(max(0.0, t1 * t1 - t2)) - t1

    c = math.pow((x - 0.85) / 0.293, 8.0) if x >= 0.85 else 0.0

    return sgn * (math.sqrt(max(0.0, base_approx)) + c)


def get_precision_adjusted_beat_len(slider_velocity_multiplier: float, beat_len: float) -> float:
    if slider_velocity_multiplier == 0:
        return

    slider_velocity_as_beat_len = -100.0 / slider_velocity_multiplier

    if slider_velocity_as_beat_len < 0.0:
        bpm_multiplier = clamp(float(-slider_velocity_as_beat_len), 10.0, 10000.0) / 100.0
    else:
        bpm_multiplier = 1.0

    return beat_len * bpm_multiplier


def calculate_difficulty_peppy_stars(map_attrs, object_count: int, drain_len: int) -> int:
    object_to_drain_ratio = 16.0
    if drain_len != 0:
        object_to_drain_ratio = clamp((float(object_count) / float(drain_len) * 8.0), 0.0, 16.0)

    drain_rate = float(map_attrs.hp())
    overall_difficulty = float(map_attrs.od())
    circle_size = float(map_attrs.cs())

    val = (drain_rate + overall_difficulty + circle_size + object_to_drain_ratio) / 38.0 * 5.0
    return int(round(val))


T = TypeVar("T")

class LimitedQueue(Generic[T]):
    __slots__ = ("_queue", "_end", "_len", "_capacity")

    def __init__(self, capacity: int, default_val: T | None = None):
        if capacity <= 0:
            raise ValueError("The capacity must be greater than zero.")
        self._capacity = capacity
        self._queue: list[T | None] = [default_val for _ in range(capacity)]
        self._end = capacity - 1
        self._len = 0

    def push(self, elem: T) -> None:
        self._end = (self._end + 1) % self._capacity
        self._queue[self._end] = elem
        if self._len < self._capacity:
            self._len += 1

    @property
    def is_empty(self) -> bool:
        return self._len == 0

    @property
    def is_full(self) -> bool:
        return self._len == self._capacity

    def __len__(self) -> int:
        return self._len

    @property
    def last(self) -> T | None:
        if self.is_empty:
            return None
        return self._queue[self._end]

    def __getitem__(self, idx: int) -> T | None:
        if idx < 0 or idx >= self._len:
            raise IndexError("Index outside the bounds of the array.")

        actual_idx = (idx + (1 if self.is_full else 0) * (self._end + 1)) % self._capacity
        return self._queue[actual_idx]

    def as_slices(self) -> tuple[list[T | None], list[T | None]]:
        if self.is_full:
            return self._queue[self._end + 1:self._capacity], self._queue[0:self._end + 1]
        return [], self._queue[0:self._len]


class MapOrAttrs:
    def __init__(self, beatmap=None, attrs=None):
        self._map = beatmap
        self._attrs = attrs

    @property
    def is_map(self) -> bool:
        return self._map is not None

    @property
    def is_attrs(self) -> bool:
        return self._attrs is not None

    def get_attrs(self):
        return self._attrs

    def set_attrs(self, attrs):
        self._attrs = attrs
        self._map = None