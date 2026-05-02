import math
from typing import TypeVar, Generic

T = TypeVar("T")
U = TypeVar("U")

EPSILON = 1e-7

def almost_eq(a: float, b: float, acceptable_difference: float = EPSILON) -> bool:
    return abs(a - b) <= acceptable_difference

def clamp(value: float, min_val: float, max_val: float) -> float:

    if value < min_val:
        return min_val
    if value > max_val:
        return max_val
    return value

def lerp(start: float, end: float, amount: float) -> float:
    return (start * (1.0 - amount)) + (end * amount)

def reverse_lerp(x: float, start: float, end: float) -> float:
    return clamp((x - start) / (end - start), 0.0, 1.0)

def bpm_to_milliseconds(bpm: float, delimiter: int = 4) -> float:
    return (60000.0 / delimiter) / bpm

def logistic(x: float, midpoint_offset: float, multiplier: float, max_value: float = 1.0) -> float:
    return max_value / (1.0 +  math.exp(multiplier * (midpoint_offset - x)))

def norm(p: float, values: list[float]) -> float:
    sum_pow = sum(math.pow(x, p) for x in values)
    return math.pow(sum_pow, 1.0 / p)

def smoothstep(x: float, start: float, end: float) -> float:
    x = reverse_lerp(x, start, end)
    return x * x * (3.0 - 2.0 * x)

def smootherstep(x: float, start: float, end: float) -> float:
    x = reverse_lerp(x, start, end)
    return x * x * x * (x * (6.0 * x - 15.0) + 10.0)

def erf_inv(x: float) -> float:
    if x <= -1.0:
        return float('-inf')
    if x >= 1.0:
        return float('inf')
    if almost_eq(x, 0.0):
        return 0.0

    A = 0.147
    sgn = 1.0 if x > 0 else -1.0
    x = abs(x)

    ln = math.log(1.0 - x * x)
    t1 = 2.0 / (math.pi * A) + ln / 2.0
    t2 = ln / A
    base_approx = math.sqrt(t1 * t1 - t2) - t1

    c = math.pow((x - 0.85) / 0.293, 8.0) if x >= 0.85 else 0.0

    return sgn * (math.sqrt(base_approx) + c)


class LimitedQueue(Generic[T]):
    __slots__ = ('_queue', 'capacity', 'end', '_len')

    def __init__(self, capacity: int, default_val: T = None):
        self.capacity = capacity
        self._queue = [default_val] * capacity
        self.end = capacity - 1
        self._len = 0

    def push(self, item: T) -> None:
        self.end = (self.end + 1) % self.capacity
        self._queue[self.end] = item
        if self._len < self.capacity:
            self._len += 1

    def __len__(self) -> int:
        return self._len

    @property
    def is_empty(self) -> bool:
        return self._len == 0

    @property
    def is_full(self) -> bool:
        return self._len == self.capacity

    @property
    def last(self) -> T | None:
        if self.is_empty:
            return None
        return self._queue[self.end]

    def __getitem__(self, idx: int) -> T:
        if self._len == self.capacity:
            real_idx = (idx + self.end + 1) % self.capacity
        else:
            real_idx = idx % self.capacity
        return self._queue[real_idx]