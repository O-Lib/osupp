from abc import ABC, abstractmethod
from typing import Any, Optional, Union

from osupp.Beatmap.section.enums import GameMode, HitSoundType
from osupp.Beatmap.section.hit_objects.slider import Curve, PathControlPoint
from osupp.Beatmap.utils import Pos
from osupp.Mods.game_mods import GameMods as LazerGameMods
from osupp.Mods.game_mods_legacy import GameModsLegacy

from ..any.difficulty import Difficulty
from .beatmap.beatmap import Beatmap


class HitObjectKind(ABC):
    pass

class Circle(HitObjectKind):
    pass

class Slider(HitObjectKind):
    __slots__ = ("expected_dist", "repeats", "control_points", "node_sounds")

    def __init__(self, expected_dist: float | None, repeats: int, control_points: list[PathControlPoint], node_sounds: list[HitSoundType]):
        self.expected_dist = expected_dist
        self.repeats = repeats
        self.control_points = control_points
        self.node_sounds = node_sounds

    def span_count(self) -> int:
        return self.repeats + 1

    def curve(self, mode: GameMode, reflection: str) -> Curve:
        points = []

        for p in self.control_points:
            new_pos = Pos(p.pos.x, p.pos.y)

            if reflection == Reflection.VERTICAL:
                new_pos.y = -new_pos.y
            elif reflection == Reflection.HORIZONTAL:
                new_pos.x = -new_pos.x
            elif reflection == Reflection.BOTH:
                new_pos.x = -new_pos.x
                new_pos.y = -new_pos.y

            points.append(PathControlPoint(new_pos, p.path_type))

        return Curve(mode, points, self.expected_dist)

class Spinner(HitObjectKind):
    __slots__ = ("duration",)

    def __init__(self, duration: float):
        self.duration = duration

class HoldNote(HitObjectKind):
    __slots__ = ("duration",)

    def __init__(self, duration: float):
        self.duration = duration


class HitObject:
    __slots__ = ("pos", "start_time", "kind")

    def __init__(self, pos: Pos, start_time: float, kind: HitObjectKind):
        self.pos = pos
        self.start_time = start_time
        self.kind = kind

    def is_circle(self) -> bool:
        return isinstance(self.kind, Circle)

    def is_slider(self) -> bool:
        return isinstance(self.kind, Slider)

    def is_spinner(self) -> bool:
        return isinstance(self.kind, Spinner)

    def is_hold_note(self) -> bool:
        return isinstance(self.kind, HoldNote)

    def end_time(self) -> float:
        if isinstance(self.kind, (Circle, Slider)):
            return self.start_time
        elif isinstance(self.kind, (Spinner, HoldNote)):
            return self.start_time + self.kind.duration
        return self.start_time

    def __lt__(self, other: "HitObject") -> bool:
        return self.start_time < other.start_time


class ConvertError(Exception):
    def __init__(self, message: str, from_mode: GameMode | None = None, to_mode: GameMode | None = None):
        super().__init__(message)
        self.from_mode = from_mode
        self.to_mode = to_mode


class IGameMode(ABC):
    @staticmethod
    @abstractmethod
    def difficulty(difficulty: "Difficulty", map_obj: "Beatmap") -> Any:
        pass

    @staticmethod
    @abstractmethod
    def strains(difficulty: "Difficulty", map_obj: "Beatmap") -> Any:
        pass

    @staticmethod
    @abstractmethod
    def performance(map_obj: "Beatmap") -> Any:
        pass

    @staticmethod
    @abstractmethod
    def gradual_difficulty(difficulty: "Difficulty", map_obj: "Beatmap") -> Any:
        pass

    @staticmethod
    @abstractmethod
    def gradual_performance(difficulty: "Difficulty", map_obj: "Beatmap") -> Any:
        pass


class Reflection:
    NONE = "None"
    VERTICAL = "Vertical"
    HORIZONTAL = "Horizontal"
    BOTH = "Both"


class GameMods:
    def __init__(self, mods: LazerGameMods | GameModsLegacy | int):
        if isinstance(mods, int):
            self.inner = GameModsLegacy.from_bits(mods)
        else:
            self.inner = mods

    @classmethod
    def default(cls) -> "GameMods":
        return cls(GameModsLegacy(0))

    def clock_rate(self) -> float:
        if hasattr(self.inner, "clock_rate"):
            cr = self.inner.clock_rate()
            if cr is not None:
                return cr
        return 1.0

    def hardrock_offsets(self) -> bool:
        return self.hr()

    def no_slider_head_acc(self, lazer: bool) -> bool:
        return not lazer

    def reflection(self) -> str:
        if self.hr():
            return Reflection.VERTICAL
        return Reflection.NONE

    def mania_keys(self) -> float | None:
        if isinstance(self.inner, GameModsLegacy):
            if self.inner.contains(GameModsLegacy.Key1): return 1.0
            if self.inner.contains(GameModsLegacy.Key2): return 2.0
            if self.inner.contains(GameModsLegacy.Key3): return 3.0
            if self.inner.contains(GameModsLegacy.Key4): return 4.0
            if self.inner.contains(GameModsLegacy.Key5): return 5.0
            if self.inner.contains(GameModsLegacy.Key6): return 6.0
            if self.inner.contains(GameModsLegacy.Key7): return 7.0
            if self.inner.contains(GameModsLegacy.Key8): return 8.0
            if self.inner.contains(GameModsLegacy.Key9): return 9.0
        else:
            for i in range(1, 10):
                if self.inner.contains_acronym(f"{i}K"):
                    return float(i)
        return None

    def scroll_speed(self) -> float | None:
        return None

    def random_seed(self) -> int | None:
        return None

    def attraction_strength(self) -> float | None:
        return None

    def deflate_start_scale(self) -> float | None:
        return None

    def hd_only_fade_approach_circles(self) -> bool | None:
        return None

    def _check_mod(self, legacy_mod: GameModsLegacy, acronym: str) -> bool:
        if isinstance(self.inner, GameModsLegacy):
            return self.inner.contains(legacy_mod)
        return self.inner.contains_acronym(acronym)

    def nf(self) -> bool:
        return self._check_mod(GameModsLegacy.NoFail, "NF")

    def ez(self) -> bool:
        return self._check_mod(GameModsLegacy.Easy, "EZ")

    def td(self) -> bool:
        return self._check_mod(GameModsLegacy.TouchDevice, "TD")

    def hd(self) -> bool:
        return self._check_mod(GameModsLegacy.Hidden, "HD")

    def hr(self) -> bool:
        return self._check_mod(GameModsLegacy.HardRock, "HR")

    def rx(self) -> bool:
        return self._check_mod(GameModsLegacy.Relax, "RX")

    def fl(self) -> bool:
        return self._check_mod(GameModsLegacy.Flashlight, "FL")

    def so(self) -> bool:
        return self._check_mod(GameModsLegacy.SpunOut, "SO")

    def ap(self) -> bool:
        return self._check_mod(GameModsLegacy.Autopilot, "AP")

    def sv2(self) -> bool:
        return self._check_mod(GameModsLegacy.ScoreV2, "V2")

    def bl(self) -> bool:
        return False

    def cl(self) -> bool:
        return False

    def invert(self) -> bool:
        return False

    def ho(self) -> bool:
        return False

    def tc(self) -> bool:
        return False
