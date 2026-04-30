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
    _VALID = re.compile(r"^[A-Z0-9]{2,4}$")

    __slots__ = ("_s",)

    def __init__(self, s: str) -> None:
        if not self._VALID.match(s):
            raise ValueError(
                f"Invalid acronym {s!r}: must be 1-4 uppercase letters/digits"
            )
        self._s = s

    @classmethod
    def from_str(cls, s: str) -> "Acronym":
        return cls(s.upper())

    def as_str(self) -> str:
        return self._s

    def __str__(self) -> str:
        return self._s

    def __repr__(self) -> str:
        return f"Acronym({self._s!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Acronym):
            return self._s == other._s
        if isinstance(other, str):
            return self._s == other.upper()
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._s)

    def __lt__(self, other: "Acronym") -> bool:
        return self._s < other._s
