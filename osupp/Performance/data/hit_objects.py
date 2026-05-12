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

from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True)
class Pos:
    x: float
    y: float

@dataclass(slots=True)
class Slider:
    expected_dist: float | None
    repeats: int
    control_points: list[Any] = field(default_factory=list)
    node_sounds: list[Any] = field(default_factory=list)

    @property
    def span_count(self) -> int:
        return self.repeats + 1

@dataclass(slots=True)
class Spinner:
    duration: float

@dataclass(slots=True)
class HoldNote:
    duration: float

@dataclass(slots=True)
class HitObject:
    pos: Pos
    start_time: float
    kind: Slider | Spinner | HoldNote | None = None

    def is_circle(self) -> bool:
        return self.kind is None

    def is_slider(self) -> bool:
        return isinstance(self.kind, Slider)

    def is_spinner(self) -> bool:
        return isinstance(self.kind, Spinner)

    def is_hold_note(self) -> bool:
        return isinstance(self.kind, HoldNote)

    @property
    def end_time(self) -> float:
        if isinstance(self.kind, (Spinner, HoldNote)):
            return self.start_time + self.kind.duration
        return self.start_time