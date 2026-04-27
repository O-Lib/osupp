from __future__ import annotations

from dataclasses import dataclass

from utils import KeyValue, ParseNumberError, parse_int, trim_comment


class ParseColorsError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


def parse_u8(s: str) -> int:
    try:
        val = parse_int(s)
        if not (0 <= val <= 255):
            raise ValueError("color value out of bounds (mustbe 0-255)")
        return val
    except ParseNumberError as e:
        raise ValueError(str(e))


@dataclass(slots=True)
class Color:
    r: int
    g: int
    b: int
    a: int = 255

    @classmethod
    def from_str(cls, s: str) -> Color:
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


@dataclass(slots=True)
class CustomColor:
    name: str
    color: Color


@dataclass(slots=True)
class Colors:
    custom_color_colors: list[Color]
    custom_colors: list[CustomColor]

    def __init__(self):
        self.custom_color_colors = []
        self.custom_colors = []

    def parse_colors(self, line: str):
        clean_line = trim_comment(line)

        kv = KeyValue.parse(clean_line, str)
        if kv is None:
            return

        color = Color.from_str(kv.value)

        if kv.key.startswith("Combo"):
            self.custom_color_colors.append(color)
        else:
            for cc in self.custom_colors:
                if cc.name == kv.key:
                    cc.color = color
                    break
            else:
                self.custom_colors.append(CustomColor(name=kv.key, color=color))


ColorsState = Colors
