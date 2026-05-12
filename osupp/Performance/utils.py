"""
MIT License

Copyright (c) 2026-Present O!Lib Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys
import math
from typing import Protocol, Generic, TypeVar, Any
from collections import deque
from collections.abc import Callable

EPSILON: float = sys.float_info.epsilon
T = TypeVar("T")

class BeatmapAttributesProtocol(Protocol):
    def hp(self) -> float: ...
    def od(self) -> float: ...
    def cs(self) -> float: ...

def calculate_difficulty_peppy_stars(
        map_attrs: BeatmapAttributesProtocol,
        object_count: int,
        drain_len: int
) -> int:
    if drain_len != 0:
        object_to_drain_ratio = clamp((float(object_count) / float(drain_len)) * 8.0, 0.0, 16.0)
    else:
        object_to_drain_ratio = 16.0

    drain_rate = float(map_attrs.hp())
    overall_difficulty = float(map_attrs.od())
    circle_size = float(map_attrs.cs())

    return int(round((drain_rate + overall_difficulty + circle_size + object_to_drain_ratio) / 38.0 * 5.0))

def almost_eq(a: float, b: float, acceptable_difference: float) -> bool:
    return abs(a - b) <= acceptable_difference

def eq(a: float, b: float) -> bool:
    return almost_eq(a, b, EPSILON)

def not_eq(a: float, b: float) -> bool:
    return abs(a - b) >= EPSILON

def lerp(value1: float, value2: float, amount: float) -> float:
    return (value1 * (1.0 - amount)) + (value2 * amount)

def bpm_to_milliseconds(bpm: float, delimiter: int | None = None) -> float:
    d = delimiter if delimiter is not None else 4
    return (60000.0 / d) / bpm

def millisecods_to_bpm(ms: float, delimiter: int | None = None) -> float:
    d = delimiter if delimiter is not None else 4
    return 60000.0 / (ms * d)

def logistic(x: float, midpoint_offset: float, multiplier: float, max_value: float | None = None) -> float:
    m = max_value if max_value is not None else 1.0
    return m / (1.0 + math.exp(multiplier * (midpoint_offset - x)))

def logistic_exp(exp: float, max_value: float | None = None) -> float:
    m = max_value if max_value is not None else 1.0
    return m / (1.0 + math.exp(exp))

def norm(p: float, values: list[float]) -> float:
    return sum(math.pow(x, p) for x in values) ** (1.0 / p)

def bell_curve(x: float, mean: float, width: float, multiplier: float | None = None) -> float:
    m = multiplier if multiplier is not None else 1.0
    return m * math.exp(math.e * -(math.pow(x - mean, 2.0) / math.pow(width, 2.0)))

def smoothstep_bell_curve(x: float, mean: float, width: float) -> float:
    new_x = x - mean
    if new_x > 0.0:
        new_x = width - new_x
    else:
        new_x = width +  new_x
    return smoothstep(new_x, 0.0, width)

def smoothstep(x: float, start: float, end: float) -> float:
    x = reverse_lerp(x, start, end)
    return x * x * (3.0 - 2.0 * x)

def smootherstep(x: float, start: float, end: float) -> float:
    x = reverse_lerp(x, start, end)
    return x * x * x * (x * (6.0 * x - 15.0) + 10.0)

def reverse_lerp(x: float, start: float, end: float) -> float:
    return max(0.0, min(1.0, (x - start) / (end - start)))

def erf(x: float) -> float:
    if eq(x, 0.0):
        return 0.0

    if math.isinf(x):
        if x > 0.0:
            return 1.0
        if x < 0.0:
            return -1.0

    if math.isnan(x):
        return math.nan

    t = 1.0 / (1.0 + 0.3275911 * abs(x))
    tau = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))))
    erf_val = 1.0 - tau * math.exp(-x * x)

    return erf_val if x >= 0.0 else -erf_val

def erf_inv(x: float) -> float:
    if x <= -1.0:
        return -math.inf
    if x >= 1.0:
        return math.inf

    if eq(x, 0.0):
        return 0.0

    A = 0.147
    sgn = math.copysign(1.0, x)
    x = abs(x)

    ln = math.log(1.0 - x * x)
    t1 = 2.0 / (math.pi * A) + ln / 2.0
    t2 = ln / A
    base_approx = math.sqrt(t1 * t1 - t2) - t1

    c = math.pow((x - 0.85) / 0.293, 8.0) if x >= 0.85 else 0.0

    return sgn * (math.sqrt(base_approx) + c)

def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))

def get_precision_adjusted_beat_len(slider_velocity_multiplier: float, beat_len: float) -> float:
    slider_velocity_as_beat_len = -100.0 / slider_velocity_multiplier

    if slider_velocity_as_beat_len < 0.0:
        bpm_multiplier = clamp(-slider_velocity_as_beat_len, 10.0, 10000.0) / 100.0
    else:
        bpm_multiplier = 1.0

    return beat_len * bpm_multiplier

class LimitedQueue(Generic[T]):
    __slots__ = ("_queue",)

    def __init__(self, capacity: int) -> None:
        self._queue: deque[T] = deque(maxlen=capacity)

    def push(self, elem: T) -> None:
        self._queue.append(elem)

    def is_empty(self) -> bool:
        return not self._queue

    def is_full(self) -> bool:
        return len(self._queue) == self._queue.maxlen

    def __len__(self) -> int:
        return len(self._queue)

    def __getitem__(self, idx: int) -> T:
        return self._queue[idx]

    def last(self) -> T | None:
        return self._queue[-1] if self._queue else None

    def as_list(self) -> list[T]:
        return list(self._queue)

U32_MASK: int = 0xFFFFFFFF
INT_MASK: int = 0x7FFFFFFF
INT_MAX: int = 2147483647
INT_TO_REAL: float = 1.0 / (float(INT_MAX) + 1.0)

class OsuRandom:
    __slots__ = ("x", "y", "z", "w", "bit_buf", "bit_idx")

    def __init__(self, seed: int) -> None:
        self.x: int = seed & U32_MASK
        self.y: int = 842502087
        self.z: int = 3579807591
        self.w: int = 273326509
        self.bit_buf: int = 0
        self.bit_idx: int = 32

    def gen_unsigned(self) -> int:
        t = (self.x ^ ((self.x << 11) & U32_MASK)) & U32_MASK
        self.x = self.y
        self.y = self.z
        self.z = self.w
        self.w = (self.w ^ (self.w >> 19) ^ t ^ (t >> 8)) & U32_MASK

        return self.w

    def next_int(self) -> int:
        return INT_MASK & self.gen_unsigned()

    def next_double(self) -> float:
        return INT_TO_REAL * float(self.next_int())

    def next_int_range(self, minimum: int, maximum: int) -> int:
        return int(float(minimum) + self.next_double() * float(maximum - minimum))

    def next_double_range(self, minimum: float, maximum: float) -> int:
        return int(minimum + self.next_double() * (maximum - minimum))

    def next_bool(self) -> bool:
        if self.bit_idx == 32:
            self.bit_buf = self.gen_unsigned()
            self.bit_idx = 1
        else:
            self.bit_idx += 1
            self.bit_buf >>= 1

        return (self.bit_buf & 1) == 1

def _wrap_int(value: int) -> int:
    value &= U32_MASK
    return value - 0x100000000 if value & 0x80000000 else value

class CSharpRandom:
    __slots__ = ("seed_array", "inext", "inextp")

    def __init__(self, seed: int) -> None:
        self.seed_array: list[int] = [0] * 56
        self.inext: int = 0
        self.inextp: int = 21

        subtraction = INT_MAX if seed == -2147483648 else abs(seed)

        mj = 161803398 - subtraction
        self.seed_array[55] = mj

        mk = 1
        ii = 0

        for _ in range(1, 55):
            ii += 21
            if ii >= 55:
                ii -= 55

            self.seed_array[ii] = mk
            mk = mj - mk
            if mk < 0:
                mk += INT_MAX

            mj = self.seed_array[ii]

        for _ in range(1, 5):
            for i in range(1, 56):
                n = i + 30
                if n >= 55:
                    n -= 55

                self.seed_array[i] = _wrap_int(self.seed_array[i] - self.seed_array[1 + n])

                if self.seed_array[i] < 0:
                    self.seed_array[i] += INT_MAX

    def next(self) -> int:
        return self._internal_sample()

    def next_max(self, maximum: int) -> int:
        return int(self._sample() * float(maximum))

    def _sample(self) -> float:
        return float(self._internal_sample()) * (1.0 / float(INT_MAX))

    def _internal_sample(self) -> int:
        loc_inext = self.inext + 1
        if loc_inext >= 56:
            loc_inext = 1

        loc_inextp = self.inextp + 1
        if loc_inextp >= 56:
            loc_inextp = 1

        ret_val = self.seed_array[loc_inext] - self.seed_array[loc_inextp]

        if ret_val == INT_MAX:
            ret_val -= 1

        if ret_val < 0:
            ret_val += INT_MAX

        self.seed_array[loc_inext] = ret_val
        self.inext = loc_inext
        self.inextp = loc_inextp

        return ret_val

def _swap(keys: list[T], i: int, j: int) -> None:
    if i != j:
        keys[i], keys[j] = keys[j], keys[i]

def _swap_if_greater(keys: list[T], comparer: Callable[[T, T], int], a: int, b: int) -> None:
    if a != b and comparer(keys[a], keys[b]) > 0:
        keys[a], keys[b] = keys[b], keys[a]

def _down_heap(keys: list[T], i: int, n: int, lo: int, comparer: Callable[[T, T], int]) -> None:
    while i <= n // 2:
        child = 2 * i

        if child < n and comparer(keys[lo + child - 1], keys[lo + child]) < 0:
            child = 2 * i

        if comparer(keys[lo + i - 1], keys[lo + child - 1]) >= 0:
            break

        keys[lo + i - 1], keys[lo + child - 1] = keys[lo + child - 1], keys[lo + i - 1]
        i = child

def _heap_sort(keys: list[T], lo: int, hi: int, comparer: Callable[[T, T], int]) -> None:
    n = hi - lo + 1
    for i in range(n // 2, 0, -1):
        _down_heap(keys, i, n, lo, comparer)

    for i in range(n, 1, -1):
        _swap(keys, lo, lo + i - 1)
        _down_heap(keys, 1, i - 1, lo, comparer)

QUICK_SORT_DEPTH_THRESHOLD: int = 32

def _depth_limited_quick_sort(
        keys: list[T],
        left: int,
        right: int,
        comparer: Callable[[T, T], int],
        depth_limit: int
) -> None:
    while True:
        if depth_limit == 0:
            _heap_sort(keys, left, right, comparer)
            return

        i = left
        j = right
        middle = i + ((j - i) >> 1)

        _swap_if_greater(keys, comparer, i, middle)
        _swap_if_greater(keys, comparer, i, j)
        _swap_if_greater(keys, comparer, middle, j)

        while True:
            while comparer(keys[i], keys[middle]) < 0:
                i += 1

            while comparer(keys[middle], keys[j]) < 0:
                j -= 1

            if i < j:
                keys[i], keys[j] = keys[j], keys[i]
            elif i > j:
                break

            i += 1
            j = max(0, j - 1)

            if i > j:
                break

        depth_limit -= 1

        if max(0, j - left) <= right - i:
            if left < j:
                _depth_limited_quick_sort(keys, left, j, comparer, depth_limit)
            left = i
        else:
            if i < right:
                _depth_limited_quick_sort(keys, i, right, comparer, depth_limit)
            right = j

        if left >= right:
            break

def osu_legacy_sort(keys: list[T], comparer: Callable[[T, T], int]) -> None:
    if len(keys) < 2:
        return

    _depth_limited_quick_sort(keys, 0, len(keys) - 1, comparer, QUICK_SORT_DEPTH_THRESHOLD)

def _insertion_sort(keys: list[T], lo: int, hi: int, cmp: Callable[[T, T], int]) -> None:
    for i in range(lo, hi):
        t = keys[i + 1]
        j = i
        while j >= lo and cmp(t, keys[j]) < 0:
            keys[j + 1] = keys[j]
            j -= 1
        keys[j + 1] = t

def _pick_pivot_and_partition(keys: list[T], lo: int, hi: int, cmp: Callable[[T, T], int]) -> int:
    mid = lo + (hi - lo) // 2
    _swap_if_greater(keys, cmp, lo, mid)
    _swap_if_greater(keys, cmp, lo, hi)
    _swap_if_greater(keys, cmp, mid, hi)
    _swap(keys, mid, hi - 1)

    left = lo
    right = hi - 1
    pivot_idx = right

    while left < right:
        while True:
            left += 1
            if cmp(keys[left], keys[pivot_idx]) >= 0:
                break

        while True:
            right -= 1
            if cmp(keys[pivot_idx], keys[right]) >= 0:
                break

        if left >= right:
            break

        _swap(keys, left, right)

    _swap(keys, left, hi - 1)
    return left

def _intro_sort(keys: list[T], lo: int, hi: int, depth_limit: int, cmp: Callable[[T, T], int]) -> None:
    INTRO_SORT_SIZE_THRESHOLD: int = 16

    while hi > lo:
        partition_size = hi - lo + 1

        if partition_size <= INTRO_SORT_SIZE_THRESHOLD:
            if partition_size == 1:
                pass
            elif partition_size == 2:
                _swap_if_greater(keys, cmp, lo, hi)
            elif partition_size == 3:
                _swap_if_greater(keys, cmp, lo, hi - 1)
                _swap_if_greater(keys, cmp, lo, hi)
                _swap_if_greater(keys, cmp, hi - 1, hi)
            else:
                _insertion_sort(keys, lo, hi, cmp)
            break

        if depth_limit == 0:
            _heap_sort(keys, lo, hi, cmp)
            break

        depth_limit -= 1
        p = _pick_pivot_and_partition(keys, lo, hi, cmp)
        _intro_sort(keys, p + 1, hi, depth_limit, cmp)
        hi = p - 1

def _introspective_sort(keys: list[T], left: int, length: int, cmp: Callable[[T, T], int]) -> None:
    if length >= 2:
        depth_limit = 2 * (len(keys).bit_length() - 1)
        _intro_sort(keys, left, length + left - 1, depth_limit, cmp)

def csharp_sort(keys: list[T], comparer: Callable[[T, T], int]) -> None:
    if len(keys) < 2:
        return
    _introspective_sort(keys, 0, len(keys), comparer)

class TandemSorter:
    __slots__ = ("indices", "should_reset")

    def __init__(self, slice_data: list[Any], cmp: Callable[[Any, Any], int]) -> None:
        self.indices: list[int] = list(range(len(slice_data)))
        self.should_reset: bool = False

        def index_cmp(i: int, j: int) -> int:
            res = cmp(slice_data[i], slice_data[j])
            if res == 0:
                return (i > j) - (i < j)
            return res

        csharp_sort(self.indices, index_cmp)

    def sort(self, slice_data: list[Any]) -> None:
        if self.should_reset:
            self._toggle_marks()
            self.should_reset = False

        for i in range(len(self.indices)):
            i_idx = self.indices[i]

            if self._idx_is_marked(i_idx):
                continue

            j = i
            j_idx = i_idx

            while j_idx != i:
                self.indices[j] = self._toggle_mark_idx(j_idx)
                slice_data[j], slice_data[j_idx] = slice_data[j_idx], slice_data[j]
                j = j_idx
                j_idx = self.indices[j]

            self.indices[j] = self._toggle_mark_idx(j_idx)

        self.should_reset = True

    def _toggle_marks(self) -> None:
        for idx in range(len(self.indices)):
            self.indices[idx] = self._toggle_mark_idx(self.indices[idx])

    @staticmethod
    def _idx_is_marked(idx: int) -> bool:
        return idx < 0

    @staticmethod
    def _toggle_mark_idx(idx: int) -> int:
        return ~idx