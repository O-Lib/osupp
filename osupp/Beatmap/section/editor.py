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

from dataclasses import dataclass
from enum import Enum

from utils import KeyValue, ParseNumberError, parse_float, parse_int, trim_comment


class ParseEditorError(Exception):
    """Raised when a line in the [Editor] section cannot be parsed."""
    def __init__(self, message: str):
        """Initialise with an error message.

        Args:
            message: Description of the parse failure.
        """
        super().__init__(message)


class EditorKey(Enum):
    """Known keys in the [Editor] section."""
    Bookmarks = "Bookmarks"
    DistanceSpacing = "DistanceSpacing"
    BeatDivisor = "BeatDivisor"
    GridSize = "GridSize"
    TimelineZoom = "TimelineZoom"

    @classmethod
    def from_str(cls, s: str) -> EditorKey:
        """Parse an EditorKey from a raw key string.

        Args:
            s: The key string as it appears in the beatmap file.

        Returns:
            The matching EditorKey member.

        Raises:
            ValueError: If the string does not match any known key.
        """
        try:
            return cls(s)
        except ValueError:
            raise ValueError("invalid editor key")


@dataclass(slots=True, eq=True)
class Editor:
    """Holds all parsed fields from the [Editor] section."""
    bookmarks: list[int]
    distance_spacing: float
    beat_divisor: int
    grid_size: int
    timeline_zoom: float

    def __init__(self):
        """Initialise with default editor settings."""
        self.bookmarks = []
        self.distance_spacing = 1.0
        self.beat_divisor = 4
        self.grid_size = 0
        self.timeline_zoom = 1.0

    def parse_editor(self, line: str) -> None:
        """Parse a single key-value line from the [Editor] section.

        Unknown keys and invalid bookmark entries are silently ignored.

        Args:
            line: A single raw line from the [Editor] section.

        Raises:
            ParseEditorError: If a numeric value (other than bookmarks) cannot be parsed.
        """
        clean_line = trim_comment(line)

        kv = KeyValue.parse(clean_line, EditorKey.from_str)
        if kv is None:
            return

        try:
            match kv.key:
                case EditorKey.Bookmarks:
                    self.bookmarks = []
                    if kv.value:
                        for part in kv.value.split(","):
                            part = part.strip()
                            if part:
                                try:
                                    self.bookmarks.append(int(part))
                                except ValueError:
                                    pass
                case EditorKey.DistanceSpacing:
                    self.distance_spacing = parse_float(kv.value)
                case EditorKey.BeatDivisor:
                    self.beat_divisor = parse_int(kv.value)
                case EditorKey.GridSize:
                    self.grid_size = parse_int(kv.value)
                case EditorKey.TimelineZoom:
                    self.timeline_zoom = parse_float(kv.value)

        except ParseNumberError as e:
            raise ParseEditorError(f"failed to parse number: {e}")


EditorState = Editor
