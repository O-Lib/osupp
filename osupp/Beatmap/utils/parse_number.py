import math
from typing import Protocol, TypeVar, Union, runtime_checkable

MAX_PARSE_VALUE: int = 2147483647  # 2,147,483,647

T = TypeVar("T", bound="ParseNumber")
V = Union[int, float]

# ------------------------------------------------------------------


@runtime_checkable
class ParseNumber(Protocol):
    @classmethod
    def parse(cls: type[T], s: str) -> V: ...

    @classmethod
    def parse_with_limits(cls: type[T], s: str, limit: V) -> V: ...


# ------------------------------------------------------------------


class Int32:
    @classmethod
    def parse(cls, s: str) -> int:
        return cls.parse_with_limits(s, MAX_PARSE_VALUE)

    @classmethod
    def parse_with_limits(cls, s: str, limit: int) -> int:
        s_stripped = s.strip()
        if not s_stripped or "nan" in s_stripped.lower():
            raise InvalidInteger(
                ValueError("Cannot convert NaN or empty string to Int32")
            )

        try:
            n = int(s_stripped)
        except ValueError as e:
            raise InvalidInteger(e)

        if n < -limit:
            raise NumberUnderflow()
        elif n > limit:
            raise NumberOverflow()
        else:
            return n


# ------------------------------------------------------------------


class Float32:
    @classmethod
    def parse(cls, s: str) -> float:
        return cls.parse_with_limits(s, float(MAX_PARSE_VALUE))

    @classmethod
    def parse_with_limits(cls, s: str, limit: float) -> float:
        s_stripped = s.strip()
        if not s_stripped or "nan" in s_stripped.lower():
            raise InvalidInteger(
                ValueError("Cannot convert NaN or empty string to Int32")
            )

        try:
            n = float(s_stripped)
        except ValueError as e:
            raise InvalidFloat(e)

        if n < -limit:
            raise NumberUnderflow()
        elif n > limit:
            raise NumberOverflow()
        elif math.isnan(n):
            raise NaN()
        else:
            return n


# ------------------------------------------------------------------


class Float64:
    @classmethod
    def parse(cls, s: str) -> float:
        return cls.parse_with_limits(s, float(MAX_PARSE_VALUE))

    @classmethod
    def parse_with_limits(cls, s: str, limit: float) -> float:
        s_stripped = s.strip()
        if not s_stripped or "nan" in s_stripped.lower():
            raise InvalidInteger(
                ValueError("Cannot convert NaN or empty string to Int32")
            )

        try:
            n = float(s_stripped)
        except ValueError as e:
            raise InvalidFloat(e)

        if n < -limit:
            raise NumberUnderflow()
        elif n > limit:
            raise NumberOverflow()
        elif math.isnan(n):
            raise NaN()
        else:
            return n


# ------------------------------------------------------------------


class ParseNumberError(Exception):
    pass


class InvalidFloat(ParseNumberError):
    def __init__(self, source: Exception):
        self.source = source
        super().__init__("invalid float")


class InvalidInteger(ParseNumberError):
    def __init__(self, source: Exception):
        self.source = source
        super().__init__("invalid integer")


class NaN(ParseNumberError):
    def __init__(self):
        super().__init__("not a number")


class NumberOverflow(ParseNumberError):
    def __init__(self):
        super().__init__("value is too high")


class NumberUnderflow(ParseNumberError):
    def __init__(self):
        super().__init__("value is too low")


# ------------------------------------------------------------------
