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
    def __init__(self, kind: SplineType, degree: Optional[int] = None):
        self.kind = kind
        self.degree = degree

    @property
    def catmull(self): return PathType(SplineType.Catmull)

    @property
    def bezier(self): return PathType(SplineType.BSpline)

    @property
    def linear(self): return PathType(SplineType.Linear)

    @property
    def perfect_curve(self): return PathType(SplineType.PerfectCurve)

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

        if first_char == 'B':
            if rest.isdigit():
                degree = int(rest)
                return cls.new_b_spline(degree)
            return cls(SplineType.BSpline)
        elif first_char == 'L':
            return cls(SplineType.Linear)
        elif first_char == 'P':
            return cls(SplineType.PerfectCurve)
        else:
            return cls(SplineType.Catmull)