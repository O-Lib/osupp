from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from osupp.Beatmap.section.enums import GameMode
from osupp.Beatmap.utils import Pos

from ..any.any import DifficultyAttributes, HitResult, PerformanceAttributes, ScoreState
from ..model.model import ConvertError, GameMods, Reflection
from ..model.model import HitObject as GenericHitObjects

if TYPE_CHECKING:
    from ..model.beatmap.beatmap import Beatmap


PLAYFIELD_BASE_SIZE = Pos(512.0, 384.0)


class OsuScoreOrigin(Enum):
    STABLE = 0
    WITH_SLIDER_ACC = 1
    WITHOUT_SLIDER_ACC = 2


@dataclass(slots=True)
class OsuHitResults:
    n300: int = 0
    n100: int = 0
    n50: int = 0
    misses: int = 0
    large_tick_hits: int = 0
    small_tick_hits: int = 0
    slider_end_hits: int = 0


@dataclass(slots=True)
class OsuScoreState:
    max_combo: int = 0
    hitresults: OsuHitResults = field(default_factory=OsuHitResults)
    legacy_total_score: int | None = None


@dataclass(slots=True)
class OsuDifficultyAttributes:
    aim: float = 0.0
    aim_difficult_slider_count: float = 0.0
    speed: float = 0.0
    flashlight: float = 0.0
    slider_factor: float = 0.0
    aim_top_weighted_slider_factor: float = 0.0
    speed_top_weighted_slider_factor: float = 0.0
    speed_note_count: float = 0.0
    aim_difficult_strain_count: float = 0.0
    speed_difficult_strain_count: float = 0.0
    nested_score_per_object: float = 0.0
    legacy_score_base_multiplier: float = 0.0
    maximum_legacy_combo_score: float = 0.0
    max_combo: int = 0
    ar: float = 0.0
    cs: float = 0.0
    hp: float = 0.0
    od: float = 0.0
    clock_rate: float = 1.0
    stars: float = 0.0
    n_circles: int = 0
    n_sliders: int = 0
    n_spinners: int = 0


@dataclass(slots=True)
class OsuPerformanceAttributes:
    difficulty: OsuDifficultyAttributes
    pp: float = 0.0
    pp_acc: float = 0.0
    pp_aim: float = 0.0
    pp_flashlight: float = 0.0
    pp_speed: float = 0.0
    effective_miss_count: float = 0.0


class NestedSliderObjectKind(Enum):
    TICK = 0
    REPEAT = 1
    TAIL = 2


@dataclass(slots=True)
class NestedSliderObject:
    pos: Pos
    start_time: float
    kind: NestedSliderObjectKind


@dataclass(slots=True)
class OsuObject:
    pos: Pos
    start_time: float
    stack_height: int = 0
    stack_offset: Pos = field(default_factory=lambda: Pos(0, 0))
    kind: Any = None

    @property
    def stacked_pos(self) -> Pos:
        return self.pos + self.stack_offset


@dataclass(slots=True)
class OsuStrains:
    aim: list[float] = field(default_factory=list)
    aim_no_sliders: list[float] = field(default_factory=list)
    speed: list[float] = field(default_factory=list)
    flashlight: list[float] = field(default_factory=list)


class OsuLegacyScoreMissCalculator:
    def __init__(self, state: OsuScoreState, acc: float, mods: GameMods, attrs: OsuDifficultyAttributes):
        self.state = state
        self.acc = acc
        self.mods = mods
        self.attrs = attrs

    def calculate(self) -> float:
        if self.attrs.max_combo == 0 or self.state.legacy_total_score is None:
            return 0.0
        return float(self.state.hitresults.misses)


def prepare_map(difficulty: Any, map_data: Beatmap) -> Beatmap:
    if map_data.mode != GameMode.Osu:
        pass
    return map_data


def convert_objects(map_data: Beatmap, reflection: Reflection) -> list[OsuObject]:
    osu_objects = []
    for h in map_data.hit_objects:
        obj = OsuObject(pos=h.pos, start_time=h.start_time, kind=h.kind)
        osu_objects.append(obj)
    return osu_objects
