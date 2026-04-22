from .decode import Colors, ColorsKey, ColorsState, ParseColorsError

from dataclasses import dataclass, field

__all__ = ["Colors", "ColorsKey", "ColorsState", "ParseColorsError"]

@dataclass
class Color:
    r: int = 0
    g: int = 0
    b: int = 0
    a: int = 255

    @classmethod
    def from_array(cls, color_array: list[int] | tuple[int, ...]) -> "Color":
        if len(color_array) < 3:
            raise ValueError("Array de cor deve ter pelo menos 3 elementos")

        r = color_array[0]
        g = color_array[1]
        b = color_array[2]
        a = color_array[3] if len(color_array) > 3 else 255

        return cls.new(r, g, b, a)

    @classmethod
    def parse(cls, s: str) -> "Color":
        parts = [p.strip() for p in s.split(',')]

        if len(parts) != 3:
            raise ParseColorsError.incorrect_color()

        try:
            r = int(parts[0])
            g = int(parts[1])
            b = int(parts[2])

            return cls.new(r, g, b, 255)
        except ValueError as e:
            raise ParseColorsError.incorrect_color() from e

    @classmethod
    def new(cls, r: int, g: int, b: int, a: int = 255) -> "Color":
        return cls(
            r=max(0, min(255, r)),
            g=max(0, min(255, g)),
            b=max(0, min(255, b)),
            a=max(0, min(255, a))
        )

    @property
    def red(self) -> int:
        return self.r

    @property
    def green(self) -> int:
        return self.g

    @property
    def blue(self) -> int:
        return self.b

    @property
    def alpha(self) -> int:
        return self.a

    def __getitem__(self, index: int) -> int:
        if index == 0: return self.r
        if index == 1: return self.g
        if index == 2: return self.b
        if index == 3: return self.a
        raise IndexError("Color index out of range")

    def __setitem__(self, index: int, value: int):
        val = max(0, min(255, value))

        if index == 0: self.r = val
        elif index == 1: self.g = val
        elif index == 2: self.b = val
        elif index == 3: self.a = val
        else:
            raise IndexError("Color index out of range")

    def __iter__(self):
        yield from (self.r, self.g, self.b, self.a)

@dataclass
class CustomColor:
    name: str = ""
    color: Color = field(default_factory=Color)

    @classmethod
    def new(cls, name: str, color: Color) -> "CustomColor":
        return cls(name=name, color=color)