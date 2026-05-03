import math
from typing import TypeVar, Generic

EPSILON = 1e-7

def almost_eq(a: float, b: float, acceptable_difference: float = EPSILON) -> bool:
    return abs(a - b) <= acceptable_difference

def lerp(value1: float, value2: float, amount: float) -> float:
    return (value1 * (1.0 - amount)) + (value2 * amount)

def bpm_to_milliseconds(bpm: float, delimiter: int = 4) -> float:
    return 60000.0 / delimiter / bpm

def milliseconds_to_bpm(ms: float, delimiter: int = 4) -> float:
    if ms == 0:
        return 0.0
    return 60000.0 / (ms * delimiter)

def logistic(x: float, midpoint_offset: float, multiplier: float, max_value: float = 1.0) -> float:
    try:
        exp_val = math.exp(multiplier * (midpoint_offset - x))
    except OverflowError:
        exp_val = float('inf')
    return max_value / (1.0 + exp_val)

def reverse_lerp(x: float, start: float, end: float) -> float:
    if start == end:
        return 0.0
    val = (x - start) / (end - start)
    return max(0.0, min(1.0, val))

def smoothstep(x: float, start: float, end: float) -> float:
    t = reverse_lerp(x, start, end)
    return t * t * (3.0 - 2.0 * t)

def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, value))


T = TypeVar("T")

class LimitedQueue(Generic[T]):
    __slots__ = ("_queue", "_end", "_len", "_capacity")

    def __init__(self, capacity: int, default_val: T = None):
        if capacity <= 0:
            raise ValueError("The capacity must be greater than zero.")
        self._capacity = capacity
        self._queue = [default_val for _ in range(capacity)]
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

    def __getitem__(self, idx: int) -> T:
        if idx < 0 or idx >= self._len:
            raise IndexError("Index outside the bounds of the array.")

        actual_idx = (idx + (1 if self.is_full else 0) * (self._end + 1)) % self._capacity
        return self._queue[actual_idx]