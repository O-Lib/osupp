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

from __future__ import annotations

from dataclasses import dataclass, field

from .acronym import Acronym


class SettingSimple:
    """A typed wrapper around a single mod setting value (bool, float, or str)."""
    __slots__ = ("_value",)

    def __init__(self, value: bool | float | str) -> None:
        """Initialise with a raw setting value.

        Args:
            value: The setting value. Must be bool, float, or str.
        """
        self._value = value

    @property
    def value(self) -> bool | float | str:
        """The underlying setting value."""
        return self._value

    def is_bool(self) -> bool:
        """Return ``True`` if the value is a bool."""
        return isinstance(self._value, bool)

    def is_float(self) -> bool:
        """Return ``True`` if the value is a float (not a bool)."""
        return isinstance(self._value, float) and not isinstance(self._value, bool)

    def is_str(self) -> bool:
        """Return ``True`` if the value is a string."""
        return isinstance(self._value, str)

    def as_bool(self) -> bool:
        """Return the value as a bool.

        Raises:
            TypeError: If the value is not a bool.
        """
        if isinstance(self._value, bool):
            return self._value
        raise TypeError(f"Setting is not a bool: {self._value!r}")

    def as_float(self) -> float:
        """Return the value as a float.

        Raises:
            TypeError: If the value is not a numeric type.
        """
        if isinstance(self._value, (int, float)) and not isinstance(self._value, bool):
            return float(self._value)
        raise TypeError(f"Setting is not a float: {self._value!r}")

    def as_str(self) -> str:
        """Return the value as a string.

        Raises:
            TypeError: If the value is not a str.
        """
        if isinstance(self._value, str):
            return self._value
        raise TypeError(f"Setting is not a str: {self._value!r}")

    def __eq__(self, other: object) -> bool:
        """Compare with another SettingSimple or a raw value."""
        if isinstance(other, SettingSimple):
            return self._value == other._value
        return self._value == other

    def __float__(self) -> float:
        """Return the float representation of this setting."""
        return self.as_float()

    def __repr__(self) -> str:
        """Return an unambiguous representation."""
        return f"SettingSimple({self._value!r})"

    def __str__(self) -> str:
        """Return the string representation of the underlying value."""
        return str(self._value)


@dataclass
class GameModSimple:
    """A lightweight mod representation storing only an acronym and its settings."""
    acronym: Acronym
    settings: dict[str, SettingSimple] = field(default_factory=dict)

    def __repr__(self) -> str:
        """Return an unambiguous representation."""
        return f"GameModSimple(acronym={self.acronym!r}, settings={self.settings!r})"

    def __str__(self) -> str:
        """Return the acronym string."""
        return str(self.acronym)
