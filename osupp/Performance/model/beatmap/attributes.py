from dataclasses import dataclass, field
from enum import Enum
import math
from osupp.Beatmap.section.enums import GameMode
from ..model import GameMods

class AttributesType(Enum):
    NONE = 0
    VALUE = 1
    GIVEN = 2
    FIXED = 3


@dataclass(slots=True)
class BeatmapAttribute:
    attr_type: AttributesType = AttributesType.NONE
    value: float = 5.0

    @classmethod
    def given(cls, value: float) -> "BeatmapAttribute":
        return cls(AttributesType.GIVEN, value)

    @classmethod
    def fixed(cls, value: float) -> "BeatmapAttribute":
        return cls(AttributesType.FIXED, value)

    def overwrite(self, other: "BeatmapAttribute") -> "BeatmapAttribute":
        if other.attr_type == AttributesType.NONE:
            return self
        return other


@dataclass(slots=True)
class BeatmapDifficulty:
    ar: BeatmapAttribute = field(default_factory=BeatmapAttribute)
    cs: BeatmapAttribute = field(default_factory=BeatmapAttribute)
    hp: BeatmapAttribute = field(default_factory=BeatmapAttribute)
    od: BeatmapAttribute = field(default_factory=BeatmapAttribute)

    def apply_mods(self, mods: GameMods, mode: GameMode) -> None:
        if mods.ez:
            ratio = 0.5
            for attr in (self.ar, self.cs, self.hp, self.od):
                if attr.attr_type in (AttributesType.VALUE, AttributesType.GIVEN, AttributesType.NONE):
                    attr.value *= ratio
                    attr.attr_type = AttributesType.VALUE
        elif mods.hr:
            ratio = 1.4
            self.cs.value = min(self.cs.value * 1.3, 10.0) if mode == GameMode.Osu else min(self.cs.value * ratio, 10.0)
            for attr in (self.ar, self.hp, self.od):
                if attr.attr_type in (AttributesType.VALUE, AttributesType.GIVEN, AttributesType.NONE):
                    attr.value = min(attr.value * ratio, 10.0)
                    attr.attr_type = AttributesType.VALUE


@dataclass(slots=True)
class HitWindows:
    ar: float | None = None
    od_perfect: float | None = None
    od_great: float | None = None
    od_good: float | None = None
    od_ok: float | None = None
    od_meh: float | None = None


class BeatmapAttributesExt:
    @staticmethod
    def difficulty_range(difficulty: float, min_val: float, mid_val: float, max_val: float) -> float:
        if difficulty > 5.0:
            return mid_val + (max_val - mid_val) * (difficulty - 5.0) / 5.0
        if difficulty < 5.0:
            return mid_val - (mid_val - min_val) * (5.0 - difficulty) / 5.0
        return mid_val


@dataclass(slots=True)
class BeatmapAttributes:
    difficulty: BeatmapDifficulty
    mode: GameMode
    clock_rate: float
    is_convert: bool

    def hit_windows(self) -> HitWindows:
        od = self.difficulty.od.value
        ar = self.difficulty.ar.value

        match self.mode:
            case GameMode.Osu:
                return HitWindows(
                    ar=BeatmapAttributesExt.difficulty_range(ar, 1800.0, 1200.0, 450.0),
                    od_great=BeatmapAttributesExt.difficulty_range(od, 80.0, 50.0, 20.0),
                    od_ok=BeatmapAttributesExt.difficulty_range(od, 140.0, 100.0, 60.0),
                    od_meh=BeatmapAttributesExt.difficulty_range(od, 200.0, 150.0, 100.0)
                )
            case GameMode.Mania:
                return HitWindows(
                    od_perfect=BeatmapAttributesExt.difficulty_range(od, 22.4, 19.4, 13.9),
                    od_great=BeatmapAttributesExt.difficulty_range(od, 64.1, 49.1, 34.1),
                    od_good=BeatmapAttributesExt.difficulty_range(od, 97.1, 82.1, 67.1),
                    od_ok=BeatmapAttributesExt.difficulty_range(od, 127.1, 112.1, 97.1),
                    od_meh=BeatmapAttributesExt.difficulty_range(od, 151.1, 136.1, 121.1)
                )
            case _:
                return HitWindows()


@dataclass(slots=True)
class AdjustedBeatmapAttributes:
    ar: float
    cs: float
    hp: float
    od: float