from __future__ import annotations
from dataclasses import dataclass
import math


@dataclass(slots=True)
class Pos:
    x: float = 0.0
    y: float = 0.0

    @classmethod
    def new(cls, x: float, y: float) -> Pos:
        return cls(x, y)

    def length_squared(self) -> float:
        return self.dot(self)

    def length(self) -> float:
        return float(math.sqrt(self.x * self.x + self.y * self.y))

    def dot(self, other: Pos) -> float:
        return (self.x * other.x) + (self.y * other.y)

    def distance(self, other: Pos) -> float:
        return (self - other).length()

    def normalize(self) -> Pos:
        l = self.length()
        if l < 1e-7:
            return Pos(0.0, 0.0)

        scale = 1.0 / l
        return Pos(self.x * scale, self.y * scale)

    def __add__(self, rhs: Pos) -> Pos:
        return Pos.new(self.x + rhs.x, self.y + rhs.y)

    def __iadd__(self, rhs: Pos) -> Pos:
        self.x += rhs.x
        self.y += rhs.y
        return self

    def __sub__(self, rhs: Pos) -> Pos:
        return Pos.new(self.x - rhs.x, self.y - rhs.y)

    def __isub__(self, rhs: Pos) -> Pos:
        self.x -= rhs.x
        self.y -= rhs.y
        return self

    def __mul__(self, rhs: float) -> Pos:
        if isinstance(rhs, (int, float)):
            return Pos(x=self.x * rhs, y=self.y * rhs)
        return NotImplemented

    def __rmul__(self, lhs: float) -> Pos:
        return self.__mul__(lhs)

    def __imul__(self, rhs: float) -> Pos:
        if isinstance(rhs, (int, float)):
            self.x *= rhs
            self.y *= rhs
            return self
        return NotImplemented

    def __truediv__(self, rhs: float) -> Pos:
        if isinstance(rhs, (int, float)):
            return Pos(x=self.x / rhs, y=self.y / rhs)
        return NotImplemented

    def __itruediv__(self, rhs: float) -> Pos:
        if isinstance(rhs, (int, float)):
            self.x /= rhs
            self.y /= rhs
            return self
        return NotImplemented

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"Pos(x={self.x}, y={self.y})"
