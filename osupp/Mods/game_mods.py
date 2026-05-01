"""
MIT License

Copyright (c) 2026-Present O!Lib Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from .acronym import Acronym
from .game_mod import GameMod
from .game_mod_intermode import GameModIntermode
from .game_mode import GameMode


class GameMods:
    """An ordered, deduplicated collection of game-mode-specific GameMod instances."""
    def __init__(self, mods: Iterable[GameMod] = ()) -> None:
        """Initialise the collection, optionally from an iterable of GameMod objects.

        Args:
            mods: Initial mods to insert.
        """
        self._inner: dict[tuple, GameMod] = {}
        for m in mods:
            self.insert(m)

    def _key(self, m: GameMod) -> tuple:
        """Compute the sort key for a GameMod (mode value, kind rank, acronym)."""
        mode = m.mode()
        mode_val = mode.value if mode is not None else -1
        kind_val = m.kind().rank() if m.kind() is not None else 999
        return (mode_val, kind_val, str(m.acronym()))

    def _sorted(self) -> list[GameMod]:
        """Return all mods sorted by their sort key."""
        return sorted(self._inner.values(), key=self._key)

    def insert(self, gamemod: GameMod) -> None:
        """Insert a mod, replacing any existing mod with the same key.

        Args:
            gamemod: The GameMod to insert.
        """
        key = self._key(gamemod)
        self._inner[key] = gamemod

    def remove(self, gamemod: GameMod) -> bool:
        """Remove a mod by value.

        Args:
            gamemod: The GameMod to remove.

        Returns:
            ``True`` if the mod was present and removed.
        """
        key = self._key(gamemod)
        if key in self._inner:
            del self._inner[key]
            return True
        return False

    def remove_acronym(self, acronym: str | Acronym) -> bool:
        """Remove all mods matching the given acronym.

        Args:
            acronym: The acronym to match (case-insensitive).

        Returns:
            ``True`` if any mods were removed.
        """
        s = str(acronym).upper()
        keys = [k for k in self._inner if k[2] == s]
        for k in keys:
            del self._inner[k]
        return bool(keys)

    def extend(self, mods: Iterable[GameMod]) -> None:
        """Insert all mods from an iterable.

        Args:
            mods: Mods to add.
        """
        for m in mods:
            self.insert(m)

    def clear(self) -> None:
        """Remove all mods from the collection."""
        self._inner.clear()

    def is_empty(self) -> bool:
        """Return ``True`` if the collection contains no mods."""
        return len(self._inner) == 0

    def len(self) -> int:
        """Return the number of mods in the collection."""
        return len(self._inner)

    def __len__(self) -> int:
        """Return the number of mods in the collection."""
        return len(self._inner)

    def contains(self, gamemod: GameMod) -> bool:
        """Return ``True`` if the exact mod is present.

        Args:
            gamemod: The GameMod to look up.
        """
        return self._key(gamemod) in self._inner

    def contains_acronym(self, acronym: str | Acronym) -> bool:
        """Return ``True`` if any mod with the given acronym is present.

        Args:
            acronym: The acronym to search for.
        """
        s = str(acronym).upper()
        return any(k[2] == s for k in self._inner)

    def get(
        self, acronym: str | Acronym, mode: GameMode | None = None
    ) -> GameMod | None:
        """Return the first mod matching the acronym (and optionally the mode).

        Args:
            acronym: The acronym to look up.
            mode: Optional game mode filter.

        Returns:
            The matching GameMod, or ``None``.
        """
        s = str(acronym).upper()
        for k, m in self._inner.items():
            if k[2] == s:
                if mode is None or m.mode() == mode:
                    return m
        return None

    def bits(self) -> int:
        """Return the bitwise OR of all legacy bit values in this collection."""
        result = 0
        for m in self._inner.values():
            b = m.bits()
            if b is not None:
                result |= b
        return result

    def checked_bits(self) -> int | None:
        """Return the combined bits, or ``None`` if any mod lacks a bit value."""
        result = 0
        for m in self._inner.values():
            b = m.bits()
            if b is None:
                return None
            result |= b
        return result

    def to_intermode(self):
        """Convert to a GameModsIntermode collection."""
        from .game_mods_intermode import GameModsIntermode

        result = GameModsIntermode()
        for m in self._inner.values():
            intermode = GameModIntermode.from_acronym(str(m.acronym()))
            result.insert(intermode)
        return result

    def __iter__(self) -> Iterator[GameMod]:
        """Iterate over mods in sorted order."""
        return iter(self._sorted())

    def __contains__(self, item: object) -> bool:
        """Support the ``in`` operator for GameMod instances."""
        if isinstance(item, GameMod):
            return self.contains(item)
        return False

    def __ior__(self, other: GameMods) -> GameMods:
        """In-place union: insert all mods from another collection."""
        self.extend(other)
        return self

    def __or__(self, other: GameMods) -> GameMods:
        """Return a new collection containing mods from both collections."""
        result = GameMods(self._sorted())
        result.extend(other)
        return result

    def __str__(self) -> str:
        """Return the concatenated acronym string, or "NM" for an empty set."""
        if not self._inner:
            return "NM"
        return "".join(str(m.acronym()) for m in self._sorted())

    def __repr__(self) -> str:
        """Return an unambiguous representation."""
        return f"GameMods([{', '.join(repr(m) for m in self._sorted())}])"

    def __eq__(self, other: object) -> bool:
        """Two GameMods collections are equal when their inner dicts are equal."""
        if isinstance(other, GameMods):
            return self._inner == other._inner
        return NotImplemented

    def __hash__(self) -> int:
        """Return a hash based on the sorted key tuples."""
        return hash(tuple(self._key(m) for m in self._sorted()))

    @classmethod
    def from_iter(cls, mods: Iterable[GameMod]) -> GameMods:
        """Construct a GameMods collection from an iterable.

        Args:
            mods: The mods to include.

        Returns:
            A new GameMods instance.
        """
        return cls(mods)


def _gamemods_clock_rate(self) -> float | None:
    result = 1.0
    for gm in self:
        cr = gm.clock_rate()
        if cr is None:
            return None
        if cr != 1.0:
            result = cr
    return result


def _gamemod_clock_rate(self) -> float | None:
    from .generated_mods import (
        AdaptiveSpeedMania,
        AdaptiveSpeedOsu,
        AdaptiveSpeedTaiko,
        DaycoreCatch,
        DaycoreMania,
        DaycoreOsu,
        DaycoreTaiko,
        DoubleTimeCatch,
        DoubleTimeMania,
        DoubleTimeOsu,
        DoubleTimeTaiko,
        HalfTimeCatch,
        HalfTimeMania,
        HalfTimeOsu,
        HalfTimeTaiko,
        NightcoreCatch,
        NightcoreMania,
        NightcoreOsu,
        NightcoreTaiko,
        WindDownCatch,
        WindDownMania,
        WindDownOsu,
        WindDownTaiko,
        WindUpCatch,
        WindUpMania,
        WindUpOsu,
        WindUpTaiko,
    )

    _DT = (DoubleTimeOsu, DoubleTimeTaiko, DoubleTimeCatch, DoubleTimeMania)
    _NC = (NightcoreOsu, NightcoreTaiko, NightcoreCatch, NightcoreMania)
    _HT = (HalfTimeOsu, HalfTimeTaiko, HalfTimeCatch, HalfTimeMania)
    _DC = (DaycoreOsu, DaycoreTaiko, DaycoreCatch, DaycoreMania)
    _NONE = (
        WindUpOsu,
        WindUpTaiko,
        WindUpCatch,
        WindUpMania,
        WindDownOsu,
        WindDownTaiko,
        WindDownCatch,
        WindDownMania,
        AdaptiveSpeedOsu,
        AdaptiveSpeedTaiko,
        AdaptiveSpeedMania,
    )

    inner = self._inner
    if isinstance(inner, _NONE):
        return None
    if isinstance(inner, _DT + _NC):
        return inner.speed_change if inner.speed_change is not None else 1.5
    if isinstance(inner, _HT + _DC):
        return inner.speed_change if inner.speed_change is not None else 0.75
    return 1.0


def _gamemods_is_valid(self) -> bool:
    for gm in self:
        own = str(gm.acronym())
        for incompat in gm.incompatible_mods():
            s = str(incompat)
            if s == own:
                continue
            if self.contains_acronym(s):
                return False
    return True


def _gamemods_sanitize(self) -> None:
    changed = True
    while changed:
        changed = False
        for gm in list(self):
            own = str(gm.acronym())
            for incompat in gm.incompatible_mods():
                s = str(incompat)
                if s == own:
                    continue
                keys_to_remove = [k for k in self._inner if k[2] == s]
                if keys_to_remove:
                    for k in keys_to_remove:
                        del self._inner[k]
                    changed = True
                    break
            if changed:
                break


def _gamemods_as_legacy(self):
    from .game_mods_legacy import GameModsLegacy

    return GameModsLegacy.from_bits(self.bits())


def _gamemods_try_as_legacy(self):
    from .game_mods_legacy import GameModsLegacy

    b = self.checked_bits()
    return GameModsLegacy.from_bits(b) if b is not None else None


def _gamemods_contains_intermode(self, gamemod) -> bool:
    s = str(gamemod) if not isinstance(gamemod, str) else gamemod
    return any(k[2] == s.upper() for k in self._inner)


def _gamemods_contains_any(self, mods) -> bool:
    return any(self._gamemods_contains_intermode(self, m) for m in mods)


def _gamemods_remove_intermode(self, gamemod) -> bool:
    s = str(gamemod).upper()
    keys = [k for k in self._inner if k[2] == s]
    for k in keys:
        del self._inner[k]
    return bool(keys)


def _gamemods_remove_all(self, mods) -> None:
    for m in mods:
        self.remove(m)


def _gamemods_remove_all_intermode(self, mods) -> None:
    for m in mods:
        self._gamemods_remove_intermode(self, m)


def _gamemods_intersects(self, other: GameMods) -> bool:
    self_acrs = {k[2] for k in self._inner}
    other_acrs = {k[2] for k in other._inner}
    return bool(self_acrs & other_acrs)


def _gamemods_intersection(self, other: GameMods) -> GameMods:
    from .game_mods import GameMods

    result = GameMods()
    for k, m in self._inner.items():
        if k in other._inner:
            result.insert(m)
    return result


def _gamemods_try_from_intermode(intermode, mode) -> GameMods | None:
    return intermode.try_with_mode(mode)


def _gamemods_from_intermode(intermode, mode) -> GameMods:
    return intermode.with_mode(mode)


from .game_mods import GameMods

GameMods.clock_rate = _gamemods_clock_rate
GameMods.is_valid = _gamemods_is_valid
GameMods.sanitize = _gamemods_sanitize
GameMods.as_legacy = _gamemods_as_legacy
GameMods.try_as_legacy = _gamemods_try_as_legacy
GameMods.contains_intermode = lambda self, m: _gamemods_contains_intermode(self, m)
GameMods.contains_any = lambda self, mods: _gamemods_contains_any(self, mods)
GameMods.remove_intermode = lambda self, m: _gamemods_remove_intermode(self, m)
GameMods.remove_all = lambda self, mods: _gamemods_remove_all(self, mods)
GameMods.remove_all_intermode = lambda self, mods: _gamemods_remove_all_intermode(
    self, mods
)
GameMods.intersects = _gamemods_intersects
GameMods.intersection = _gamemods_intersection
GameMods.try_from_intermode = staticmethod(_gamemods_try_from_intermode)
GameMods.from_intermode = staticmethod(_gamemods_from_intermode)
GameMod.clock_rate = _gamemod_clock_rate


def _gamemods_from_acronyms(s: str, mode=None) -> GameMods:
    from .game_mode import GameMode
    from .game_mods_intermode import GameModsIntermode

    intermode = GameModsIntermode.parse(s)
    return intermode.with_mode(mode if mode is not None else GameMode.Osu)


from .game_mods import GameMods

GameMods.from_acronyms = staticmethod(_gamemods_from_acronyms)
