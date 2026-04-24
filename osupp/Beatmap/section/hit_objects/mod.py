from typing import Union

from .circle import HitObjectCircle
from .hit_samples import HitSampleInfo
from .hold import HitObjectHold
from .slider import CurveBuffers, HitObjectSlider
from .spinner import HitObjectSpinner

BASE_SCORING_DIST: float = 100.0
HitObjectKind = Union[HitObjectCircle, HitObjectSlider, HitObjectSpinner, HitObjectHold]


class HitObject:
    def __init__(
        self, start_time: float, kind: HitObjectKind, samples: list[HitSampleInfo]
    ):
        self.start_time = start_time
        self.kind = kind
        self.samples = samples

    @property
    def new_combo(self) -> bool:
        if hasattr(self.kind, "new_combo"):
            return self.kind.new_combo
        return False

    def end_time(self, bufs: CurveBuffers | None = None) -> float:
        if bufs is None:
            bufs = CurveBuffers()
        return self.end_time_with_bufs(bufs)

    def end_time_with_bufs(self, bufs: CurveBuffers) -> float:
        if isinstance(self.kind, HitObjectCircle):
            return self.start_time
        elif isinstance(self.kind, HitObjectSlider):
            return self.start_time + self.kind.duration_with_bufs(bufs)
        elif isinstance(self.kind, (HitObjectSpinner, HitObjectHold)):
            return self.start_time + self.kind.duration
        return self.start_time


def get_new_combo(kind: HitObjectKind) -> bool:
    if isinstance(kind, (HitObjectCircle, HitObjectSlider, HitObjectSpinner)):
        return kind.new_combo
    return False


class HitObjectType:
    CIRCLE = 1
    SLIDER = 1 << 1
    NEW_COMBO = 1 << 2
    SPINNER = 1 << 3
    COMBO_OFFSET = (1 << 4) | (1 << 5) | (1 << 6)
    HOLD = 1 << 7

    def __init__(self, value: int = 0):
        self.value = value

    def has_flag(self, flag: int) -> bool:
        return (self.value & flag) != 0

    @classmethod
    def from_hit_object(cls, hit_object: "HitObject") -> "HitObjectType":
        kind_bits = 0
        obj = hit_object.kind
        if isinstance(obj, (HitObjectCircle, HitObjectSlider)):
            kind_bits |= obj.combo_offset << 4
            if obj.new_combo:
                kind_bits |= 4
        elif isinstance(obj, HitObjectSpinner):
            if obj.new_combo:
                kind_bits |= cls.NEW_COMBO
            kind_bits |= cls.SPINNER
        elif isinstance(obj, HitObjectHold):
            kind_bits |= cls.HOLD
        return cls(kind_bits)

    @classmethod
    def from_str(cls, s: str) -> "HitObjectType":
        try:
            return cls(int(s))
        except ValueError as e:
            raise ParseHitObjectTypeError(e)

    def __int__(self) -> int:
        return self.value

    def __and__(self, rhs: int) -> int:
        return self.value & rhs

    def __iand__(self, rhs: int) -> "HitObjectType":
        self.value &= rhs
        return self


class ParseHitObjectTypeError(Exception):
    def __init__(self, source: Exception):
        self.source = source
        super().__init__(f"invalid hit object type: {source}")
