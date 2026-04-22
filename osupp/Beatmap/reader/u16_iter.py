from __future__ import annotations

class DoubleByteInterator:
    __slots__ = ("_bytes", "_index")

    def __init__(self, bytes_data: bytes):
        self._bytes = bytes_data
        self._index = 0

    @classmethod
    def new(cls, bytes_data: bytes) -> DoubleByteInterator:
        return cls(bytes_data)

    def __iter__(self) -> DoubleByteInterator:
        return self

    def __next__(self) -> tuple[int, int]:
        if self._index + 1 < len(self._bytes):
            a = self._bytes[self._index]
            b = self._bytes[self._index + 1]

            self._index += 2

            return (a, b)
        raise StopIteration

    def size_hint(self) -> tuple[int, int | None]:
        remaining_bytes = len(self._bytes) - self._index
        length = remaining_bytes // 2

        return (length, length)

class U16BeInterator:
    __slots__ = ("_inner",)

    def __init__(self, inner: DoubleByteInterator):
        self._inner = inner

    @classmethod
    def new(cls, bytes_data: bytes) -> U16BeInterator:
        return cls(DoubleByteInterator.new(bytes_data))

    def __iter__(self) -> U16BeInterator:
        return self

    def __next__(self) -> int:
        pair = next(self._inner, None)

        if pair is None:
            raise StopIteration

        b1, b2 = pair
        return (b1 << 8) | b2

    def size_hint(self) -> tuple[int, int | None]:
        return self._inner.size_hint()

class U16LeInterator:
    __slots__ = ("_inner",)

    def __init__(self, inner: DoubleByteInterator):
        self._inner = inner

    @classmethod
    def new(cls, bytes_data: bytes) -> U16BeInterator:
        return cls(DoubleByteInterator.new(bytes_data))

    def __iter__(self) -> U16LeInterator:
        return self

    def __next__(self) -> int:
        pair = next(self._inner, None)

        if pair is None:
            raise StopIteration

        b1, b2 = pair
        return (b2 << 8) | b1

    def size_hint(self) -> tuple[int, int | None]:
        return self._inner.size_hint()