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

import re


class Acronym:
    """A validated 2-4 character uppercase mod acronym (e.g. "HD", "DT", "SV2")."""
    _VALID = re.compile(r"^[A-Z0-9]{2,4}$")

    __slots__ = ("_s",)

    def __init__(self, s: str) -> None:
        """Initialise and validate the acronym string.

        Args:
            s: The raw string. Must match ``[A-Z0-9]{2,4}``.

        Raises:
            ValueError: If the string does not match the required format.
        """
        if not self._VALID.match(s):
            raise ValueError(
                f"Invalid acronym {s!r}: must be 1-4 uppercase letters/digits"
            )
        self._s = s

    @classmethod
    def from_str(cls, s: str) -> "Acronym":
        """Construct an Acronym by uppercasing the input string.

        Args:
            s: The raw string to convert.

        Returns:
            A validated Acronym instance.
        """
        return cls(s.upper())

    def as_str(self) -> str:
        """Return the underlying string value."""
        return self._s

    def __str__(self) -> str:
        """Return the acronym string."""
        return self._s

    def __repr__(self) -> str:
        """Return an unambiguous representation."""
        return f"Acronym({self._s!r})"

    def __eq__(self, other: object) -> bool:
        """Compare with another Acronym or a plain string (case-insensitive)."""
        if isinstance(other, Acronym):
            return self._s == other._s
        if isinstance(other, str):
            return self._s == other.upper()
        return NotImplemented

    def __hash__(self) -> int:
        """Return a hash based on the acronym string."""
        return hash(self._s)

    def __lt__(self, other: "Acronym") -> bool:
        """Support lexicographic ordering."""
        return self._s < other._s
