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

from collections.abc import Iterator

_NOMOD = 0
_NOFAIL = 1 << 0
_EASY = 1 << 1
_TOUCHDEVICE = 1 << 2
_HIDDEN = 1 << 3
_HARDROCK = 1 << 4
_SUDDENDEATH = 1 << 5
_DOUBLETIME = 1 << 6
_RELAX = 1 << 7
_HALFTIME = 1 << 8
_NIGHTCORE = (1 << 9) | _DOUBLETIME
_FLASHLIGHT = 1 << 10
_AUTOPLAY = 1 << 11
_SPUNOUT = 1 << 12
_AUTOPILOT = 1 << 13
_PERFECT = (1 << 14) | _SUDDENDEATH
_KEY4 = 1 << 15
_KEY5 = 1 << 16
_KEY6 = 1 << 17
_KEY7 = 1 << 18
_KEY8 = 1 << 19
_FADEIN = 1 << 20
_RANDOM = 1 << 21
_CINEMA = 1 << 22
_TARGET = 1 << 23
_KEY9 = 1 << 24
_KEYCOOP = 1 << 25
_KEY1 = 1 << 26
_KEY3 = 1 << 27
_KEY2 = 1 << 28
_SCOREV2 = 1 << 29
_MIRROR = 1 << 30

_VALID_LEGACY_MASK = _MIRROR | (_MIRROR - 1)
_FROM_BITS_MASK = (2**32 - 1) >> 2


_NAMED_BITS: dict[str, int] = {
    "NoMod": _NOMOD,
    "NoFail": _NOFAIL,
    "Easy": _EASY,
    "TouchDevice": _TOUCHDEVICE,
    "Hidden": _HIDDEN,
    "HardRock": _HARDROCK,
    "SuddenDeath": _SUDDENDEATH,
    "DoubleTime": _DOUBLETIME,
    "Relax": _RELAX,
    "HalfTime": _HALFTIME,
    "Nightcore": _NIGHTCORE,
    "Flashlight": _FLASHLIGHT,
    "Autoplay": _AUTOPLAY,
    "SpunOut": _SPUNOUT,
    "Autopilot": _AUTOPILOT,
    "Perfect": _PERFECT,
    "Key4": _KEY4,
    "Key5": _KEY5,
    "Key6": _KEY6,
    "Key7": _KEY7,
    "Key8": _KEY8,
    "FadeIn": _FADEIN,
    "Random": _RANDOM,
    "Cinema": _CINEMA,
    "Target": _TARGET,
    "Key9": _KEY9,
    "KeyCoop": _KEYCOOP,
    "Key1": _KEY1,
    "Key3": _KEY3,
    "Key2": _KEY2,
    "ScoreV2": _SCOREV2,
    "Mirror": _MIRROR,
}

_ACRONYM_TO_BIT: dict[str, int] = {
    "NM": _NOMOD,
    "NF": _NOFAIL,
    "EZ": _EASY,
    "TD": _TOUCHDEVICE,
    "HD": _HIDDEN,
    "HR": _HARDROCK,
    "SD": _SUDDENDEATH,
    "DT": _DOUBLETIME,
    "RX": _RELAX,
    "RL": _RELAX,
    "HT": _HALFTIME,
    "NC": _NIGHTCORE,
    "FL": _FLASHLIGHT,
    "SO": _SPUNOUT,
    "AP": _AUTOPILOT,
    "PF": _PERFECT,
    "4K": _KEY4,
    "5K": _KEY5,
    "6K": _KEY6,
    "7K": _KEY7,
    "8K": _KEY8,
    "FI": _FADEIN,
    "RD": _RANDOM,
    "CN": _CINEMA,
    "TP": _TARGET,
    "9K": _KEY9,
    "1K": _KEY1,
    "3K": _KEY3,
    "2K": _KEY2,
    "V2": _SCOREV2,
    "MR": _MIRROR,
}

_ITER_ORDER: list[tuple[int, str]] = [
    (_NOFAIL, "NoFail"),
    (_EASY, "Easy"),
    (_TOUCHDEVICE, "TouchDevice"),
    (_HIDDEN, "Hidden"),
    (_HARDROCK, "HardRock"),
    (_SUDDENDEATH, "SuddenDeath"),
    (_DOUBLETIME, "DoubleTime"),
    (_RELAX, "Relax"),
    (_HALFTIME, "HalfTime"),
    (_NIGHTCORE, "Nightcore"),
    (_FLASHLIGHT, "Flashlight"),
    (_AUTOPLAY, "Autoplay"),
    (_SPUNOUT, "SpunOut"),
    (_AUTOPILOT, "Autopilot"),
    (_PERFECT, "Perfect"),
    (_KEY4, "Key4"),
    (_KEY5, "Key5"),
    (_KEY6, "Key6"),
    (_KEY7, "Key7"),
    (_KEY8, "Key8"),
    (_FADEIN, "FadeIn"),
    (_RANDOM, "Random"),
    (_CINEMA, "Cinema"),
    (_TARGET, "Target"),
    (_KEY9, "Key9"),
    (_KEYCOOP, "KeyCoop"),
    (_KEY1, "Key1"),
    (_KEY3, "Key3"),
    (_KEY2, "Key2"),
    (_SCOREV2, "ScoreV2"),
    (_MIRROR, "Mirror"),
]

_NAME_TO_ACRONYM: dict[str, str] = {
    "NoMod": "NM",
    "NoFail": "NF",
    "Easy": "EZ",
    "TouchDevice": "TD",
    "Hidden": "HD",
    "HardRock": "HR",
    "SuddenDeath": "SD",
    "DoubleTime": "DT",
    "Relax": "RX",
    "HalfTime": "HT",
    "Nightcore": "NC",
    "Flashlight": "FL",
    "Autoplay": "",
    "SpunOut": "SO",
    "Autopilot": "AP",
    "Perfect": "PF",
    "Key4": "4K",
    "Key5": "5K",
    "Key6": "6K",
    "Key7": "7K",
    "Key8": "8K",
    "FadeIn": "FI",
    "Random": "RD",
    "Cinema": "",
    "Target": "TP",
    "Key9": "9K",
    "KeyCoop": "",
    "Key1": "1K",
    "Key3": "3K",
    "Key2": "2K",
    "ScoreV2": "V2",
    "Mirror": "MR",
}


class GameModsLegacy:
    """A legacy mod combination stored as a 31-bit integer bitmask.

    Each named class attribute (e.g. ``GameModsLegacy.Hidden``) is a singleton
    instance representing a single mod bit.
    """
    NoMod: GameModsLegacy
    NoFail: GameModsLegacy
    Easy: GameModsLegacy
    TouchDevice: GameModsLegacy
    Hidden: GameModsLegacy
    HardRock: GameModsLegacy
    SuddenDeath: GameModsLegacy
    DoubleTime: GameModsLegacy
    Relax: GameModsLegacy
    HalfTime: GameModsLegacy
    Nightcore: GameModsLegacy
    Flashlight: GameModsLegacy
    Autoplay: GameModsLegacy
    SpunOut: GameModsLegacy
    Autopilot: GameModsLegacy
    Perfect: GameModsLegacy
    Key4: GameModsLegacy
    Key5: GameModsLegacy
    Key6: GameModsLegacy
    Key7: GameModsLegacy
    Key8: GameModsLegacy
    FadeIn: GameModsLegacy
    Random: GameModsLegacy
    Cinema: GameModsLegacy
    Target: GameModsLegacy
    Key9: GameModsLegacy
    KeyCoop: GameModsLegacy
    Key1: GameModsLegacy
    Key3: GameModsLegacy
    Key2: GameModsLegacy
    ScoreV2: GameModsLegacy
    Mirror: GameModsLegacy

    __slots__ = ("_bits",)

    def __init__(self, bits: int = 0) -> None:
        """Initialise from an integer bitfield.

        Args:
            bits: The raw bit value. Masked to 31 bits.
        """
        self._bits = int(bits) & _VALID_LEGACY_MASK

    @classmethod
    def from_bits(cls, bits: int) -> GameModsLegacy:
        """Construct a GameModsLegacy from an integer bitfield.

        Args:
            bits: The raw bit value.

        Returns:
            A GameModsLegacy instance.
        """
        return cls(int(bits) & _FROM_BITS_MASK)

    @classmethod
    def parse(cls, s: str) -> GameModsLegacy:
        """Parse a concatenated 2-letter acronym string (e.g. "HDDT").

        Unknown tokens are silently skipped.

        Args:
            s: The mod string to parse.

        Returns:
            A GameModsLegacy with all recognised mods.
        """
        result = cls(0)
        upper = s.upper()
        i = 0
        while i + 1 < len(upper):
            token = upper[i : i + 2]
            if token in _ACRONYM_TO_BIT:
                result._bits |= _ACRONYM_TO_BIT[token]
            i += 2
        return result

    @classmethod
    def parse_strict(cls, s: str) -> GameModsLegacy:
        """Parse a concatenated acronym string, raising on unknown tokens.

        Args:
            s: The mod string. Length must be even.

        Returns:
            A GameModsLegacy with all mods.

        Raises:
            ValueError: If the string length is odd or an unknown token is encountered.
        """
        result = cls(0)
        upper = s.upper()
        if len(upper) % 2 != 0:
            raise ValueError(f"Failed to parse string {s!r} into GameModsLegacy")
        i = 0
        while i < len(upper):
            token = upper[i : i + 2]
            if token in _ACRONYM_TO_BIT:
                result._bits |= _ACRONYM_TO_BIT[token]
                i += 2
            else:
                raise ValueError(f"Failed to parse string {s!r} into GameModsLegacy")
        return result

    @classmethod
    def _from_name(cls, name: str) -> GameModsLegacy:
        """Construct from a named mod string (internal use)."""
        return cls(_NAMED_BITS[name])

    def bits(self) -> int:
        """Return the raw integer bit value."""
        return self._bits

    def is_empty(self) -> bool:
        """Return ``True`` if no mods are set (NoMod)."""
        return self._bits == 0

    def len(self) -> int:
        """Return the number of individual mods represented by this value."""
        ones = bin(self._bits).count("1")
        if self.contains(GameModsLegacy.Nightcore):
            ones -= 1
        if self.contains(GameModsLegacy.Perfect):
            ones -= 1
        return ones

    def contains(self, other: GameModsLegacy) -> bool:
        """Return ``True`` if all bits of ``other`` are set in this value.

        Args:
            other: The mods to check for.
        """
        return (self._bits & other._bits) == other._bits

    def intersects(self, other: GameModsLegacy) -> bool:
        """Return ``True`` if any bit of ``other`` overlaps with this value.

        Args:
            other: The mods to check against.
        """
        return (self._bits & other._bits) != 0

    def clock_rate(self) -> float:
        """Return the clock rate multiplier for this mod combination.

        Returns:
            1.5 for DoubleTime/Nightcore, 0.75 for HalfTime, 1.0 otherwise.
        """
        if self.contains(GameModsLegacy.DoubleTime):
            return 1.5
        if self.contains(GameModsLegacy.HalfTime):
            return 0.75
        return 1.0

    def iter(self) -> Iterator[GameModsLegacy]:
        """Iterate over individual mod instances that make up this combination."""
        if self._bits == 0:
            yield GameModsLegacy(0)
            return
        remaining = self._bits
        shift = 0
        while shift < 32 and remaining:
            bit = 1 << shift
            shift += 1
            if bit == _DOUBLETIME and (self._bits & _NIGHTCORE) == _NIGHTCORE:
                continue
            if bit == _SUDDENDEATH and (self._bits & _PERFECT) == _PERFECT:
                continue
            check_bit = bit
            if bit == (_NIGHTCORE & ~_DOUBLETIME):
                check_bit = _NIGHTCORE
            if bit == (_PERFECT & ~_SUDDENDEATH):
                check_bit = _PERFECT
            if (self._bits & check_bit) == check_bit and (remaining & check_bit):
                remaining &= ~check_bit
                yield GameModsLegacy(check_bit)

    def __iter__(self) -> Iterator[GameModsLegacy]:
        """Iterate over individual mod instances."""
        return self.iter()

    def named_mods(self) -> list[str]:
        """Return a list of mod name strings for each active mod."""
        result = []
        for m in self.iter():
            b = m._bits
            for bit, name in _ITER_ORDER:
                if bit == b:
                    result.append(name)
                    break
        return result

    def acronyms(self) -> list[str]:
        """Return a list of 2-letter acronyms for each active mod."""
        return [a for n in self.named_mods() if (a := _NAME_TO_ACRONYM[n])]

    def __or__(self, other: GameModsLegacy) -> GameModsLegacy:
        """Return the bitwise OR (union) of two mod sets."""
        return GameModsLegacy(self._bits | other._bits)

    def __ior__(self, other: GameModsLegacy) -> GameModsLegacy:
        """In-place bitwise OR."""
        self._bits |= other._bits
        return self

    def __and__(self, other: GameModsLegacy) -> GameModsLegacy:
        """Return the bitwise AND (intersection) of two mod sets."""
        return GameModsLegacy(self._bits & other._bits)

    def __iand__(self, other: GameModsLegacy) -> GameModsLegacy:
        """In-place bitwise AND."""
        self._bits &= other._bits
        return self

    def __xor__(self, other: GameModsLegacy) -> GameModsLegacy:
        """Return the bitwise XOR (symmetric difference) of two mod sets."""
        return GameModsLegacy(self._bits ^ other._bits)

    def __ixor__(self, other: GameModsLegacy) -> GameModsLegacy:
        """In-place bitwise XOR."""
        self._bits ^= other._bits
        return self

    def __sub__(self, other: GameModsLegacy) -> GameModsLegacy:
        """Return this mod set with bits in ``other`` cleared."""
        return GameModsLegacy(self._bits & ~other._bits)

    def __isub__(self, other: GameModsLegacy) -> GameModsLegacy:
        """In-place subtraction: clear bits present in ``other``."""
        self._bits &= ~other._bits
        return self

    def __invert__(self) -> GameModsLegacy:
        """Return the bitwise complement (all unknown bits are cleared)."""
        return GameModsLegacy(~self._bits & 0xFFFFFFFF)

    def __eq__(self, other: object) -> bool:
        """Compare bit values. Also supports comparison with plain integers."""
        if isinstance(other, GameModsLegacy):
            return self._bits == other._bits
        if isinstance(other, int):
            return self._bits == other
        return NotImplemented

    def __hash__(self) -> int:
        """Return a hash based on the bit value."""
        return hash(self._bits)

    def __lt__(self, other: GameModsLegacy) -> bool:
        """Support numeric ordering."""
        return self._bits < other._bits

    def __le__(self, other: GameModsLegacy) -> bool:
        """Support numeric ordering."""
        return self._bits <= other._bits

    def __gt__(self, other: GameModsLegacy) -> bool:
        """Support numeric ordering."""
        return self._bits > other._bits

    def __ge__(self, other: GameModsLegacy) -> bool:
        """Support numeric ordering."""
        return self._bits >= other._bits

    def __str__(self) -> str:
        """Return the concatenated acronym string, or "NM" for no mods."""
        if self._bits == 0:
            return "NM"
        return "".join(self.acronyms())

    def __repr__(self) -> str:
        """Return an unambiguous representation."""
        return f"GameModsLegacy({self._bits})"

    def __format__(self, spec: str) -> str:
        """Support format spec "b" for binary output, otherwise uses __str__."""
        if spec == "b":
            return format(self._bits, "b")
        return str(self)

    def __int__(self) -> int:
        """Return the integer bit value."""
        return self._bits

    def __index__(self) -> int:
        """Support use as an integer index."""
        return self._bits


for _name, _bit in _NAMED_BITS.items():
    setattr(GameModsLegacy, _name, GameModsLegacy(_bit))
