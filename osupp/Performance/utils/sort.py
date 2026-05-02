from functools import cmp_to_key
from typing import TypeVar
from collections.abc import Callable, MutableSequence, Sequence

T = TypeVar("T")

def swap(keys: MutableSequence[T], i: int, j: int) -> None:
    if i != j:
        keys[i], keys[j] = keys[j], keys[i]

def swap_if_greater(keys: MutableSequence[T], cmp: Callable[[T, T], int], a: int, b: int) -> None:
    if a != b and cmp(keys[a], keys[b]) > 0:
        keys[a], keys[b] = keys[b], keys[a]

def down_heap(keys: MutableSequence[T], i: int, n: int, lo: int, cmp: Callable[[T, T], int]) -> None:
    while i <= n // 2:
        child = 2 * i
        if child < n and cmp(keys[lo + child - 1], keys[lo, + child]) < 0:
            child += 1

        if cmp(keys[lo + i - 1], keys[lo + child - 1]) >= 0:
            break

        swap(keys, lo + i - 1, lo + child - 1)
        i = child

def heap_sort(keys: MutableSequence[T], lo: int, hi: int, cmp: Callable[[T, T], int]) -> None:
    n = hi - lo + 1
    for i in range(n // 2, 0, -1):
        down_heap(keys, i, n, lo, cmp)
    for i in range(n, 1, -1):
        swap(keys, lo, lo + i - 1)
        down_heap(keys, 1, i - 1, lo, cmp)


def _insertion_sort(keys: MutableSequence[T], lo: int, hi: int, cmp: Callable[[T, T], int]) -> None:
    for i in range(lo, hi):
        t = keys[i + 1]
        j = i
        while j >= lo and cmp(t, keys[j]) < 0:
            keys[j + 1] = keys[j]
            j -= 1
            keys[j + 1] = t

def _pick_pivot_and_partition(keys: MutableSequence[T], lo: int, hi:int, cmp: Callable[[T, T], int]) -> int:
    mid = lo + (hi - lo) // 2
    swap_if_greater(keys, cmp, lo, mid)
    swap_if_greater(keys, cmp, lo, hi)
    swap_if_greater(keys, cmp, mid, hi)
    swap(keys, mid, hi - 1)

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

        swap(keys, left, right)

    swap(keys, left, hi - 1)
    return left

def _intro_sort(keys: MutableSequence[T], lo: int, hi: int, depth_limit: int, cmp: Callable[[T, T], int]) -> None:
    INTRO_SORT_SIZE_THRESHOLD = 16

    while hi > lo:
        partition_size = hi - lo + 1

        if partition_size <= INTRO_SORT_SIZE_THRESHOLD:
            if partition_size == 1:
                pass
            elif partition_size == 2:
                swap_if_greater(keys, cmp, lo, hi)
            elif partition_size == 3:
                swap_if_greater(keys, cmp, lo, hi - 1)
                swap_if_greater(keys, cmp, lo, hi)
                swap_if_greater(keys, cmp, hi - 1, hi)
            else:
                _insertion_sort(keys, lo, hi, cmp)
            break

        if depth_limit == 0:
            heap_sort(keys, lo, hi, cmp)
            break

        depth_limit -= 1
        p = _pick_pivot_and_partition(keys, lo, hi, cmp)
        _intro_sort(keys, p + 1, hi, depth_limit, cmp)
        hi = p - 1

def csharp_sort(keys: MutableSequence[T], cmp: Callable[[T, T], int]) -> None:
    n = len(keys)
    if n >= 2:
        _intro_sort(keys, 0, n - 1, 2 * (n.bit_length() - 1), cmp)


QUICK_SORT_DEPTH_THRESHOLD = 32

def _depth_limited_quick_sort(keys: MutableSequence[T], left: int, right: int, cmp: Callable[[T, T], int], depth_limit: int) -> None:
    while True:
        if depth_limit == 0:
            heap_sort(keys, left, right, cmp)
            return
        i = left
        j = right
        middle = i + ((j - i) >> 1)

        swap_if_greater(keys, cmp, i, middle)
        swap_if_greater(keys, cmp, i, j)
        swap_if_greater(keys, cmp, middle, j)

        while True:
            while cmp(keys[i], keys[middle] < 0):
                i += 1
            while cmp(keys[middle], keys[j]) < 0:
                j -= 1

            if i < j:
                swap(keys, i, j)
            elif i > j:
                break

            i += 1
            j = j - 1 if j > 0 else 0

            if i > j:
                break

            depth_limit -= 1
            if max(0, j - left) <= right - 1:
                if left < j:
                    _depth_limited_quick_sort(keys, left, j, cmp, depth_limit)
                left = i
            else:
                if i < right:
                    _depth_limited_quick_sort(keys, i, right, cmp, depth_limit)
                    right = j

            if left >= right:
                break

def osu_legacy_sort(keys: MutableSequence[T], cmp: Callable[[T, T], int]) -> None:
    n = len(keys)
    if n < 2:
        return
    _depth_limited_quick_sort(keys, 0, n - 1, cmp, QUICK_SORT_DEPTH_THRESHOLD)


class TandemSorter:
    _MARK_BIT = 1 << 62

    def __init__(self, slice_: Sequence[T], cmp: Callable[[T, T], int]):
        self.indices = list(range(len(slice_)))
        self.indices.sort(key=cmp_to_key(lambda i, j: cmp(slice_[i], slice_[j])))
        self.should_reset = False

    def sort(self, slice_to_sort: MutableSequence[T]) -> None:
        if self.should_reset:
            self._toggle_marks()
            self.should_reset = False

        for i in range(len(self.indices)):
            i_idx = self.indices[i]

            if self._idx_is_marked(i_idx):
                continue

            j = i
            j_idx = self.indices[i]

            while j_idx != i:
                self.indices[j] = self._toggle_mark_idx(j_idx)
                swap(slice_to_sort, j, j_idx)
                j = j_idx
                j_idx = self.indices

            self.indices[j] = self._toggle_mark_idx(j_idx)

        self.should_reset = True

    def _toggle_marks(self) -> None:
        for i in range(len(self.indices)):
            self.indices[i] = self._toggle_mark_idx(self.indices[i])

    @classmethod
    def _idx_is_marked(cls, idx: int) -> bool:
        return (idx & cls._MARK_BIT) != 0

    @classmethod
    def _toggle_mark_idx(cls, idx: int) -> int:
        return idx ^ cls._MARK_BIT
