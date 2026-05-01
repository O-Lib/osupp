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

from enum import Enum
from typing import Union

from .acronym import Acronym
from .game_mod_kind import GameModKind


class UnknownGameMod:
    """Represents a mod acronym that is not recognised by the current mod tables."""
    __slots__ = ("_acronym",)

    def __init__(self, acronym: str) -> None:
        """Initialise with a raw acronym string.

        Args:
            acronym: The unrecognised acronym (will be uppercased).
        """
        self._acronym = acronym.upper()

    def acronym(self) -> Acronym:
        """Return the raw acronym as an Acronym-like object."""
        return _RawAcronym(self._acronym)

    def bits(self) -> int | None:
        """Always returns ``None`` — unknown mods have no legacy bit representation."""
        return None

    def kind(self) -> GameModKind:
        """Return GameModKind.System for all unknown mods."""
        from .game_mod_kind import GameModKind

        return GameModKind.System

    def _order_key(self) -> tuple:
        """Return the sort key tuple used for ordering."""
        return (self.kind().rank(), self._acronym)

    def __lt__(self, other: object) -> bool:
        """Support ordering against other intermode mods."""
        if isinstance(other, (GameModIntermode, UnknownGameMod)):
            return self._order_key() < _order_key_of(other)
        return NotImplemented

    def __le__(self, other: object) -> bool:
        """Support ordering against other intermode mods."""
        if isinstance(other, (GameModIntermode, UnknownGameMod)):
            return self._order_key() <= _order_key_of(other)
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        """Support ordering against other intermode mods."""
        if isinstance(other, (GameModIntermode, UnknownGameMod)):
            return self._order_key() > _order_key_of(other)
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        """Support ordering against other intermode mods."""
        if isinstance(other, (GameModIntermode, UnknownGameMod)):
            return self._order_key() >= _order_key_of(other)
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        """Two UnknownGameMod instances are equal when their acronyms match."""
        if isinstance(other, UnknownGameMod):
            return self._acronym == other._acronym
        return False

    def __hash__(self) -> int:
        """Return a hash based on the acronym."""
        return hash(("__unknown__", self._acronym))

    def __str__(self) -> str:
        """Return the uppercase acronym string."""
        return self._acronym

    def __repr__(self) -> str:
        """Return an unambiguous representation."""
        return f"UnknownGameMod({self._acronym!r})"


class _RawAcronym:
    """Internal acronym wrapper used by UnknownGameMod."""
    __slots__ = ("_s",)

    def __init__(self, s: str) -> None:
        """Initialise with a raw string.

        Args:
            s: The raw acronym string.
        """
        self._s = s

    def as_str(self) -> str:
        """Return the underlying string."""
        return self._s

    def __str__(self) -> str:
        """Return the acronym string."""
        return self._s

    def __repr__(self) -> str:
        """Return an unambiguous representation."""
        return f"Acronym({self._s!r})"

    def __eq__(self, other: object) -> bool:
        """Compare with another _RawAcronym, Acronym, or plain string."""
        if isinstance(other, (_RawAcronym, Acronym)):
            return self._s == str(other)
        if isinstance(other, str):
            return self._s == other.upper()
        return NotImplemented

    def __hash__(self) -> int:
        """Return a hash based on the string value."""
        return hash(self._s)


def _order_key_of(m: AnyIntermode) -> tuple:
    if isinstance(m, UnknownGameMod):
        return m._order_key()
    return (m.kind().rank(), _ACRONYM_MAP[m])


AnyIntermode = Union["GameModIntermode", UnknownGameMod]


class GameModIntermode(Enum):
    """A game-mode-agnostic mod identifier shared across all four osu! modes."""
    AccuracyChallenge = "AccuracyChallenge"
    AdaptiveSpeed = "AdaptiveSpeed"
    Alternate = "Alternate"
    ApproachDifferent = "ApproachDifferent"
    Autopilot = "Autopilot"
    Autoplay = "Autoplay"
    BarrelRoll = "BarrelRoll"
    Blinds = "Blinds"
    Bloom = "Bloom"
    Bubbles = "Bubbles"
    Cinema = "Cinema"
    Classic = "Classic"
    ConstantSpeed = "ConstantSpeed"
    Cover = "Cover"
    Daycore = "Daycore"
    Deflate = "Deflate"
    Depth = "Depth"
    DifficultyAdjust = "DifficultyAdjust"
    DoubleTime = "DoubleTime"
    DualStages = "DualStages"
    Easy = "Easy"
    EightKeys = "EightKeys"
    FadeIn = "FadeIn"
    FiveKeys = "FiveKeys"
    Flashlight = "Flashlight"
    FloatingFruits = "FloatingFruits"
    FourKeys = "FourKeys"
    FreezeFrame = "FreezeFrame"
    Grow = "Grow"
    HalfTime = "HalfTime"
    HardRock = "HardRock"
    Hidden = "Hidden"
    HoldOff = "HoldOff"
    Invert = "Invert"
    Magnetised = "Magnetised"
    Mirror = "Mirror"
    MovingFast = "MovingFast"
    Muted = "Muted"
    Nightcore = "Nightcore"
    NineKeys = "NineKeys"
    NoFail = "NoFail"
    NoRelease = "NoRelease"
    NoScope = "NoScope"
    OneKey = "OneKey"
    Perfect = "Perfect"
    Random = "Random"
    Relax = "Relax"
    Repel = "Repel"
    ScoreV2 = "ScoreV2"
    SevenKeys = "SevenKeys"
    SimplifiedRhythm = "SimplifiedRhythm"
    SingleTap = "SingleTap"
    SixKeys = "SixKeys"
    SpinIn = "SpinIn"
    SpunOut = "SpunOut"
    StrictTracking = "StrictTracking"
    SuddenDeath = "SuddenDeath"
    Swap = "Swap"
    Synesthesia = "Synesthesia"
    TargetPractice = "TargetPractice"
    TenKeys = "TenKeys"
    ThreeKeys = "ThreeKeys"
    TouchDevice = "TouchDevice"
    Traceable = "Traceable"
    Transform = "Transform"
    TwoKeys = "TwoKeys"
    Wiggle = "Wiggle"
    WindDown = "WindDown"
    WindUp = "WindUp"
    Unknown = "Unknown"

    def acronym(self) -> Acronym:
        """Return the 2-4 character acronym for this mod."""
        return Acronym(_ACRONYM_MAP[self])

    def bits(self) -> int | None:
        """Return the legacy bitfield value for this mod, or ``None`` if not applicable."""
        return _BITS_MAP.get(self)

    def kind(self) -> GameModKind:
        """Return the GameModKind category for this mod."""
        return _KIND_MAP[self]

    @classmethod
    def from_acronym(cls, acronym) -> AnyIntermode:
        """Look up a GameModIntermode by acronym string.

        Args:
            acronym: The 2-4 character acronym (case-insensitive).

        Returns:
            The matching GameModIntermode, or an UnknownGameMod if not found.
        """
        s = str(acronym).upper()
        if s in _FROM_ACRONYM:
            return _FROM_ACRONYM[s]
        return UnknownGameMod(s)

    @classmethod
    def try_from_bits(cls, bits: int) -> GameModIntermode | None:
        """Convert a legacy bit value to a ``GameModIntermode``, or ``None``."""
        return _FROM_BITS.get(bits)

    def _order_key(self) -> tuple:
        """Return the sort key tuple used for ordering."""
        return (self.kind().rank(), _ACRONYM_MAP[self])

    def __lt__(self, other: AnyIntermode) -> bool:
        """Support ordering against other intermode mods."""
        return self._order_key() < _order_key_of(other)

    def __le__(self, other: AnyIntermode) -> bool:
        """Support ordering against other intermode mods."""
        return self._order_key() <= _order_key_of(other)

    def __gt__(self, other: AnyIntermode) -> bool:
        """Support ordering against other intermode mods."""
        return self._order_key() > _order_key_of(other)

    def __ge__(self, other: AnyIntermode) -> bool:
        """Support ordering against other intermode mods."""
        return self._order_key() >= _order_key_of(other)

    def __str__(self) -> str:
        """Return the 2-4 character acronym string."""
        return _ACRONYM_MAP[self]

    def __repr__(self) -> str:
        """Return an unambiguous representation."""
        return f"GameModIntermode.{self.value}"


_ACRONYM_MAP: dict[GameModIntermode, str] = {
    GameModIntermode.AccuracyChallenge: "AC",
    GameModIntermode.AdaptiveSpeed: "AS",
    GameModIntermode.Alternate: "AL",
    GameModIntermode.ApproachDifferent: "AD",
    GameModIntermode.Autopilot: "AP",
    GameModIntermode.Autoplay: "AT",
    GameModIntermode.BarrelRoll: "BR",
    GameModIntermode.Blinds: "BL",
    GameModIntermode.Bloom: "BM",
    GameModIntermode.Bubbles: "BU",
    GameModIntermode.Cinema: "CN",
    GameModIntermode.Classic: "CL",
    GameModIntermode.ConstantSpeed: "CS",
    GameModIntermode.Cover: "CO",
    GameModIntermode.Daycore: "DC",
    GameModIntermode.Deflate: "DF",
    GameModIntermode.Depth: "DP",
    GameModIntermode.DifficultyAdjust: "DA",
    GameModIntermode.DoubleTime: "DT",
    GameModIntermode.DualStages: "DS",
    GameModIntermode.Easy: "EZ",
    GameModIntermode.EightKeys: "8K",
    GameModIntermode.FadeIn: "FI",
    GameModIntermode.FiveKeys: "5K",
    GameModIntermode.Flashlight: "FL",
    GameModIntermode.FloatingFruits: "FF",
    GameModIntermode.FourKeys: "4K",
    GameModIntermode.FreezeFrame: "FR",
    GameModIntermode.Grow: "GR",
    GameModIntermode.HalfTime: "HT",
    GameModIntermode.HardRock: "HR",
    GameModIntermode.Hidden: "HD",
    GameModIntermode.HoldOff: "HO",
    GameModIntermode.Invert: "IN",
    GameModIntermode.Magnetised: "MG",
    GameModIntermode.Mirror: "MR",
    GameModIntermode.MovingFast: "MF",
    GameModIntermode.Muted: "MU",
    GameModIntermode.Nightcore: "NC",
    GameModIntermode.NineKeys: "9K",
    GameModIntermode.NoFail: "NF",
    GameModIntermode.NoRelease: "NR",
    GameModIntermode.NoScope: "NS",
    GameModIntermode.OneKey: "1K",
    GameModIntermode.Perfect: "PF",
    GameModIntermode.Random: "RD",
    GameModIntermode.Relax: "RX",
    GameModIntermode.Repel: "RP",
    GameModIntermode.ScoreV2: "SV2",
    GameModIntermode.SevenKeys: "7K",
    GameModIntermode.SimplifiedRhythm: "SR",
    GameModIntermode.SingleTap: "SG",
    GameModIntermode.SixKeys: "6K",
    GameModIntermode.SpinIn: "SI",
    GameModIntermode.SpunOut: "SO",
    GameModIntermode.StrictTracking: "ST",
    GameModIntermode.SuddenDeath: "SD",
    GameModIntermode.Swap: "SW",
    GameModIntermode.Synesthesia: "SY",
    GameModIntermode.TargetPractice: "TP",
    GameModIntermode.TenKeys: "10K",
    GameModIntermode.ThreeKeys: "3K",
    GameModIntermode.TouchDevice: "TD",
    GameModIntermode.Traceable: "TC",
    GameModIntermode.Transform: "TR",
    GameModIntermode.TwoKeys: "2K",
    GameModIntermode.Wiggle: "WG",
    GameModIntermode.WindDown: "WD",
    GameModIntermode.WindUp: "WU",
    GameModIntermode.Unknown: "??",
}

_FROM_ACRONYM: dict[str, GameModIntermode] = {
    v: k for k, v in _ACRONYM_MAP.items() if v != "??"
}

_BITS_MAP: dict[GameModIntermode, int] = {
    GameModIntermode.Autopilot: 8192,
    GameModIntermode.Autoplay: 2048,
    GameModIntermode.Cinema: 4194304,
    GameModIntermode.DoubleTime: 64,
    GameModIntermode.DualStages: 33554432,
    GameModIntermode.Easy: 2,
    GameModIntermode.EightKeys: 524288,
    GameModIntermode.FadeIn: 1048576,
    GameModIntermode.FiveKeys: 65536,
    GameModIntermode.Flashlight: 1024,
    GameModIntermode.FourKeys: 32768,
    GameModIntermode.HalfTime: 256,
    GameModIntermode.HardRock: 16,
    GameModIntermode.Hidden: 8,
    GameModIntermode.Mirror: 1073741824,
    GameModIntermode.Nightcore: 576,
    GameModIntermode.NineKeys: 16777216,
    GameModIntermode.NoFail: 1,
    GameModIntermode.OneKey: 67108864,
    GameModIntermode.Perfect: 16416,
    GameModIntermode.Random: 2097152,
    GameModIntermode.Relax: 128,
    GameModIntermode.ScoreV2: 536870912,
    GameModIntermode.SevenKeys: 262144,
    GameModIntermode.SixKeys: 131072,
    GameModIntermode.SpunOut: 4096,
    GameModIntermode.SuddenDeath: 32,
    GameModIntermode.TargetPractice: 8388608,
    GameModIntermode.ThreeKeys: 134217728,
    GameModIntermode.TouchDevice: 4,
    GameModIntermode.TwoKeys: 268435456,
}

_FROM_BITS: dict[int, GameModIntermode] = {v: k for k, v in _BITS_MAP.items()}

_KIND_MAP: dict[GameModIntermode, GameModKind] = {
    GameModIntermode.AccuracyChallenge: GameModKind.DifficultyIncrease,
    GameModIntermode.AdaptiveSpeed: GameModKind.Fun,
    GameModIntermode.Alternate: GameModKind.Conversion,
    GameModIntermode.ApproachDifferent: GameModKind.Fun,
    GameModIntermode.Autopilot: GameModKind.Automation,
    GameModIntermode.Autoplay: GameModKind.Automation,
    GameModIntermode.BarrelRoll: GameModKind.Fun,
    GameModIntermode.Blinds: GameModKind.DifficultyIncrease,
    GameModIntermode.Bloom: GameModKind.Fun,
    GameModIntermode.Bubbles: GameModKind.Fun,
    GameModIntermode.Cinema: GameModKind.Automation,
    GameModIntermode.Classic: GameModKind.Conversion,
    GameModIntermode.ConstantSpeed: GameModKind.Conversion,
    GameModIntermode.Cover: GameModKind.DifficultyIncrease,
    GameModIntermode.Daycore: GameModKind.DifficultyReduction,
    GameModIntermode.Deflate: GameModKind.Fun,
    GameModIntermode.Depth: GameModKind.Fun,
    GameModIntermode.DifficultyAdjust: GameModKind.Conversion,
    GameModIntermode.DoubleTime: GameModKind.DifficultyIncrease,
    GameModIntermode.DualStages: GameModKind.Conversion,
    GameModIntermode.Easy: GameModKind.DifficultyReduction,
    GameModIntermode.EightKeys: GameModKind.Conversion,
    GameModIntermode.FadeIn: GameModKind.DifficultyIncrease,
    GameModIntermode.FiveKeys: GameModKind.Conversion,
    GameModIntermode.Flashlight: GameModKind.DifficultyIncrease,
    GameModIntermode.FloatingFruits: GameModKind.Fun,
    GameModIntermode.FourKeys: GameModKind.Conversion,
    GameModIntermode.FreezeFrame: GameModKind.Fun,
    GameModIntermode.Grow: GameModKind.Fun,
    GameModIntermode.HalfTime: GameModKind.DifficultyReduction,
    GameModIntermode.HardRock: GameModKind.DifficultyIncrease,
    GameModIntermode.Hidden: GameModKind.DifficultyIncrease,
    GameModIntermode.HoldOff: GameModKind.Conversion,
    GameModIntermode.Invert: GameModKind.Conversion,
    GameModIntermode.Magnetised: GameModKind.Fun,
    GameModIntermode.Mirror: GameModKind.Conversion,
    GameModIntermode.MovingFast: GameModKind.Fun,
    GameModIntermode.Muted: GameModKind.Fun,
    GameModIntermode.Nightcore: GameModKind.DifficultyIncrease,
    GameModIntermode.NineKeys: GameModKind.Conversion,
    GameModIntermode.NoFail: GameModKind.DifficultyReduction,
    GameModIntermode.NoRelease: GameModKind.DifficultyReduction,
    GameModIntermode.NoScope: GameModKind.Fun,
    GameModIntermode.OneKey: GameModKind.Conversion,
    GameModIntermode.Perfect: GameModKind.DifficultyIncrease,
    GameModIntermode.Random: GameModKind.Conversion,
    GameModIntermode.Relax: GameModKind.Automation,
    GameModIntermode.Repel: GameModKind.Fun,
    GameModIntermode.ScoreV2: GameModKind.System,
    GameModIntermode.SevenKeys: GameModKind.Conversion,
    GameModIntermode.SimplifiedRhythm: GameModKind.DifficultyReduction,
    GameModIntermode.SingleTap: GameModKind.Conversion,
    GameModIntermode.SixKeys: GameModKind.Conversion,
    GameModIntermode.SpinIn: GameModKind.Fun,
    GameModIntermode.SpunOut: GameModKind.Automation,
    GameModIntermode.StrictTracking: GameModKind.DifficultyIncrease,
    GameModIntermode.SuddenDeath: GameModKind.DifficultyIncrease,
    GameModIntermode.Swap: GameModKind.Conversion,
    GameModIntermode.Synesthesia: GameModKind.Fun,
    GameModIntermode.TargetPractice: GameModKind.Conversion,
    GameModIntermode.TenKeys: GameModKind.Conversion,
    GameModIntermode.ThreeKeys: GameModKind.Conversion,
    GameModIntermode.TouchDevice: GameModKind.System,
    GameModIntermode.Traceable: GameModKind.DifficultyIncrease,
    GameModIntermode.Transform: GameModKind.Fun,
    GameModIntermode.TwoKeys: GameModKind.Conversion,
    GameModIntermode.Wiggle: GameModKind.Fun,
    GameModIntermode.WindDown: GameModKind.Fun,
    GameModIntermode.WindUp: GameModKind.Fun,
    GameModIntermode.Unknown: GameModKind.System,
}


_DESCRIPTION_MAP: dict[GameModIntermode, str] = {}


def _build_description_map():
    desc = {
        "AC": "Fail if your accuracy drops too low!",
        "AD": "Never trust the approach circles...",
        "AL": "Don't use the same key twice in a row!",
        "AP": "Automatic cursor movement - just follow the rhythm.",
        "AS": "Let track speed adapt to you.",
        "AT": "Watch a perfect automated play through the song.",
        "BL": "Play with blinds on your screen.",
        "BM": "The cursor blooms into.. a larger cursor!",
        "BR": "The whole playfield is on a wheel!",
        "BU": "Don't let their popping distract you!",
        "CL": "Feeling nostalgic?",
        "CN": "Watch the video without visual distractions.",
        "CO": "Decrease the playfield's viewing area.",
        "CS": "No more tricky speed changes!",
        "DA": "Override a beatmap's difficulty settings.",
        "DC": "Whoaaaaa...",
        "DF": "Hit them at the right size!",
        "DP": "3D. Almost.",
        "DS": "Double the stages, double the fun!",
        "DT": "Zoooooooooom...",
        "EZ": "Larger circles, more forgiving HP drain, less accuracy required, and extra lives!",
        "FF": "The fruits are... floating?",
        "FI": "Keys appear out of nowhere!",
        "FL": "Restricted view area.",
        "FR": "Burn the notes into your memory.",
        "GR": "Hit them at the right size!",
        "HD": "Play with no approach circles and fading circles/sliders.",
        "HO": "Replaces all hold notes with normal notes.",
        "HR": "Everything just got a bit harder...",
        "HT": "Less zoom...",
        "IN": "Hold the keys. To the beat.",
        "MF": "Dashing by default, slow down!",
        "MG": "No need to chase the circles – your cursor is a magnet!",
        "MR": "Flip objects on the chosen axes.",
        "MU": "Can you still feel the rhythm without music?",
        "NC": "Uguuuuuuuu...",
        "NF": "You can't fail, no matter what.",
        "NR": "No more timing the end of hold notes.",
        "NS": "Where's the cursor?",
        "PF": "SS or quit.",
        "RD": "It never gets boring!",
        "RP": "Hit objects run away!",
        "RX": "You don't need to click. Give your clicking/tapping fingers a break from the heat of things.",
        "SD": "Miss and fail.",
        "SG": "You must only use one key!",
        "SI": "Circles spin in. No approach circles.",
        "SO": "Spinners will be automatically completed.",
        "SR": "Simplify tricky rhythms!",
        "ST": "Once you start a slider, follow precisely or get a miss.",
        "SV2": "Score set on earlier osu! versions with the V2 scoring algorithm active.",
        "SW": "Dons become kats, kats become dons",
        "SY": "Colours hit objects based on the rhythm.",
        "TC": "Put your faith in the approach circles...",
        "TD": "Automatically applied to plays on devices with a touchscreen.",
        "TP": "Practice keeping up with the beat of the song.",
        "TR": "Everything rotates. EVERYTHING.",
        "WD": "Sloooow doooown...",
        "WG": "They just won't stay still...",
        "WU": "Can you keep up?",
        "1K": "Play with one key.",
        "2K": "Play with two keys.",
        "3K": "Play with three keys.",
        "4K": "Play with four keys.",
        "5K": "Play with five keys.",
        "6K": "Play with six keys.",
        "7K": "Play with seven keys.",
        "8K": "Play with eight keys.",
        "9K": "Play with nine keys.",
        "10K": "Play with ten keys.",
    }
    for intermode, acronym in _ACRONYM_MAP.items():
        if acronym in desc:
            _DESCRIPTION_MAP[intermode] = desc[acronym]


_build_description_map()


def _intermode_description(self) -> str:
    return _DESCRIPTION_MAP.get(self, "")


def _intermode_as_simple(self):
    from .acronym import Acronym
    from .game_mod_simple import GameModSimple

    return GameModSimple(acronym=Acronym(str(self)), settings={})


GameModIntermode.description = _intermode_description
GameModIntermode.as_simple = _intermode_as_simple
