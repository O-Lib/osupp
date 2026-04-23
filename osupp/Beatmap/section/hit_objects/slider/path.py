from section.general import GameMode
from utils import Pos
from .curve import BorrowedCurve, Curve, CurveBuffers
from .path_type import PathType

from dataclasses import dataclass, field
from typing import List, Optional, Union


@dataclass
class PathControlPoint:
    pos: Pos = field(default_factory=Pos)
    path_type: Optional[PathType] = None

    @classmethod
    def new(cls, pos: Pos) -> "PathControlPoint":
        return cls(pos=pos)


@dataclass
class SliderPath:
    mode: "GameMode"
    control_points: List["PathControlPoint"] = field(default_factory=list)
    expected_dist: Optional[float] = None
    curve: Optional["Curve"] = None

    @classmethod
    def new(
        cls,
        mode: "GameMode",
        control_points: List["PathControlPoint"],
        expected_dist: Optional[float] = None,
    ) -> "SliderPath":
        return cls(
            mode=mode, control_points=control_points, expected_dist=expected_dist
        )

    @property
    def _control_points(self) -> List[PathControlPoint]:
        return self.control_points

    @_control_points.setter
    def _control_points(self, value: List[PathControlPoint]):
        self.clear_curve()
        self.control_points = value

    @property
    def _expected_dist(self) -> Optional[float]:
        return self.expected_dist

    @_expected_dist.setter
    def _expected_dist(self, value: Optional[float]):
        self.clear_curve()
        self.expected_dist = value

    def get_curve(self) -> Curve:
        if self.curve is not None:
            return self.curve

        self.curve = self.calculate_curve()
        return self.curve

    def get_curve_with_bufs(self, bufs: CurveBuffers) -> Curve:
        if self.curve is not None:
            return self.curve

        self.curve = self.calculate_curve_with_bufs(bufs)
        return self.curve

    def borrowed_curve(self, bufs: CurveBuffers) -> Union[Curve, BorrowedCurve]:
        if self.curve is not None:
            return self.curve

        return BorrowedCurve(self.mode, self.control_points, self.expected_dist, bufs)

    def clear_curve(self) -> Curve:
        return self.calculate_curve_with_bufs(CurveBuffers())

    def calculate_curve_with_bufs(self, bufs: CurveBuffers) -> Curve:
        return Curve(self.mode, self.control_points, self.expected_dist, bufs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SliderPath):
            return False
        return self.control_points == other.control_points
