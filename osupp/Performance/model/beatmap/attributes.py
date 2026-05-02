import math
from enum import Enum
from typing import Any, Optional
from collections.abc import Callable

from osupp.Beatmap.section.enums import GameMode
from osupp.Mods.game_mods import GameMods

from ...utils.util import almost_eq, clamp


class AttributeType(Enum):
    NONE = 0
    VALUE = 1
    GIVEN = 2
    FIXED = 3


class BeatmapAttribute:
    DEFAULT = 5.0

    __slots__ = ("type", "value")

    def __init__(self, type_: AttributeType = AttributeType.NONE, value: float = 0.0):
        self.type = type_
        self.value = value

    @classmethod
    def default_none(cls) -> "BeatmapAttribute":
        return cls(AttributeType.NONE, 0.0)

    @classmethod
    def value_type(cls, val: float) -> "BeatmapAttribute":
        return cls(AttributeType.VALUE, val)

    @classmethod
    def given_type(cls, val: float) -> "BeatmapAttribute":
        return cls(AttributeType.GIVEN, val)

    @classmethod
    def fixed_type(cls, val: float) -> "BeatmapAttribute":
        return cls(AttributeType.FIXED, val)

    def overwrite(self, other: "BeatmapAttribute") -> "BeatmapAttribute":
        if other.type == AttributeType.NONE:
            return self
        return other

    def try_mutate(self, f: Callable[[float], float]) -> None:
        if self.type == AttributeType.NONE:
            self.type = AttributeType.VALUE
            self.value = self.DEFAULT

        if self.type in (AttributeType.VALUE, AttributeType.GIVEN):
            self.value = f(self.value)

    def try_set(self, value: float) -> None:
        if self.type == AttributeType.NONE:
            self.type = AttributeType.VALUE
            self.value = value
        elif self.type == AttributeType.VALUE:
            self.value = value

    def map_or_else(self, default_func: Callable[[float], float], f: Callable[[float], float]):
        if self.type == AttributeType.NONE:
            return f(self.DEFAULT)
        elif self.type in (AttributeType.VALUE, AttributeType.GIVEN):
            return f(self.value)
        elif self.type == AttributeType.FIXED:
            return default_func(self.value)
        return 0.0

    def get_raw(self) -> float:
        if self.type == AttributeType.NONE:
            return self.DEFAULT
        return self.value

    def clone(self) -> BeatmapAttribute:
        return BeatmapAttribute(self.type, self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BeatmapAttribute):
            return NotImplemented
        return self.type == other.type and almost_eq(self.value, other.value)


class BeatmapDifficulty:
    __slots__ = ("ar", "cs", "hp", "od")

    def __init__(
            self,
            ar: BeatmapAttribute | None = None,
            cs: BeatmapAttribute | None = None,
            hp: BeatmapAttribute | None = None,
            od: BeatmapAttribute | None = None,
    ):
        self.ar = ar if ar is not None else BeatmapAttribute.default_none()
        self.cs = cs if cs is not None else BeatmapAttribute.default_none()
        self.hp = hp if hp is not None else BeatmapAttribute.default_none()
        self.od = od if od is not None else BeatmapAttribute.default_none()

    @classmethod
    def default(cls) -> "BeatmapDifficulty":
        return cls()

    def apply_mods(self, mods: GameMods, mode: GameMode) -> None:
        for m in mods:
            if str(m.acronym()) == "DA":
                da = m.inner

                if mode == GameMode.Osu:
                    if getattr(da, "approach_rate", None) is not None:
                        self.ar.try_set(float(da.approach_rate))
                    if getattr(da, "circle_size", None) is not None:
                        self.cs.try_set(float(da.circle_size))
                    if getattr(da, "drain_rate", None) is not None:
                        self.hp.try_set(float(da.drain_rate))
                    if getattr(da, "overall_difficulty", None) is not None:
                        self.od.try_set(float(da.overall_difficulty))
                elif mode == GameMode.Taiko:
                    if getattr(da, "drain_rate", None) is not None:
                        self.hp.try_set(float(da.drain_rate))
                    if getattr(da, "overall_difficulty", None) is not None:
                        self.od.try_set(float(da.overall_difficulty))
                elif mode == GameMode.Catch:
                    if getattr(da, "approach_rate", None) is not None:
                        self.ar.try_set(float(da.approach_rate))
                    if getattr(da, "circle_size", None) is not None:
                        self.cs.try_set(float(da.circle_size))
                    if getattr(da, "drain_rate", None) is not None:
                        self.hp.try_set(float(da.drain_rate))
                    if getattr(da, "overall_difficulty", None) is not None:
                        self.od.try_set(float(da.overall_difficulty))
                elif mode == GameMode.Mania:
                    if getattr(da, "drain_rate", None) is not None:
                        self.hp.try_set(float(da.drain_rate))
                    if getattr(da, "overall_difficulty", None) is not None:
                        self.od.try_set(float(da.overall_difficulty))

        if mods.contains_acronym("EZ"):
            ADJUST_RATIO = 0.5
            self.ar.try_mutate(lambda x: x * ADJUST_RATIO)
            self.cs.try_mutate(lambda x: x * ADJUST_RATIO)
            self.hp.try_mutate(lambda x: x * ADJUST_RATIO)

            if mode in (GameMode.Osu, GameMode.Taiko, GameMode.Catch):
                self.od.try_mutate(lambda x: x * ADJUST_RATIO)

        elif mods.contains_acronym("HR"):
            ADJUST_RATIO = 1.4
            self.hp.try_mutate(lambda x: min(x * ADJUST_RATIO, 10.0))

            if mode == GameMode.Osu:
                self.od.try_mutate(lambda x: min(x * ADJUST_RATIO, 10.0))
                self.cs.try_mutate(lambda x: min(x * 1.3, 10.0))
                self.ar.try_mutate(lambda x: min(x * ADJUST_RATIO, 10.0))
            elif mode == GameMode.Taiko:
                self.od.try_mutate(lambda x: min(x * ADJUST_RATIO, 10.0))
            elif mode == GameMode.Catch:
                self.od.try_mutate(lambda x: min(x * ADJUST_RATIO, 10.0))
                self.cs.try_mutate(lambda x: min(x * 1.3, 10.0))
                self.ar.try_mutate(lambda x: min(x * ADJUST_RATIO, 10.0))

    def clone(self) -> "BeatmapDifficulty":
        return BeatmapDifficulty(self.ar.clone(), self.cs.clone(), self.hp.clone(), self.od.clone())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BeatmapDifficulty):
            return NotImplemented
        return (self.ar == other.ar and self.cs == other.cs and
                self.hp == other.hp and self.od == other.od)


class BeatmapAttributesExt:
    @staticmethod
    def difficulty_range(difficulty: float, min_val: float, mid_val: float, max_val: float) -> float:
        if difficulty > 5.0:
            return mid_val + (max_val - mid_val) * BeatmapAttributesExt.difficulty_range_value(difficulty)
        elif difficulty < 5.0:
            return mid_val + (mid_val - min_val) * BeatmapAttributesExt.difficulty_range_value(difficulty)
        else:
            return mid_val

    @staticmethod
    def difficulty_range_value(difficulty: float) -> float:
        return (difficulty - 5.0) / 5.0

    @staticmethod
    def inverse_difficulty_range(difficulty_value: float, diff0: float, diff5: float, diff10: float) -> float:
        def signum(val: float) -> float:
            if val > 0: return 1.0
            if val < 0: return -1.0
            return 0.0

        if almost_eq(signum(difficulty_value - diff5), signum(diff10 - diff5)):
            return (difficulty_value - diff5) / (diff10 - diff5) * 5.0 + 5.0
        else:
            return (difficulty_value - diff5) / (diff5 - diff0) * 5.0 + 5.0

    @staticmethod
    def osu_great_hit_window_to_od(hit_window: float) -> float:
        return (79.5 - hit_window) / 6.0

class GameModeHitWindows:
    __slots__ = ("min", "mid", "max")

    def __init__(self, min_val: float, mid_val: float, max_val: float):
        self.min = min_val
        self.mid = mid_val
        self.max = max_val

    def difficulty_range(self, difficulty: float) -> float:
        return BeatmapAttributesExt.difficulty_range(difficulty, self.min, self.mid, self.max)

    def inverse_difficulty_range(self, difficulty_value: float) -> float:
        return BeatmapAttributesExt.inverse_difficulty_range(difficulty_value, self.min, self.mid, self.max)


class OsuHitWindows:
    GREAT = GameModeHitWindows(80.0, 50.0, 20.0)
    OK = GameModeHitWindows(140.0, 100.0, 60.0)
    MEH = GameModeHitWindows(120.0, 80.0, 50.0)


class TaikoHitWindows:
    GREAT = GameModeHitWindows(50.0, 35.0, 20.0)
    OK = GameModeHitWindows(120.0, 80.0, 50.0)


class ManiaHitWindows:
    PERFECT = GameModeHitWindows(22.4, 19.4, 13.9)
    GREAT = GameModeHitWindows(64.0, 49.0, 34.0)
    GOOD = GameModeHitWindows(97.0, 82.0, 67.0)
    OK = GameModeHitWindows(127.0, 112.0, 97.0)
    MEH = GameModeHitWindows(151.0, 136.0, 121.0)


AR_HIT_WINDOWS = GameModeHitWindows(1800.0, 1200.0, 450.0)


class HitWindows:
    __slots__ = ("ar, od_perfect", "od_great", "od_good", "od_ok", "od_meh")

    def __init__(
            self,
            ar: float | None = None,
            od_perfect: float | None = None,
            od_great: float | None = None,
            od_good: float | None = None,
            od_ok: float | None = None,
            od_meh: float | None = None
    ):
        self.ar = ar
        self.od_perfect = od_perfect
        self.od_great = od_great
        self.od_good = od_good
        self.od_ok = od_ok
        self.od_meh = od_meh

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HitWindows):
            return NotImplemented
        return (
            self.ar == other.ar and
            self.od_perfect == other.od_perfect and
            self.od_great == other.od_great and
            self.od_good == other.od_good and
            self.od_ok == other.od_ok and
            self.od_meh == other.od_meh
        )


class AdjustedBeatmapAttributes:
    __slots__ = ("ar", "cs", "hp", "od")

    def __init__(self, ar: float, cs: float, hp: float, od: float):
        self.ar = ar
        self.cs = cs
        self.hp = hp
        self.od = od

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AdjustedBeatmapAttributes):
            return NotImplemented
        return (
            almost_eq(self.ar, other.ar) and
            almost_eq(self.cs, other.cs) and
            almost_eq(self.hp, other.hp) and
            almost_eq(self.od, other.od)
        )


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


def _round_ties_even(num: float) -> float:
    return round(num)


class BeatmapAttributes:
    __slots__ = ("difficulty", "mode", "_clock_rate", "is_convert", "classic_and_not_v2", "mod_status")

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
        self._clock_rate = clock_rate
        self.is_convert = is_convert
        self.classic_and_not_v2 = classic_and_not_v2
        self.mod_status = mod_status

    @staticmethod
    def builder() -> "BeatmapAttributesBuilder":
        return BeatmapAttributesBuilder()

    def ar(self) -> float:
        if self.difficulty.ar.type == AttributeType.NONE:
            return BeatmapAttribute.DEFAULT
        if self.difficulty.ar.type in (AttributeType.GIVEN, AttributeType.VALUE):
            return self.difficulty.ar.value

        fixed = self.difficulty.ar.value
        if self.mode in (GameMode.Osu, GameMode.Catch):
            return AR_HIT_WINDOWS.inverse_difficulty_range(
                AR_HIT_WINDOWS.difficulty_range(fixed) * self._clock_rate
            )
        return fixed

    def od(self) -> float:
        if self.difficulty.od.type == AttributeType.NONE:
            return BeatmapAttribute.DEFAULT
        if self.difficulty.od.type in (AttributeType.GIVEN, AttributeType.VALUE):
            return self.difficulty.od.value

        fixed = self.difficulty.od.value
        if self.mode == GameMode.Osu:
            return OsuHitWindows.GREAT.inverse_difficulty_range(
                OsuHitWindows.GREAT.difficulty_range(fixed) * self._clock_rate
            )
        elif self.mode == GameMode.Taiko:
            return TaikoHitWindows.GREAT.inverse_difficulty_range(
                TaikoHitWindows.GREAT.difficulty_range(fixed) * self._clock_rate
            )
        elif self.mode == GameMode.Mania:
            factor = 1.0
            if self.mod_status == ModStatus.EASY:
                factor = 1.0 / 1.4
            elif self.mod_status == ModStatus.HARDROCK:
                factor = 1.4

            return ManiaHitWindows.PERFECT.inverse_difficulty_range(
                ManiaHitWindows.PERFECT.difficulty_range(fixed) * factor
            )
        elif self.mode == GameMode.Catch:
            return fixed
        return 0.0

    def cs(self) -> float:
        return self.difficulty.cs.get_raw()

    def hp(self) -> float:
        return self.difficulty.hp.get_raw()

    def clock_rate(self) -> float:
        return self._clock_rate

    def hit_windows(self) -> HitWindows:
        clock_rate = self._clock_rate

        def _ar() -> float:
            if self.difficulty.ar.type == AttributeType.NONE:
                val = BeatmapAttribute.DEFAULT
            elif self.difficulty.ar.type in (AttributeType.VALUE, AttributeType.GIVEN):
                val = self.difficulty.ar.value
            else:
                return AR_HIT_WINDOWS.difficulty_range(self.difficulty.ar.value)
            return AR_HIT_WINDOWS.difficulty_range(val) / clock_rate

        def _set_difficulty(hit_wins: GameModeHitWindows) -> float:
            if self.difficulty.od.type == AttributeType.NONE:
                val = BeatmapAttribute.DEFAULT
            elif self.difficulty.od.type in (AttributeType.VALUE, AttributeType.GIVEN):
                val = self.difficulty.od.value
            else:
                f_value = hit_wins.difficulty_range(self.difficulty.od.value) * clock_rate
                return (math.floor(f_value) - 0.5) / clock_rate
            return (math.floor(hit_wins.difficulty_range(val)) - 0.5) / clock_rate

        if self.mode == GameMode.Osu:
            return HitWindows(
                ar=_ar(),
                od_great=_set_difficulty(OsuHitWindows.GREAT),
                od_ok=_set_difficulty(OsuHitWindows.OK),
                od_meh=_set_difficulty(OsuHitWindows.MEH)
            )
        elif self.mode == GameMode.Taiko:
            return HitWindows(
                od_great=_set_difficulty(TaikoHitWindows.GREAT),
                od_ok=_set_difficulty(TaikoHitWindows.OK)
            )
        elif self.mode == GameMode.Catch:
            return HitWindows(ar=_ar())
        elif self.mode == GameMode.Mania:
            total_multiplier = 1.0
            od = self.difficulty.od.get_raw()

            if self.classic_and_not_v2:
                if self.is_convert:
                    perfect = math.floor(16.0 * total_multiplier) + 0.5
                    great = math.floor((34.0 if _round_ties_even(od) > 4.0 else 47.0) * total_multiplier) + 0.5
                    good = math.floor((67.0 if _round_ties_even(od) > 4.0 else 77.0) * total_multiplier) + 0.5
                    ok = math.floor(97.0 * total_multiplier) + 0.5
                    meh = math.floor(121.0 * total_multiplier) + 0.5
                else:
                    inverted_od = clamp(10.0 - od, 0.0, 10.0)

                    def _hw(add: float) -> float:
                        return math.floor((add + 3.0 * inverted_od) * total_multiplier) + 0.5

                    perfect = math.floor(16.0 * total_multiplier) + 0.5
                    great = _hw(34.0)
                    good = _hw(67.0)
                    ok = _hw(97.0)
                    meh = _hw(121.0)
            else:
                def _hw_normal(hit_wins: GameModeHitWindows) -> float:
                    return math.floor(hit_wins.difficulty_range(od) * total_multiplier) + 0.5

                perfect = _hw_normal(ManiaHitWindows.PERFECT)
                great = _hw_normal(ManiaHitWindows.GREAT)
                good = _hw_normal(ManiaHitWindows.GOOD)
                ok = _hw_normal(ManiaHitWindows.OK)
                meh = _hw_normal(ManiaHitWindows.MEH)

            return HitWindows(
                od_perfect=perfect,
                od_great=great,
                od_good=good,
                od_ok=ok,
                od_meh=meh
            )
        return HitWindows()

    def apply_clock_rate(self) -> AdjustedBeatmapAttributes:
        clock_rate = self._clock_rate

        if self.mode == GameMode.Osu:
            def _ar_map(ar: float) -> float:
                preempt = AR_HIT_WINDOWS.difficulty_range(ar) / clock_rate
                return AR_HIT_WINDOWS.inverse_difficulty_range(preempt)

            ar_val = self.difficulty.ar.map_or_else(lambda x: x, _ar_map)

            def _od_map(od: float) -> float:
                gw = OsuHitWindows.GREAT.difficulty_range(od) / clock_rate
                return OsuHitWindows.GREAT.inverse_difficulty_range(gw)

            od_val = self.difficulty.od.map_or_else(lambda x: x, _od_map)
            return AdjustedBeatmapAttributes(ar_val, self.difficulty.cs.get_raw(), self.difficulty.hp.get_raw(), od_val)

        elif self.mode == GameMode.Taiko:
            def _od_map_taiko(od: float) -> float:
                gw = TaikoHitWindows.GREAT.difficulty_range(od) / clock_rate
                return TaikoHitWindows.GREAT.inverse_difficulty_range(gw)

            od_val = self.difficulty.od.map_or_else(lambda x: x, _od_map_taiko)
            return AdjustedBeatmapAttributes(self.difficulty.ar.get_raw(), self.difficulty.cs.get_raw(), self.difficulty.hp.get_raw(), od_val)


        elif self.mode == GameMode.Catch:
            def _ar_map_catch(ar: float) -> float:
                preempt = AR_HIT_WINDOWS.difficulty_range(ar) / clock_rate
                return AR_HIT_WINDOWS.inverse_difficulty_range(preempt)

            ar_val = self.difficulty.ar.map_or_else(lambda x: x, _ar_map_catch)
            return AdjustedBeatmapAttributes(ar_val, self.difficulty.cs.get_raw(), self.difficulty.hp.get_raw(), self.difficulty.od.get_raw())

        elif self.mode == GameMode.Mania:
            def _od_map_mania(od: float) -> float:
                pw = ManiaHitWindows.PERFECT.difficulty_range(od)
                if self.mod_status == ModStatus.EASY:
                    pw /= (1.0 / 1.4)
                elif self.mod_status == ModStatus.HARDROCK:
                    pw /= 1.4
                return ManiaHitWindows.PERFECT.inverse_difficulty_range(pw)

            od_val = self.difficulty.od.map_or_else(lambda x: x, _od_map_mania)
            return AdjustedBeatmapAttributes(self.difficulty.ar.get_raw(), self.difficulty.cs.get_raw(), self.difficulty.hp.get_raw(), od_val)


class BeatmapAttributesBuilder:
    __slots__ = ("_mode", "_is_convert", "_difficulty", "_mods", "_clock_rate")

    def __init__(self):
        self._mode = GameMode.Osu
        self._is_convert = False
        self._difficulty = BeatmapDifficulty.default()
        self._mods = GameMods()
        self._clock_rate: float | None = None

    def map(self, beatmap: "Beatmap") -> "BeatmapAttributesBuilder":
        self._mode = getattr(beatmap, "mode", GameMode.Osu)
        self._is_convert = getattr(beatmap, "is_convert", False)

        ar_val = getattr(beatmap, "ar", 5.0)
        od_val = getattr(beatmap, "od", 5.0)
        cs_val = getattr(beatmap, "cs", 5.0)
        hp_val = getattr(beatmap, "hp", 5.0)

        self._difficulty = BeatmapDifficulty(
            ar=BeatmapAttribute.value_type(clamp(ar_val, 0.0, 10.0)),
            od=BeatmapAttribute.value_type(clamp(od_val, 0.0, 10.0)),
            cs=BeatmapAttribute.value_type(cs_val),
            hp=BeatmapAttribute.value_type(hp_val)
        )
        return self

    def ar(self, value: float, fixed: bool) -> "BeatmapAttributesBuilder":
        self._difficulty.ar = BeatmapAttribute.fixed_type(value) if fixed else BeatmapAttribute.given_type(value)
        return self

    def od(self, value: float, fixed: bool) -> "BeatmapAttributesBuilder":
        self._difficulty.od = BeatmapAttribute.fixed_type(value) if fixed else BeatmapAttribute.given_type(value)
        return self

    def cs(self, value: float, fixed: bool) -> "BeatmapAttributesBuilder":
        self._difficulty.cs = BeatmapAttribute.fixed_type(value) if fixed else BeatmapAttribute.given_type(value)
        return self

    def hp(self, value: float, fixed: bool) -> "BeatmapAttributesBuilder":
        self._difficulty.hp = BeatmapAttribute.fixed_type(value) if fixed else BeatmapAttribute.given_type(value)
        return self

    def mods(self, mods: GameMods) -> "BeatmapAttributesBuilder":
        self._mods = mods
        return self

    def clock_rate(self, clock_rate: float) -> "BeatmapAttributesBuilder":
        self._clock_rate = clock_rate
        return self

    def mode(self, mode: GameMode, is_convert: bool) -> "BeatmapAttributesBuilder":
        self._mode = mode
        self._is_convert = is_convert
        return self

    def difficulty(self, difficulty: Any) -> "BeatmapAttributesBuilder":
        if hasattr(difficulty, "get_map_difficulty"):
            map_diff = difficulty.get_map_difficulty()
            self._difficulty.ar = self._difficulty.ar.overwrite(map_diff.ar)
            self._difficulty.cs = self._difficulty.cs.overwrite(map_diff.cs)
            self._difficulty.hp = self._difficulty.hp.overwrite(map_diff.hp)
            self._difficulty.od = self._difficulty.od.overwrite(map_diff.od)

        if hasattr(difficulty, "get_mods"):
            self._mods = difficulty.get_mods()

        if hasattr(difficulty, "get_clock_rate"):
            self._clock_rate = difficulty.get_clock_rate()

        return self

    def build(self) -> "BeatmapAttributes":
        mods = self._mods

        difficulty = self._difficulty.clone()
        difficulty.apply_mods(mods, self._mode)

        mod_clock_rate = 1.0

        try:
            cr = mods.clock_rate()
            if cr is not None:
                mod_clock_rate = cr
        except AttributeError:
            for m in mods:
                acr = str(m.acronym()).upper()
                if acr in ("DT", "NC"):
                    custom_speed = getattr(m.inner, "speed_change", None)
                    mod_clock_rate = custom_speed if custom_speed is not None else 1.5
                elif acr in ("HT", "DC"):
                    custom_speed = getattr(m.inner, "speed_change", None)
                    mod_clock_rate = custom_speed if custom_speed is not None else 0.75

        cr = self._clock_rate if self._clock_rate is not None else mod_clock_rate

        classic_and_not_v2 = False
        if hasattr(mods, "contains_acronym"):
            classic_and_not_v2 = mods.contains_acronym("CL") and not mods.contains_acronym("SV2")

        return BeatmapAttributes(
            difficulty=difficulty,
            mode=self._mode,
            clock_rate=cr,
            is_convert=self._is_convert,
            classic_and_not_v2=classic_and_not_v2,
            mod_status=ModStatus.new(mods)
        )
