from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from utils import KeyValue, ParseNumberError, parse_float, parse_int, trim_comment


class ParseEditorError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class EditorKey(Enum):
    Bookmarks = "Bookmarks"
    DistanceSpacing = "DistanceSpacing"
    BeatDivisor = "BeatDivisor"
    GridSize = "GridSize"
    TimelineZoom = "TimelineZoom"

    @classmethod
    def from_str(cls, s: str) -> EditorKey:
        try:
            return cls(s)
        except ValueError:
            raise ValueError("invalid editor key")


@dataclass(slots=True)
class Editor:
    bookmarks: list[int]
    distance_spacing: float
    beat_divisor: int
    grid_size: int
    timeline_zoom: float

    def __init__(self):
        self.bookmarks = []
        self.distance_spacing = 1.0
        self.beat_divisor = 4
        self.grid_size = 0
        self.timeline_zoom = 1.0

    def parse_editor(self, line: str) -> None:
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
