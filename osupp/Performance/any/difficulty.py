import math
from typing import List, Optional, Protocol
from dataclasses import dataclass

from osupp.Mods.game_mods import GameMods
from osupp.Beatmap.section.enums import GameMode
from osupp.Beatmap.beatmap import Beatmap

from ..model.beatmap.attributes import BeatmapAttribute, BeatmapDifficulty
from .any import DifficultyAttributes

def count_top_weighted_strains(object_strains: List[float], difficulty_value: float) -> float:
    if not object_strains:
        return 0.0

    consistent_top_strain = difficulty_value / 10.0

    if abs(consistent_top_strain) < 1e-7:
        return float(len(object_strains))

    total = 0.0
    for s in object_strains:
        total += 1.1 / (1.0 + math.exp(-10.0 * (s / consistent_top_strain - 0.88)))
    return total

def calculate_difficulty_value(current_strain_peaks: List[float], decay_weight: float) -> float:
    difficulty = 0.0
    weight = 1.0

    peaks = [p for p in current_strain_peaks if p > 0.0]
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


@dataclass
class InspectDifficulty:
    mods: GameMods
    passed_objects: Optional[int]
    clock_rate: Optional[float]
    ar: BeatmapAttribute
    cs: BeatmapAttribute
    hp: BeatmapAttribute
    od: BeatmapAttribute
    hardrock_offsets: Optional[bool]
    lazer: Optional[bool]


class Difficulty:
    def __init__(self):
        self._mods = GameMods()
        self._passed_objects: Optional[int] = None
        self._clock_rate: Optional[float] = None
        self._map_difficulty = BeatmapDifficulty()
        self._hardrock_offsets: Optional[bool] = None
        self._lazer: Optional[bool] = None

    def inspect(self) -> "InspectDifficulty":
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

    def calculate(self, mapa_data: Beatmap) -> "DifficultyAttributes":
        mode = mapa_data.mode
        if mode == GameMode.Osu:
            raise NotImplementedError("Osu calculator to be implemented.")
        elif mode == GameMode.Taiko:
            raise NotImplementedError("Taiko calculator to be implemented.")
        elif mode == GameMode.Catch:
            raise NotImplementedError("Catch calculator to be implemented.")
        elif mode == GameMode.Mania:
            raise NotImplementedError("Mania calculator to be implemented.")

        return DifficultyAttributes()


class GradualDifficulty:
    def __init__(self, difficulty: Difficulty, map_data: Beatmap):
        pass

    def __iter__(self):
        return self

    def __next__(self) -> "DifficultyAttributes":
        raise StopIteration