import math
from dataclasses import dataclass
from typing import Generic, TypeVar

# KEY VALUE
# ----------------------------------------------------------------------------------
K = TypeVar("K")


class KeyValue(Generic[K]):
    __slots__ = ("key", "value")

    def __init__(self, key: K, value: str) -> None:
        self.key: K = key
        self.value: str = value

    @classmethod
    def parse(cls, s: str, key_type: type[K]) -> "KeyValue[K] | None":
        parts = [part.strip() for part in s.split(":", 1)]

        raw_key = parts[0] if parts else s.strip()
        raw_value = parts[1] if len(parts) > 1 else ""

        try:
            parsed_key = key_type(raw_key)
            return cls(key=parsed_key, value=raw_value)
        except (ValueError, TypeError, KeyError):
            return None


# ----------------------------------------------------------------------------------

# PARSE NUMBERS
# ----------------------------------------------------------------------------------

MAX_PARSE_VALUE = 2147483647


class ParseNumberError(Exception):
    InvalidFloat = "invalid float"
    InvalidInteger = "invalid integer"
    NaN = "not a number"
    Overflow = "value is too high"
    Underflow = "value is too low"

    def __init__(self, message: str):
        super().__init__(message)


def parse_with_limits(s: str, limit: int | float, target_type: type) -> int | float:
    try:
        n = target_type(s.strip())
    except ValueError:
        if target_type is int:
            raise ParseNumberError(ParseNumberError.InvalidInteger)
        raise ParseNumberError(ParseNumberError.InvalidFloat)

    if n < -limit:
        raise ParseNumberError(ParseNumberError.Underflow)

    if n > limit:
        raise ParseNumberError(ParseNumberError.Overflow)

    if isinstance(n, float) and math.isnan(n):
        raise ParseNumberError(ParseNumberError.NaN)

    return n


def parse_int(s: str) -> int:
    return parse_with_limits(s, int(MAX_PARSE_VALUE), int)


def parse_float(s: str) -> float:
    return parse_with_limits(s, float(MAX_PARSE_VALUE), float)


# ----------------------------------------------------------------------------------

# POS
# ----------------------------------------------------------------------------------


@dataclass(slots=True, eq=True)
class Pos:
    x: float = 0.0
    y: float = 0.0

    def length_squared(self) -> float:
        return self.dot(self)

    def length(self) -> float:
        return float(math.sqrt(self.x * self.x + self.y * self.y))

    def dot(self, other: "Pos") -> float:
        return (self.x * other.x) + (self.y * other.y)

    def distance(self, other: "Pos") -> float:
        return (self - other).length()

    def normalize(self) -> "Pos":
        length = self.length()
        if length == 0:
            return Pos(0.0, 0.0)

        scale = 1.0 / length
        return Pos(self.x * scale, self.y * scale)

    def __add__(self, other: "Pos") -> "Pos":
        return Pos(self.x + other.x, self.y + other.y)

    def __iadd__(self, other: "Pos") -> "Pos":
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other: "Pos") -> "Pos":
        return Pos(self.x - other.x, self.y - other.y)

    def __isub__(self, other: "Pos") -> "Pos":
        self.x -= other.x
        self.y -= other.y
        return self

    def __mul__(self, other: float) -> "Pos":
        return Pos(self.x * other, self.y * other)

    def __imul__(self, other: float) -> "Pos":
        self.x *= other
        self.y *= other
        return self

    def __truediv__(self, other: float) -> "Pos":
        return Pos(self.x / other, self.y / other)

    def __itruediv__(self, other: float) -> "Pos":
        self.x /= other
        self.y /= other
        return self

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"Pos(x={self.x}, y={self.y})"


# ----------------------------------------------------------------------------------


# STR EXTRA
# ----------------------------------------------------------------------------------
def trim_comment(s: str) -> str:
    index = s.find("//")
    if index == -1:
        return s.strip()
    return s[:index].rstrip()


def to_standardized_path(s: str) -> str:
    return s.replace("\\", "/")


def clean_filename(s: str) -> str:
    cleaned = s.strip('"')
    cleaned = cleaned.replace("\\\\", "\\")
    return to_standardized_path(cleaned)


# ----------------------------------------------------------------------------------
