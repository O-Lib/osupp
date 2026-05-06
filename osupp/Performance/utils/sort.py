import math
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")
Comparer = Callable[[T, T], int]


def swap(keys: list[T], i: int, j: int) -> None:
    if i != j:
        keys[i], keys[j] = keys[j], keys[i]


def swap_if_greater(keys: list[T], comparer: Comparer, a: int, b: int) -> None:
    if a != b and comparer(keys[a], keys[b]) > 0:
        keys[a], keys[b] = keys[b], keys[a]


def down_heap(keys: list[T], i: int, n: int, lo: int, comparer: Comparer) -> None:
    while i <= n // 2:
        child = 2 * i
        if child < n and comparer(keys[lo + child - 1], keys[lo + child]) < 0:
            child += 1
        if comparer(keys[lo + i - 1], keys[lo + child - 1]) >= 0:
            break

        swap(keys, lo + i - 1, lo + child - 1)
        i = child


def heap_sort(keys: list[T], lo: int, hi: int, comparer: Comparer) -> None:
    n = hi - lo + 1
    for i in range(n // 2, 0, -1):
        down_heap(keys, i, n, lo, comparer)
    for i in range(n, 1, -1):
        swap(keys, lo, lo + i - 1)
        down_heap(keys, 1, i - 1, lo, comparer)


def csharp_sort(keys: list[T], comparer: Comparer) -> None:
    _introspective_sort(keys, 0, len(keys), comparer)


def _introspective_sort(keys: list[T], left: int, length: int, comparer: Comparer) -> None:
    if length >= 2:
        depth_limit = 2 * int(math.log2(len(keys))) if len(keys) > 0 else 0
        _intro_sort(keys, left, length + left - 1, depth_limit, comparer)


def _intro_sort(keys: list[T], lo: int, hi: int, depth_limit: int, comparer: Comparer) -> None:
    INTRO_SORT_SIZE_THRESHOLD = 16

    while hi > lo:
        partition_size = hi - lo + 1

        if partition_size <= INTRO_SORT_SIZE_THRESHOLD:
            if partition_size == 1:
                pass
            elif partition_size == 2:
                swap_if_greater(keys, comparer, lo, hi)
            elif partition_size == 3:
                swap_if_greater(keys, comparer, lo, hi - 1)
                swap_if_greater(keys, comparer, lo, hi)
                swap_if_greater(keys, comparer, hi - 1, hi)
            else:
                _insertion_sort(keys, lo, hi, comparer)
            break

        if depth_limit == 0:
            heap_sort(keys, lo, hi, comparer)
            break

        depth_limit -= 1
        p = _pick_pivot_and_partition(keys, lo, hi, comparer)
        _intro_sort(keys, p + 1, hi, depth_limit, comparer)
        hi = p - 1


def _pick_pivot_and_partition(keys: list[T], lo: int, hi: int, comparer: Comparer) -> int:
    mid = lo + (hi - lo) // 2
    swap_if_greater(keys, comparer, lo, mid)
    swap_if_greater(keys, comparer, lo, hi)
    swap_if_greater(keys, comparer, mid, hi)
    swap(keys, mid, hi - 1)

    left = lo
    right = hi - 1
    pivot_idx = right

    while left < right:
        left += 1
        while comparer(keys[left], keys[pivot_idx]) < 0:
            left += 1

        right -= 1
        while comparer(keys[pivot_idx], keys[right]) < 0:
            right -= 1

        if left >= right:
            break

        swap(keys, left, right)

    swap(keys, left, hi - 1)
    return left


def _insertion_sort(keys: list[T], lo: int, hi: int, comparer: Comparer) -> None:
    for i in range(lo, hi):
        t = keys[i + 1]
        shift = 0

        for j in range(i, lo - 1, -1):
            if comparer(t, keys[j]) < 0:
                shift += 1
            else:
                break

        if shift > 0:
            keys.insert(i + 1 - shift, keys.pop(i + 1))


QUICK_SORT_DEPTH_THRESHOLD = 32


def osu_legacy_sort(keys: list[T], comparer: Comparer) -> None:
    if len(keys) < 2:
        return
    _depth_limited_quick_sort(keys, 0, len(keys) - 1, comparer, QUICK_SORT_DEPTH_THRESHOLD)


def _depth_limited_quick_sort(keys: list[T], left: int, right: int, comparer: Comparer, depth_limit: int) -> None:
    while True:
        if depth_limit == 0:
            heap_sort(keys, left, right, comparer)
            return

        i = left
        j = right
        middle = i + ((j - i) >> 1)

        swap_if_greater(keys, comparer, i, middle)
        swap_if_greater(keys, comparer, i, j)
        swap_if_greater(keys, comparer, middle, j)

        while True:
            while comparer(keys[i], keys[middle]) < 0:
                i += 1
            while comparer(keys[middle], keys[j]) < 0:
                j -= 1

            if i < j:
                swap(keys, i, j)
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


class TandemSorter:
    __slots__ = ("indices", "should_reset")

    def __init__(self, keys: list[T], comparer: Comparer):
        from functools import cmp_to_key
        self.indices = list(range(len(keys)))
        self.indices.sort(key=cmp_to_key(lambda i, j: comparer(keys[i], keys[j])))
        self.should_reset = False

    @staticmethod
    def _toggle_mark_idx(idx: int) -> int:
        return ~idx

    def sort(self, slice_list: list[Any]) -> None:
        if self.should_reset:
            for i in range(len(self.indices)):
                self.indices[i] = self._toggle_mark_idx(self.indices[i])
            self.should_reset = False

        for i in range(len(self.indices)):
            i_idx = self.indices[i]

            if i_idx < 0:
                continue

            j = i
            j_idx = i_idx

            while j_idx != i:
                self.indices[j] = self._toggle_mark_idx(j_idx)
                swap(slice_list, j, j_idx)
                j = j_idx
                j_idx = self.indices[i]

            self.indices[j] = self._toggle_mark_idx(j_idx)

        self.should_reset = True
