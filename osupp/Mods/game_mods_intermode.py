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
from .game_mod_intermode import GameModIntermode, UnknownGameMod


class GameModsIntermode:
    def __init__(self, mods: Iterable[GameModIntermode] = ()) -> None:
        self._inner: list[GameModIntermode] = []
        for m in mods:
            self.insert(m)

    def insert(self, gamemod: GameModIntermode) -> None:
        if gamemod not in self._inner:
            self._inner.append(gamemod)
            self._inner.sort()

    def remove(self, gamemod: GameModIntermode) -> bool:
        if gamemod in self._inner:
            self._inner.remove(gamemod)
            return True
        return False

    def remove_all(self, mods: Iterable[GameModIntermode]) -> None:
        for m in mods:
            self.remove(m)

    def extend(self, mods: Iterable[GameModIntermode]) -> None:
        for m in mods:
            self.insert(m)

    def clear(self) -> None:
        self._inner.clear()

    def is_empty(self) -> bool:
        return len(self._inner) == 0

    def len(self) -> int:
        return len(self._inner)

    def __len__(self) -> int:
        return len(self._inner)

    def contains(self, gamemod: GameModIntermode | str) -> bool:
        if isinstance(gamemod, str):
            gamemod = GameModIntermode.from_acronym(gamemod)
        return gamemod in self._inner

    def contains_acronym(self, acronym: Acronym | str) -> bool:
        s = str(acronym).upper()
        return any(str(m) == s for m in self._inner)

    def bits(self) -> int:
        result = 0
        for m in self._inner:
            b = m.bits()
            if b is not None:
                result |= b
        return result

    def checked_bits(self) -> int | None:
        result = 0
        for m in self._inner:
            b = m.bits()
            if b is None:
                return None
            result |= b
        return result

    def intersection(self, other: GameModsIntermode) -> GameModsIntermode:
        return GameModsIntermode(m for m in self._inner if m in other._inner)

    def union(self, other: GameModsIntermode) -> GameModsIntermode:
        result = GameModsIntermode(self._inner)
        result.extend(other._inner)
        return result

    def difference(self, other: GameModsIntermode) -> GameModsIntermode:
        return GameModsIntermode(m for m in self._inner if m not in other._inner)

    @classmethod
    def from_bits(cls, bits: int) -> GameModsIntermode:
        NC_BITS = 576
        DT_BITS = 64
        PF_BITS = 16416
        SD_BITS = 32

        if (bits & NC_BITS) == NC_BITS:
            bits &= ~DT_BITS
        else:
            bits &= ~(1 << 9)

        if (bits & PF_BITS) == PF_BITS:
            bits &= ~SD_BITS
        else:
            bits &= ~(1 << 14)

        BITFLAG_MODS = [
            GameModIntermode.NoFail,
            GameModIntermode.Easy,
            GameModIntermode.TouchDevice,
            GameModIntermode.Hidden,
            GameModIntermode.HardRock,
            GameModIntermode.SuddenDeath,
            GameModIntermode.DoubleTime,
            GameModIntermode.Relax,
            GameModIntermode.HalfTime,
            GameModIntermode.Nightcore,
            GameModIntermode.Flashlight,
            GameModIntermode.Autoplay,
            GameModIntermode.SpunOut,
            GameModIntermode.Autopilot,
            GameModIntermode.Perfect,
            GameModIntermode.FourKeys,
            GameModIntermode.FiveKeys,
            GameModIntermode.SixKeys,
            GameModIntermode.SevenKeys,
            GameModIntermode.EightKeys,
            GameModIntermode.FadeIn,
            GameModIntermode.Random,
            GameModIntermode.Cinema,
            GameModIntermode.TargetPractice,
            GameModIntermode.NineKeys,
            GameModIntermode.DualStages,
            GameModIntermode.OneKey,
            GameModIntermode.ThreeKeys,
            GameModIntermode.TwoKeys,
            GameModIntermode.ScoreV2,
            GameModIntermode.Mirror,
        ]

        result = cls()
        for bit_pos, gamemod in enumerate(BITFLAG_MODS):
            if bits & (1 << bit_pos):
                result.insert(gamemod)
        return result

    @classmethod
    def from_acronyms(cls, acronyms: Iterable[str | Acronym]) -> GameModsIntermode:
        result = cls()
        for a in acronyms:
            result.insert(GameModIntermode.from_acronym(str(a)))
        return result

    @classmethod
    def parse(cls, s: str) -> GameModsIntermode:
        from .game_mod_intermode import _FROM_ACRONYM

        result = cls()
        s = s.upper()

        if not s or s == "NM":
            return result

        tokens: list[str] = []
        i = 0
        while i < len(s):
            remaining = len(s) - i

            if remaining == 1:
                if tokens:
                    tokens[-1] = tokens[-1] + s[i]
                i += 1

            elif s[i : i + 3] in _FROM_ACRONYM:
                tokens.append(s[i : i + 3])
                i += 3

            else:
                tokens.append(s[i : i + 2])
                i += 2

        for token in tokens:
            if token in _FROM_ACRONYM:
                result.insert(_FROM_ACRONYM[token])
            else:
                result.insert(UnknownGameMod(token))

        return result

    def __iter__(self) -> Iterator[GameModIntermode]:
        return iter(self._inner)

    def __contains__(self, item: object) -> bool:
        return item in self._inner

    def __ior__(self, other: GameModsIntermode) -> GameModsIntermode:
        self.extend(other)
        return self

    def __or__(self, other: GameModsIntermode) -> GameModsIntermode:
        return self.union(other)

    def __sub__(self, other: GameModsIntermode) -> GameModsIntermode:
        return self.difference(other)

    def __isub__(self, other: GameModsIntermode) -> GameModsIntermode:
        self.remove_all(other)
        return self

    def __str__(self) -> str:
        if not self._inner:
            return "NM"
        return "".join(str(m) for m in self._inner)

    def __repr__(self) -> str:
        return f"GameModsIntermode([{', '.join(repr(m) for m in self._inner)}])"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, GameModsIntermode):
            return self._inner == other._inner
        return NotImplemented

    def __hash__(self) -> int:
        return hash(tuple(self._inner))
