import math
from dataclasses import dataclass
from typing import Protocol, TYPE_CHECKING

from osupp.Mods.game_mods import GameMods
from osupp.Beatmap.section.enums import GameMode
from osupp.Beatmap.beatmap import Beatmap

from ..model.beatmap.attributes import BeatmapAttribute, BeatmapDifficulty
from .any import DifficultyAttributes

if TYPE_CHECKING:
    from ..osu.difficulty.difficulty import OsuGradualDifficulty


def count_top_weighted_strains(object_strains: list[float], difficulty_value: float) -> float:
    if not object_strains:
        return 0.0

    consistent_top_strains = difficulty_value / 10.0

    if abs(consistent_top_strains) < 1e-7:
        return float(len(object_strains))

    return sum(
        1.1 / 1.0 + math.exp(-10.0 * (s / consistent_top_strains - 0.88))
        for s in object_strains
    )

def calculate_difficulty_value(current_strains_peaks: list[float], decay_weight: float) -> float:
    difficulty = 0
    weight = 1.0

    peaks = [p for p in current_strains_peaks if p > 0.0]
    peaks.sort(reverse=True)

    for strain in peaks:
        difficulty += strain * weight
        weight *= decay_weight

    return difficulty


def strain_decay(ms: float, strain_decay_base: float) -> float:
    return math.pow(strain_decay_base, ms / 1000.0)


class IDifficultyObject(Protocol):
    start_time: float

    def idx(self) -> int:
        ...


class StrainSkill:
    DECAY_WEIGHT: float = 0.9
    SECTION_LENGTH: float = 400.0


@dataclass(slots=True)
class InspectDifficulty:
    mods: GameMods
    passed_objects: int | None
    clock_rate: float | None
    ar: BeatmapAttribute
    cs: BeatmapAttribute
    hp: BeatmapAttribute
    od: BeatmapAttribute
    hardrock_offsets: bool | None
    lazer: bool | None


class Difficulty:
    __slots__ = ("_mods", "_passed_objects", "_clock_rate", "_map_difficulty", "_hardrock_offsets", "_lazer")

    def __init__(self):
        self._mods = GameMods()
        self._passed_objects: int | None = None
        self._clock_rate: float | None = None
        self._map_difficulty = BeatmapDifficulty()
        self._hardrock_offsets: bool | None = None
        self._lazer: bool | None = None

    def inspect(self) -> InspectDifficulty:
        return InspectDifficulty(
            mods=self._mods,
            passed_objects=self._passed_objects,
            clock_rate=self._clock_rate,
            ar=self._map_difficulty.ar,
            cs=self._map_difficulty.cs,
            hp=self._map_difficulty.hp,
            od=self._map_difficulty.od,
            hardrock_offsets=self._hardrock_offsets,
            lazer=self._lazer
        )

    def mods(self, mods: GameMods) -> "Difficulty":
        self._mods = mods
        return self

    def passed_objects(self, amount: int) -> "Difficulty":
        self._passed_objects = amount
        return self

    def clock_rate(self, rate: float) -> "Difficulty":
        self._clock_rate = max(0.01, min(100.0, rate))
        return self

    def ar(self, ar: float, fixed: bool) -> "Difficulty":
        ar_clamped = max(-20.0, min(20.0, ar))
        if fixed:
            self._map_difficulty.ar = BeatmapAttribute.fixed(ar_clamped)
        else:
            self._map_difficulty.ar = BeatmapAttribute.given(ar_clamped)
        return self

    def cs(self, cs: float, fixed: bool) -> "Difficulty":
        cs_clamped = max(-20.0, min(20.0, cs))
        if fixed:
            self._map_difficulty.cs = BeatmapAttribute.fixed(cs_clamped)
        else:
            self._map_difficulty.cs = BeatmapAttribute.given(cs_clamped)
        return self

    def hp(self, hp: float, fixed: bool) -> "Difficulty":
        hp_clamped = max(-20.0, min(20.0, hp))
        if fixed:
            self._map_difficulty.hp = BeatmapAttribute.fixed(hp_clamped)
        else:
            self._map_difficulty.hp = BeatmapAttribute.given(hp_clamped)
        return self

    def od(self, od: float, fixed: bool) -> "Difficulty":
        od_clamped = max(-20.0, min(20.0, od))
        if fixed:
            self._map_difficulty.od = BeatmapAttribute.fixed(od_clamped)
        else:
            self._map_difficulty.od = BeatmapAttribute.given(od_clamped)
        return self

    def hardrock_offsets(self, use_offsets: bool) -> "Difficulty":
        self._hardrock_offsets = use_offsets
        return self

    def lazer(self, is_lazer: bool) -> "Difficulty":
        self._lazer = is_lazer
        return self

    def get_clock_rate(self) -> float:
        if self._clock_rate is not None:
            return self._clock_rate
        return getattr(self._mods, "clock_rate", lambda: 1.0)() or 1.0

    def get_passed_objects(self) -> int:
        return self._passed_objects if self._passed_objects is not None else int(1e9)

    def get_lazer(self) -> bool:
        return self._lazer if self._lazer is not None else True

    def calculate(self, map_data: Beatmap) -> DifficultyAttributes:
        match map_data.mode:
            case GameMode.Osu:
                from ..osu.difficulty.difficulty import difficulty as calc_osu_difficulty
                return calc_osu_difficulty(self, map_data)
            case GameMode.Taiko:
                raise NotImplementedError("Taiko calculator to be implemented.")
            case GameMode.Catch:
                raise NotImplementedError("Catch calculator to be implemented.")
            case GameMode.Mania:
                raise NotImplementedError("Mania calculator to be implemented.")
            case _:
                return DifficultyAttributes()


class GradualDifficulty:
    __slots__ = ("_inner")

    def __init__(self, difficulty: Difficulty, map_data: Beatmap):
        match map_data.mode:
            case GameMode.Osu:
                from ..osu.difficulty.difficulty import OsuGradualDifficulty
                self._inner = OsuGradualDifficulty(difficulty, map_data)
            case GameMode.Taiko:
                raise NotImplementedError("Taiko Gradual to be implemented.")
            case GameMode.Catch:
                raise NotImplementedError("Catch Gradual to be implemented.")
            case GameMode.Mania:
                raise NotImplementedError("Mania Gradual to be implemented.")
            case _:
                self._inner = None

    def __iter__(self):
        return self

    def __next__(self) -> DifficultyAttributes:
        if self._inner is None:
            raise StopIteration

        res = next(self._inner, None)
        if res is None:
            raise StopIteration

        return res