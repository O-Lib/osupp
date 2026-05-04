import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from osupp.Beatmap.section.enums import GameMode
from osupp.Mods.game_mods import GameMods


class BeatmapAttributesType(Enum):
    NONE = 0
    VALUE = 1
    GIVEN = 2
    FIXED = 3

@dataclass
class BeatmapAttribute:
    type: BeatmapAttributesType = BeatmapAttributesType.NONE
    value: float = 5.0

    DEFAULT = 5.0

    @classmethod
    def none(cls) -> "BeatmapAttribute":
        return cls()

    @classmethod
    def from_value(cls, val: float) -> "BeatmapAttribute":
        return cls(type=BeatmapAttributesType.VALUE, value=val)

    @classmethod
    def given(cls, val: float) -> "BeatmapAttribute":
        return cls(type=BeatmapAttributesType.GIVEN, value=val)

    @classmethod
    def fixed(cls, val: float) -> "BeatmapAttribute":
        return cls(type=BeatmapAttributesType.FIXED, value=val)

    def overwrite(self, other: "BeatmapAttribute") -> "BeatmapAttribute":
        if other.type == BeatmapAttributesType.NONE:
            return self
        return other

    def try_mutate(self, func: callable) -> None:
        if self.type == BeatmapAttributesType.NONE:
            self.type = BeatmapAttributesType.VALUE
            self.value = self.DEFAULT

        if self.type in (BeatmapAttributesType.VALUE, BeatmapAttributesType.GIVEN):
            self.value = func(self.value)

    def try_set(self, new_val: float) -> None:
        if self.type == BeatmapAttributesType.NONE:
            self.type = BeatmapAttributesType.VALUE
            self.value = new_val
        elif self.type == BeatmapAttributesType.VALUE:
            self.value = new_val

    def get_raw(self) -> float:
        if self.type == BeatmapAttributesType.NONE:
            return self.DEFAULT
        return self.value


class ModStatus(Enum):
    NEITHER = 0
    EASY = 1
    HARDROCK = 2

    @classmethod
    def new(cls, mods: GameMods) -> "ModStatus":
        if mods.contains_acronym("HR"):
            return cls.HARDROCK
        elif mods.contains_acronym("EZ"):
            return cls.EASY
        return cls.NEITHER


@dataclass(slots=True)
class AdjustedBeatmapAttributes:
    ar: float
    cs: float
    hp: float
    od: float


class BeatmapAttributesExt:
    @staticmethod
    def difficulty_range(difficulty: float, min_val: float, mid_val: float, max_val: float) -> float:
        if difficulty > 5.0:
            return mid_val + (max_val -  mid_val) * BeatmapAttributesExt.difficulty_range_value(difficulty)
        elif difficulty < 5.0:
            return mid_val + (mid_val - min_val) * BeatmapAttributesExt.difficulty_range_value(difficulty)
        return mid_val

    @staticmethod
    def difficulty_range_value(difficulty: float) -> float:
        return (difficulty - 5.0) / 5.0

    @staticmethod
    def inverse_difficulty_range(difficulty_val: float, diff0: float, diff5: float, diff10: float) -> float:
        val1 = math.copysign(1.0, difficulty_val - diff5)
        val2 = math.copysign(1.0, diff10 - diff5)

        if abs(val1 - val2) < 1e-7:
            return (difficulty_val - diff5) / (diff10 - diff5) * 5.0 + 5.0
        else:
            return (difficulty_val - diff5) / (diff5 - diff0) * 5.0 + 5.0

@dataclass(slots=True)
class GameModeHitWindows:
    min: float
    mid: float
    max: float

    def difficulty_range(self, difficulty: float) -> float:
        return BeatmapAttributesExt.difficulty_range(difficulty, self.min, self.mid, self.max)

    def inverse_difficulty_range(self, difficulty_val: float) -> float:
        return BeatmapAttributesExt.inverse_difficulty_range(difficulty_val, self.min, self.mid, self.max)


AR_WINDOWS = GameModeHitWindows(1800.0, 1200.0, 450.0)

class OsuWindows:
    GREAT = GameModeHitWindows(80.0, 50.0, 20.0)
    OK = GameModeHitWindows(140.0, 100.0, 60.0)
    MEH = GameModeHitWindows(200.0, 150.0, 100.0)

class TaikoWindows:
    GREAT = GameModeHitWindows(50.0, 35.0, 20.0)
    OK = GameModeHitWindows(120.0, 80.0, 50.0)

class ManiaWindows:
    PERFECT = GameModeHitWindows(22.4, 19.4, 13.9)
    GREAT = GameModeHitWindows(64.0, 49.0, 34.0)
    GOOD = GameModeHitWindows(97.0, 82.0, 67.0)
    OK = GameModeHitWindows(127.0, 112.0, 97.0)
    MEH = GameModeHitWindows(151.0, 136.0, 121.0)


@dataclass(slots=True)
class HitWindows:
    ar: float | None = None
    od_perfect: float | None = None
    od_great: float | None = None
    od_good: float | None = None
    od_ok: float | None = None
    od_meh: float | None = None


class BeatmapDifficulty:
    def __init__(self):
        self.ar = BeatmapAttribute.none()
        self.cs = BeatmapAttribute.none()
        self.hp = BeatmapAttribute.none()
        self.od = BeatmapAttribute.none()


class BeatmapAttributes:
    def __init__(
            self,
            difficulty: BeatmapDifficulty,
            mode: GameMode,
            clock_rate: float,
            is_convert: bool,
            classic_and_not_v2: bool,
            mod_status: ModStatus
    ):
        self.difficulty = difficulty
        self.mode = mode
        self.clock_rate = clock_rate
        self.is_convert = is_convert
        self.class_and_not_v2 = classic_and_not_v2
        self.mod_status = mod_status

    def ar(self) -> float:
        attr = self.difficulty.ar
        if attr.type == BeatmapAttributesType.NONE:
            return BeatmapAttribute.DEFAULT
        if attr.type in (BeatmapAttributesType.GIVEN, BeatmapAttributesType.VALUE):
            return attr.value

        if self.mode in (GameMode.Osu, GameMode.Catch):
            preempt = AR_WINDOWS.difficulty_range(attr.value) * self.clock_rate
            return AR_WINDOWS.inverse_difficulty_range(preempt)
        return attr.value

    def od(self) -> float:
        attr = self.difficulty.od
        if attr.type == BeatmapAttributesType.NONE:
            return BeatmapAttribute.DEFAULT
        if attr.type in (BeatmapAttributesType.GIVEN, BeatmapAttributesType.VALUE):
            return attr.value

        if self.mode == GameMode.Osu:
            win = OsuWindows.GREAT.difficulty_range(attr.value) * self.clock_rate
            return OsuWindows.GREAT.inverse_difficulty_range(win)
        elif self.mode == GameMode.Taiko:
            win = TaikoWindows.GREAT.difficulty_range(attr.value) * self.clock_rate
            return TaikoWindows.GREAT.inverse_difficulty_range(win)
        elif self.mode == GameMode.Mania:
            factor = 1.0
            if self.mod_status == ModStatus.EASY:
                factor = 1.0 / 1.4
            elif self.mod_status == ModStatus.HARDROCK:
                factor = 1.4
            win = ManiaWindows.PERFECT.difficulty_range(attr.value) * factor
            return ManiaWindows.PERFECT.inverse_difficulty_range(win)

        return attr.value

    def cs(self) -> float:
        return self.difficulty.cs.get_raw()

    def hp(self) -> float:
        return self.difficulty.hp.get_raw()

    def get_clock_rate(self) -> float:
        return self.clock_rate

    def hit_windows(self) -> HitWindows:
        hw = HitWindows()

        def calculate_ar() -> float:
            attr = self.difficulty.ar
            val = BeatmapAttribute.DEFAULT if attr.type == BeatmapAttributesType.NONE else attr.value
            if attr.type == BeatmapAttributesType.FIXED:
                return AR_WINDOWS.difficulty_range(val)
            return AR_WINDOWS.difficulty_range(val) / self.clock_rate

        def set_difficulty(windows: GameModeHitWindows) -> float:
            attr = self.difficulty.od
            val = BeatmapAttribute.DEFAULT if attr.type == BeatmapAttributesType.NONE else attr.value

            if attr.type == BeatmapAttributesType.FIXED:
                f_val = windows.difficulty_range(val) * self.clock_rate
                return (math.floor(f_val) - 0.5) / self.clock_rate

            return (math.floor(windows.difficulty_range(val)) - 0.5) / self.clock_rate

        if self.mode == GameMode.Osu:
            hw.ar = calculate_ar()
            hw.od_great = set_difficulty(OsuWindows.GREAT)
            hw.od_ok = set_difficulty(OsuWindows.OK)
            hw.od_meh = set_difficulty(OsuWindows.MEH)

        elif self.mode == GameMode.Taiko:
            hw.od_great = set_difficulty(TaikoWindows.GREAT)
            hw.od_ok = set_difficulty(TaikoWindows.OK)

        elif self.mode == GameMode.Catch:
            hw.ar = calculate_ar()

        elif self.mode == GameMode.Mania:
            od = self.difficulty.od.get_raw()
            if self.class_and_not_v2:
                if self.is_convert:
                    hw.od_perfect = math.floor(16.0) + 0.5
                    hw.od_great = math.floor(34.0 if round(od) > 4.0 else 47.0) + 0.5
                    hw.od_good = math.floor(67.0 if round(od) > 4.0 else 77.0) + 0.5
                    hw.od_ok = math.floor(97.0) + 0.5
                    hw.od_meh = math.floor(121.0) + 0.5
                else:
                    inv_od = max(0.0, min(10.0, 10.0 - od))
                    hw.od_perfect = math.floor(16.0) + 0.5
                    hw.od_great = math.floor(34.0 + 3.0 * inv_od) + 0.5
                    hw.od_good = math.floor(67.0 + 3.0 * inv_od) + 0.5
                    hw.od_ok = math.floor(97.0 + 3.0 * inv_od) + 0.5
                    hw.od_meh = math.floor(121.0 + 3.0 * inv_od) + 0.5
            else:
                hw.od_perfect = math.floor(ManiaWindows.PERFECT.difficulty_range(od)) + 0.5
                hw.od_great = math.floor(ManiaWindows.GREAT.difficulty_range(od)) + 0.5
                hw.od_good = math.floor(ManiaWindows.GOOD.difficulty_range(od)) + 0.5
                hw.od_ok = math.floor(ManiaWindows.OK.difficulty_range(od)) + 0.5
                hw.od_meh = math.floor(ManiaWindows.MEH.difficulty_range(od)) + 0.5

        return hw

    def apply_clock_rate(self) -> AdjustedBeatmapAttributes:
        ar = self.ar()
        od = self.od()
        if self.mode in (GameMode.Taiko, GameMode.Mania):
            ar = self.difficulty.ar.get_raw()

        return AdjustedBeatmapAttributes(
            ar=ar,
            cs=self.cs(),
            hp=self.hp(),
            od=od
        )
