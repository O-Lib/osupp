from enum import Enum
from typing import Any
from dataclasses import dataclass
from osupp.Beatmap.section.enums import GameMode
from osupp.Beatmap.utils import Pos
import copy

class ConvertError(Exception):
    def __init__(self, from_mode: GameMode | None = None, to_mode: GameMode | None = None):
        if from_mode is not None and to_mode is not None:
            super().__init__(f"Cannot convert from {from_mode.name} to {to_mode.name}")
        else:
            super().__init__("Cannot convert an already converted beatmap")
        self.from_mode = from_mode
        self.to_mode = to_mode


class Reflection(Enum):
    NONE = 0
    VERTICAL = 1
    HORIZONTAL = 2
    BOTH = 3


class GameMods:
    __slots__ = ("_legacy_bits", "_lazer_mods")

    def __init__(self, legacy_bits: int = 0, lazer_mods: list | None = None):
        self._legacy_bits = legacy_bits
        self._lazer_mods = lazer_mods or []

    @property
    def nf(self) -> bool: return bool(self._legacy_bits & 1)

    @property
    def ez(self) -> bool: return bool(self._legacy_bits & 2)

    @property
    def td(self) -> bool: return bool(self._legacy_bits & 4)

    @property
    def hd(self) -> bool: return bool(self._legacy_bits & 8)

    @property
    def hr(self) -> bool: return bool(self._legacy_bits & 16)

    @property
    def rx(self) -> bool: return bool(self._legacy_bits & 128)

    @property
    def fl(self) -> bool: return bool(self._legacy_bits & 1024)

    @property
    def so(self) -> bool: return bool(self._legacy_bits & 4096)

    @property
    def ap(self) -> bool: return bool(self._legacy_bits & 8192)

    @property
    def sv2(self) -> bool: return bool(self._legacy_bits & 536870912)

    @property
    def bl(self) -> bool: return False

    @property
    def cl(self) -> bool: return False

    @property
    def invert(self) -> bool: return False

    @property
    def ho(self) -> bool: return False

    @property
    def tc(self) -> bool: return False

    def clock_rate(self) -> float:
        if self._lazer_mods:
            for mod in self._lazer_mods:
                if hasattr(mod, "clock_rate"):
                    return mod.clock_rate

        if self._legacy_bits & 64:
            return 1.5
        if self._legacy_bits & 512:
            return 1.5
        if self._legacy_bits & 256:
            return 0.75
        if self._legacy_bits & 4194304:
            return 0.75
        return 1.0

    def hardrock_offsets(self) -> bool:
        if self._lazer_mods:
            for mod in self._lazer_mods:
                if type(mod).__name__ == "DifficultyAdjustCatch" and hasattr(mod, "hard_rock_offsets"):
                    return mod.hard_rock_offsets
        return self.hr

    def no_slider_head_acc(self, lazer: bool) -> bool:
        if self._lazer_mods:
            for mod in self._lazer_mods:
                if type(mod).__name__ == "ClassicOsu" and hasattr(mod, "no_slider_head_accuracy"):
                    return mod.no_slider_head_accuracy
            return not lazer
        return not lazer

    def reflection(self) -> Reflection:
        if self._lazer_mods:
            for mod in self._lazer_mods:
                name = type(mod).__name__
                if "HardRockOsu" in name:
                    return Reflection.VERTICAL

                if "MirrorOsu" in name:
                    ref = getattr(mod, "reflection", None)
                    match ref:
                        case "1": return Reflection.VERTICAL
                        case "2": return Reflection.BOTH
                        case None: return Reflection.HORIZONTAL
                        case _: return Reflection.NONE

                if "MirrorCatch" in name:
                    return Reflection.HORIZONTAL
            return Reflection.NONE
        return Reflection.VERTICAL if self.hr else Reflection.NONE

    def mania_keys(self) -> float | None:
        b = self._legacy_bits
        if b & 67108864: return 1.0
        if b & 268435456: return 2.0
        if b & 134217728: return 3.0
        if b & 32768: return 4.0
        if b & 65536: return 5.0
        if b & 131072: return 6.0
        if b & 262144: return 7.0
        if b & 524288: return 8.0
        if b & 16777216: return 9.0
        return None

    def scroll_speed(self) -> float | None:
        if self._lazer_mods:
            for mod in self._lazer_mods:
                if type(mod).__name__ == "DifficultyAdjustTaiko":
                    return getattr(mod, "scroll_speed", None)
        return None

    def random_seed(self) -> int | None:
        if self._lazer_mods:
            for mod in self._lazer_mods:
                if type(mod).__name__ in ("RandomTaiko", "RandomMania"):
                    return getattr(mod, "seed", None)
        return None

    def attraction_strength(self) -> float | None:
        if self._lazer_mods:
            for mod in self._lazer_mods:
                if type(mod).__name__ == "MagnetisedOsu":
                    return getattr(mod, "attraction_strength", None)
        return None

    def deflate_start_scale(self) -> float | None:
        if self._lazer_mods:
            for mod in self._lazer_mods:
                if type(mod).__name__ == "DeflateOsu":
                    return getattr(mod, "start_scale", None)
        return None

    def hd_only_fade_approach_circles(self) -> bool | None:
        if self._lazer_mods:
            for mod in self._lazer_mods:
                if type(mod).__name__ == "HiddenOsu":
                    return getattr(mod, "only_fade_approach_circles", None)
        return None


@dataclass(slots=True)
class HitObject:
    pos: Pos
    start_time: float
    kind: Any

    @property
    def is_circle(self) -> bool:
        return type(self.kind).__name__ == "Circle"

    @property
    def is_slider(self) -> bool:
        return type(self.kind).__name__ == "Slider"

    @property
    def is_spinner(self) -> bool:
        return type(self.kind).__name__ == "Spinner"

    @property
    def is_hold_note(self) -> bool:
        return type(self.kind).__name__ == "Hold"

    @property
    def end_time(self) -> float:
        return getattr(self.kind, "end_time", self.start_time)

    def curve(self, mode: GameMode, reflection: Reflection) -> tuple[list, float]:
        if not self.is_slider:
            return [], 0.0

        points = getattr(self.kind, "control_points", [])
        expected_dist = getattr(self.kind, "expected_dist", 0.0)
        reflected_points = []

        for p in points:
            new_p = copy.copy(p)

            if hasattr(p, "pos"):
                new_pos = Pos(p.pos.x, p.pos.y)
                match reflection:
                    case Reflection.VERTICAL:
                        new_pos.y = -new_pos.y
                    case Reflection.HORIZONTAL:
                        new_pos.x = -new_pos.x
                    case Reflection.BOTH:
                        new_pos.x = -new_pos.x
                        new_pos.y = -new_pos.y
                new_p.pos = new_pos

            reflected_points.append(new_p)

        return reflected_points, expected_dist