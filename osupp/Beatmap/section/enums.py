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

from enum import Enum, IntEnum, IntFlag


class ParseGameModeError(Exception):
    """Raised when a game mode value cannot be mapped to a known mode."""
    def __init__(self, message: str = "invalid game mode"):
        """Initialise with an optional custom message."""
        super().__init__(message)


class GameMode(IntEnum):
    """osu! game mode identifiers as stored in the beatmap file."""
    Osu = 0
    Taiko = 1
    Catch = 2
    Mania = 3

    @classmethod
    def from_str(cls, mode: str) -> "GameMode":
        """Parse a GameMode from its string representation.

        Args:
            mode: The raw value string (e.g. "0").

        Returns:
            The corresponding GameMode member.

        Raises:
            ParseGameModeError: If the string is not "0"-"3".
        """
        match mode:
            case "0":
                return cls.Osu
            case "1":
                return cls.Taiko
            case "2":
                return cls.Catch
            case "3":
                return cls.Mania
            case _:
                raise ParseGameModeError()

    @classmethod
    def from_int(cls, mode: int) -> "GameMode":
        """Convert an integer to a GameMode, defaulting to Osu for unknown values.

        Args:
            mode: Integer game mode value.

        Returns:
            The corresponding GameMode, or Osu for unknown values.
        """
        match mode:
            case 0:
                return cls.Osu
            case 1:
                return cls.Taiko
            case 2:
                return cls.Catch
            case 3:
                return cls.Mania
            case _:
                return cls.Osu


class ParseCountdownTypeError(Exception):
    """Raised when a countdown type string cannot be parsed."""
    def __init__(self, message: str = "invalid countdown type"):
        """Initialise with an optional custom message."""
        super().__init__(message)


class CountdownType(IntEnum):
    """Countdown animation type before gameplay begins."""
    NONE = 0
    NORMAL = 1
    HALFSPEED = 2
    DOUBLESPEED = 3

    @classmethod
    def from_str(cls, s: str) -> "CountdownType":
        """Parse a CountdownType from its string representation.

        Args:
            s: The raw value string from the Countdown key.

        Returns:
            The corresponding CountdownType member.

        Raises:
            ParseCountdownTypeError: If the string is not recognised.
        """
        match s:
            case "0" | "None":
                return cls.NONE
            case "1" | "Normal":
                return cls.NORMAL
            case "2" | "Half speed":
                return cls.HALFSPEED
            case "3" | "Double speed":
                return cls.DOUBLESPEED
            case _:
                raise ParseCountdownTypeError()


class SampleBank(IntEnum):
    """Hit sound sample bank identifiers."""
    None_ = 0
    Normal = 1
    Soft = 2
    Drum = 3

    def to_lowercase_str(self) -> str:
        """Return the lowercase string name used in osu! file format output."""
        return self.name.lower().replace("none_", "none")

    def __str__(self) -> str:
        """Return the lowercase string representation of this bank."""
        return self.to_lowercase_str()


class HitSoundType(IntFlag):
    """Bit flags representing which hit sounds are active on a hit object."""
    NONE = 0
    NORMAL = 1
    WHISTLE = 2
    FINISH = 4
    CLAP = 8

    def has_flag(self, flag: "HitSoundType") -> bool:
        """Check whether a specific hit sound flag is set.

        Args:
            flag: The HitSoundType flag to test.

        Returns:
            ``True`` if the flag is set.
        """
        return (self.value & flag.value) != 0


class SplineType(Enum):
    """Curve type used to interpolate slider control points."""
    Catmull = 0
    BSpline = 1
    Linear = 2
    PerfectCurve = 3


class Section(Enum):
    """Named sections inside an osu! beatmap file."""
    General = "General"
    Editor = "Editor"
    Metadata = "Metadata"
    Difficulty = "Difficulty"
    Events = "Events"
    TimingPoints = "TimingPoints"
    Colors = "Colours"
    HitObjects = "HitObjects"
    Variables = "Variables"
    CatchTheBeat = "CatchTheBeat"
    Mania = "Mania"

    @classmethod
    def try_from_line(cls, line: str) -> "Section | None":
        """Attempt to parse a section header line such as ``[General]``.

        Args:
            line: A single line from the beatmap file.

        Returns:
            The matching Section member, or ``None`` if not recognised.
        """
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            name = line[1:-1]
            try:
                return cls(name)
            except ValueError:
                return None
        return None
