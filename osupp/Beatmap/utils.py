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

import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

K = TypeVar("K")


class KeyValue(Generic[K]):
    """A parsed key: value pair from an osu! beatmap section line."""
    __slots__ = ("key", "value")

    def __init__(self, key: K, value: str) -> None:
        """Initialise with a parsed key and raw value string.

        Args:
            key: The parsed key.
            value: The raw value string.
        """
        self.key: K = key
        self.value: str = value

    @classmethod
    def parse(cls, s: str, key_type: Callable[[str], K]) -> "KeyValue[K] | None":
        """Attempt to parse a ``key: value`` line.

        Args:
            s: A single trimmed line from a beatmap section.
            key_type: Callable that converts the raw key string to K.

        Returns:
            A KeyValue instance, or ``None`` if the key is unknown.
        """
        parts = [part.strip() for part in s.split(":", 1)]

        raw_key = parts[0] if parts else s.strip()
        raw_value = parts[1] if len(parts) > 1 else ""

        try:
            parsed_key = key_type(raw_key)
            return cls(key=parsed_key, value=raw_value)
        except (ValueError, TypeError, KeyError):
            return None


MAX_PARSE_VALUE = 2147483647

T_Num = TypeVar("T_Num", int, float)


class ParseNumberError(Exception):
    """Raised when a numeric string cannot be parsed within the allowed range."""
    InvalidFloat = "invalid float"
    InvalidInteger = "invalid integer"
    NaN = "not a number"
    Overflow = "value is too high"
    Underflow = "value is too low"

    def __init__(self, message: str):
        """Initialise with an error message.

        Args:
            message: Description of the parse failure.
        """
        super().__init__(message)


def parse_with_limits(s: str, limit: int | float, target_type: type[T_Num]) -> T_Num:
    """Parse a numeric string and enforce magnitude limits.

    Args:
        s: The raw string to parse.
        limit: Maximum absolute value (inclusive).
        target_type: Either ``int`` or ``float``.

    Returns:
        The parsed number as target_type.

    Raises:
        ParseNumberError: If the string is invalid, out of range, or NaN.
    """
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
    """Parse a string as a 32-bit signed integer.

    Args:
        s: The raw string to parse.

    Returns:
        The parsed integer value.

    Raises:
        ParseNumberError: If parsing fails or the value is out of range.
    """
    return parse_with_limits(s, int(MAX_PARSE_VALUE), int)


def parse_float(s: str) -> float:
    """Parse a string as a float within the 32-bit signed integer magnitude range.

    Args:
        s: The raw string to parse.

    Returns:
        The parsed float value.

    Raises:
        ParseNumberError: If parsing fails, the value is out of range, or NaN.
    """
    return parse_with_limits(s, float(MAX_PARSE_VALUE), float)



@dataclass(slots=True, eq=True)
class Pos:
    """A 2-D position in osu! pixel space."""
    x: float = 0.0
    y: float = 0.0

    def length_squared(self) -> float:
        """Return the squared Euclidean length of this vector."""
        return self.dot(self)

    def length(self) -> float:
        """Return the Euclidean length of this vector."""
        return float(math.sqrt(self.x * self.x + self.y * self.y))

    def dot(self, other: "Pos") -> float:
        """Compute the dot product with another position vector.

        Args:
            other: The other Pos.

        Returns:
            The scalar dot product.
        """
        return (self.x * other.x) + (self.y * other.y)

    def distance(self, other: "Pos") -> float:
        """Return the Euclidean distance to another position.

        Args:
            other: The target Pos.

        Returns:
            The distance as a float.
        """
        return (self - other).length()

    def normalize(self) -> "Pos":
        """Return a unit vector in the direction of this position.

        Returns:
            A Pos with length 1.0, or Pos(0, 0) if the length is zero.
        """
        length = self.length()
        if length == 0:
            return Pos(0.0, 0.0)

        scale = 1.0 / length
        return Pos(self.x * scale, self.y * scale)

    def __add__(self, other: "Pos") -> "Pos":
        """Return the element-wise sum of two positions."""
        return Pos(self.x + other.x, self.y + other.y)

    def __iadd__(self, other: "Pos") -> "Pos":
        """Add another position in-place."""
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other: "Pos") -> "Pos":
        """Return the element-wise difference of two positions."""
        return Pos(self.x - other.x, self.y - other.y)

    def __isub__(self, other: "Pos") -> "Pos":
        """Subtract another position in-place."""
        self.x -= other.x
        self.y -= other.y
        return self

    def __mul__(self, other: float) -> "Pos":
        """Return this position scaled by a scalar."""
        return Pos(self.x * other, self.y * other)

    def __imul__(self, other: float) -> "Pos":
        """Scale this position in-place."""
        self.x *= other
        self.y *= other
        return self

    def __truediv__(self, other: float) -> "Pos":
        """Return this position divided by a scalar."""
        return Pos(self.x / other, self.y / other)

    def __itruediv__(self, other: float) -> "Pos":
        """Divide this position in-place."""
        self.x /= other
        self.y /= other
        return self

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        """Return an unambiguous string representation."""
        return f"Pos(x={self.x}, y={self.y})"


def trim_comment(s: str) -> str:
    """Strip an inline ``//`` comment and surrounding whitespace.

    Args:
        s: A raw beatmap line.

    Returns:
        The content before the first ``//``, right-stripped.
    """
    index = s.find("//")
    if index == -1:
        return s.strip()
    return s[:index].rstrip()


def to_standardized_path(s: str) -> str:
    """Normalise a file path to use forward slashes.

    Args:
        s: A raw file path string.

    Returns:
        The path with backslashes replaced by forward slashes.
    """
    return s.replace("\\", "/")


def clean_filename(s: str) -> str:
    """Clean a filename value as stored in a beatmap file.

    Args:
        s: The raw filename string.

    Returns:
        The cleaned filename with standardised path separators.
    """
    cleaned = s.strip('"')
    cleaned = cleaned.replace("\\\\", "\\")
    return to_standardized_path(cleaned)
