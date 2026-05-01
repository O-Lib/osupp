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

from dataclasses import dataclass

from utils import KeyValue, ParseNumberError, parse_int, trim_comment


class ParseColorsError(Exception):
    """Raised when a colour value in the [Colours] section cannot be parsed."""
    def __init__(self, message: str):
        """Initialise with an error message.

        Args:
            message: Description of the parse failure.
        """
        super().__init__(message)


def parse_u8(s: str) -> int:
    """Parse a string as a u8 colour component (0-255).

    Args:
        s: The raw string value to parse.

    Returns:
        An integer in the range [0, 255].

    Raises:
        ValueError: If the value is unparseable or outside [0, 255].
    """
    try:
        val = parse_int(s)
        if not (0 <= val <= 255):
            raise ValueError("color value out of bounds (mustbe 0-255)")
        return val
    except ParseNumberError as e:
        raise ValueError(str(e))


@dataclass(slots=True, eq=True)
class Color:
    """An RGBA colour value."""
    red: int
    green: int
    blue: int
    alpha: int = 255

    @classmethod
    def from_str(cls, s: str) -> Color:
        """Parse a Color from a comma-separated R,G,B or R,G,B,A string.

        Args:
            s: The raw colour value string from the beatmap file.

        Returns:
            A Color instance.

        Raises:
            ParseColorsError: If the format is invalid or any component is out of range.
        """
        parts = [part.strip() for part in s.split(",")]

        if len(parts) == 3:
            r, g, b = parts
            a = "255"
        elif len(parts) == 4:
            r, g, b, a = parts
        else:
            raise ParseColorsError(
                "color specified incorrect format (should be R,G,B or R,G,B,A"
            )

        try:
            return cls(parse_u8(r), parse_u8(g), parse_u8(b), parse_u8(a))
        except ValueError as e:
            raise ParseColorsError(f"invalid color number: {e}")


@dataclass(slots=True, eq=True)
class CustomColor:
    """A named custom colour entry from the [Colours] section."""
    name: str
    color: Color


@dataclass(slots=True, eq=True)
class Colors:
    """Holds all parsed colour data from the [Colours] section."""
    custom_combo_colors: list[Color]
    custom_colors: list[CustomColor]

    def __init__(self):
        """Initialise with empty combo and custom colour lists."""
        self.custom_combo_colors = []
        self.custom_colors = []

    def parse_colors(self, line: str):
        """Parse a single key-value line from the [Colours] section.

        Lines starting with ``Combo`` are appended to custom_combo_colors.
        All other keys are stored or updated in custom_colors.

        Args:
            line: A single raw line from the [Colours] section.
        """
        clean_line = trim_comment(line)

        kv = KeyValue.parse(clean_line, str)
        if kv is None:
            return

        color = Color.from_str(kv.value)

        if kv.key.startswith("Combo"):
            self.custom_combo_colors.append(color)
        else:
            for cc in self.custom_colors:
                if cc.name == kv.key:
                    cc.color = color
                    break
            else:
                self.custom_colors.append(CustomColor(name=kv.key, color=color))


ColorsState = Colors
