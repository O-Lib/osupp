from enum import Enum, auto
from typing import Optional


class SplineType(Enum):
    Catmull = auto()
    BSpline = auto()
    Linear = auto()
    PerfectCurve = auto()

    @classmethod
    def default(cls) -> "SplineType":
        return cls.Catmull


class PathType:
    def __init__(self, kind: SplineType, degree: int | None = None):
        self.kind = kind
        self.degree = degree

    @classmethod
    def catmull(cls) -> "PathType":
        return cls(SplineType.Catmull)

    @classmethod
    def bezier(cls) -> "PathType":
        return cls(SplineType.BSpline)

    @classmethod
    def linear(cls) -> "PathType":
        return cls(SplineType.Linear)

    @classmethod
    def perfect_curve(cls) -> "PathType":
        return cls(SplineType.PerfectCurve)

    @classmethod
    def new(cls, kind: SplineType) -> "PathType":
        return cls(kind)

    @classmethod
    def new_b_spline(cls, degree: int) -> "PathType":
        return cls(SplineType.BSpline, degree)

    @classmethod
    def new_from_str(cls, input_str: str) -> "PathType":
        if not input_str:
            return cls(SplineType.Catmull)
        first_char = input_str[0].upper()
        rest = input_str[1:]
        if first_char == "B":
            if rest.isdigit():
                degree = int(rest)
                return cls.new_b_spline(degree)
            return cls(SplineType.BSpline)
        elif first_char == "L":
            return cls(SplineType.Linear)
        elif first_char == "P":
            return cls(SplineType.PerfectCurve)
        else:
            return cls(SplineType.Catmull)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PathType):
            return self.kind == other.kind and self.degree == other.degree
        return False
