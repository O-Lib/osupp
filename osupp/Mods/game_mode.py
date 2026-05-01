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

from enum import IntEnum


class GameMode(IntEnum):
    """osu! game mode identifiers used throughout the Mods module."""
    Osu = 0
    Taiko = 1
    Catch = 2
    Mania = 3

    def as_str(self) -> str:
        """Return the lowercase API string for this game mode (e.g. "osu", "taiko")."""
        return {
            GameMode.Osu: "osu",
            GameMode.Taiko: "taiko",
            GameMode.Catch: "fruits",
            GameMode.Mania: "mania",
        }[self]

    def __str__(self) -> str:
        """Return the lowercase API string for this game mode."""
        return self.as_str()

    @classmethod
    def from_str(cls, s: str) -> "GameMode":
        """Parse a GameMode from a string representation.

        Accepts numeric strings ("0"-"3"), lowercase names ("osu", "taiko", "catch",
        "mania"), and common abbreviations ("tko", "ctb", "mna", "fruits", "osu!").

        Args:
            s: The raw string to parse.

        Returns:
            The corresponding GameMode member.

        Raises:
            ValueError: If the string is not recognised.
        """
        mapping = {
            "0": cls.Osu,
            "osu": cls.Osu,
            "osu!": cls.Osu,
            "1": cls.Taiko,
            "taiko": cls.Taiko,
            "tko": cls.Taiko,
            "2": cls.Catch,
            "catch": cls.Catch,
            "ctb": cls.Catch,
            "fruits": cls.Catch,
            "3": cls.Mania,
            "mania": cls.Mania,
            "mna": cls.Mania,
        }
        key = s.lower()
        if key in mapping:
            return mapping[key]
        raise ValueError(f"Unknown game mode: {s!r}")
