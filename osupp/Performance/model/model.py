from enum import Enum
from typing import Any, Optional, Protocol

from osupp.Beatmap.section.enums import GameMode
from osupp.Beatmap.section.hit_objects.hit_objects import (
    HitObject,
    HitObjectCircle,
    HitObjectHold,
    HitObjectSlider,
    HitObjectSpinner,
)
from osupp.Mods.game_mods import GameMods


class Reflection(Enum):
    NONE = 0
    VERTICAL = 1
    HORIZONTAL = 2
    BOTH = 3

def get_reflection(mods: GameMods) -> "Reflection":
    if mods.contains_acronym("HR"):
        return Reflection.VERTICAL

    if mods.contains_acronym("MR"):
        mr_mod = mods.get("MR")
        if mr_mod and hasattr(mr_mod.inner, "reflection") and mr_mod.inner.reflection is not None:
            val = mr_mod.inner.reflection
            if val == "1":
                return Reflection.VERTICAL
            elif val == "2":
                return Reflection.BOTH
            return Reflection.NONE

        return Reflection.HORIZONTAL

    return Reflection.NONE

def get_end_time(obj: HitObject) -> float:
    if isinstance(obj.kind, (HitObjectCircle, HitObjectSlider)):
        return obj.start_time
    elif isinstance(obj.kind, (HitObjectSpinner, HitObjectHold)):
        return obj.start_time + obj.kind.duration
    return obj.start_time

def is_circle(obj: HitObject) -> bool:
    return isinstance(obj.kind, HitObjectCircle)

def is_slider(obj: HitObject) -> bool:
    return isinstance(obj.kind, HitObjectSlider)

def is_spinner(obj: HitObject) -> bool:
    return isinstance(obj.kind, HitObjectSpinner)

def is_hold_note(obj: HitObject) -> bool:
    return isinstance(obj.kind, HitObjectHold)


class CalculateError(Exception):
    pass

class ConvertError(Exception):
    def __init__(self, from_mode: GameMode, to_mode: GameMode):
        self.from_mode = from_mode
        self.to_mode = to_mode
        super().__init__(f"It is not possible to convert the map from {from_mode.name} to {to_mode.name}")

class AlreadyConvertedError(Exception):
    def __init__(self):
        super().__init__("The map has already been converted.")


class IGameMode(Protocol):
    @classmethod
    def difficulty(cls, difficulty_settings: Any, map_data: Any) -> Any:
        ...

    @classmethod
    def checked_difficulty(cls, difficulty_settings: Any, map_data: Any) -> Any:
        ...

    @classmethod
    def strains(cls, difficulty_settings: Any, map_data: Any) -> Any:
        ...

    @classmethod
    def performance(cls, map_data: Any) -> Any:
        ...


def get_mania_keys(mods: GameMods) -> float | None:
    for keys in range(1, 11):
        if mods.contains_acronym(f"{keys}K"):
            return float(keys)
    return None

def get_scroll_speed(mods: GameMods) -> float | None:
    da_mod = mods.get("DA", GameMode.Taiko)
    if da_mod and hasattr(da_mod.inner, "scroll_speed") and da_mod.inner.scroll_speed is not None:
        return float(da_mod.inner.scroll_speed)
    return None

def get_attraction_strength(mods: GameMods) -> float | None:
    mg_mod = mods.get("MG")
    if mg_mod and hasattr(mg_mod.inner, "attraction_strength") and mg_mod.inner.attraction_strength is not None:
        return float(mg_mod.inner.attraction_strength)
    return None
