from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

from utils import KeyValue, ParseNumberError
from beatmap import Beatmap

@dataclass
class Editor:
    bookmarks: List[int]
    distance_spacing: float
    beat_divisor: int
    grid_size: int
    timeline_zoom: float

    @classmethod
    def default(cls) -> "Editor":
        return cls(
            bookmarks=[],
            distance_spacing=1.0,
            beat_divisor=4,
            grid_size=0,
            timeline_zoom=1.0
        )

    def into_beatmap(self) -> "Beatmap":
        return Beatmap(
            bookmarks=self.bookmarks,
            distance_spacing=self.distance_spacing,
            beat_divisor=self.beat_divisor,
            grid_size=self.grid_size,
            timeline_zoom=self.timeline_zoom
        )

    @classmethod
    def create(cls, version: int) -> "EditorState":
        return cls.default()

    def to_result(self) -> "EditorState":
        return self

    @classmethod
    def parse_general(cls, state: "EditorState", line: str) -> None:
        pass

    @classmethod
    def parse_editor(cls, state: "EditorState", line: str) -> None:
        clean_line = line.split('//')[0].strip()

        kv = KeyValue.parse(clean_line)
        if kv is None:
            return

        key_enum = EditorKey.from_str(kv.key)
        if key_enum is None:
            return

        value = kv.value

        try:
            if key_enum == EditorKey.Bookmarks:
                bookmarks = []
                for s in value.split(','):
                    s = s.strip()
                    if not s:
                        continue
                    try:
                        bookmarks.append(int(s))
                    except ValueError:
                        continue
                state.bookmarks = bookmarks
            elif key_enum == EditorKey.DistanceSpacing:
                state.distance_spacing = float(value)

            elif key_enum == EditorKey.BeatDivisor:
                state.beat_divisor = int(value)

            elif key_enum == EditorKey.GridSize:
                state.grid_size = int(value)

            elif key_enum == EditorKey.TimelineZoom:
                state.timeline_zoom = float(value)

        except ValueError as e:
            raise ParseEditorError.from_number(e)

    @classmethod
    def parse_metadata(cls, state: "EditorState", line: str) -> None:
        pass

    @classmethod
    def parse_difficulty(cls, state: "EditorState", line: str) -> None:
        pass

    @classmethod
    def parse_events(cls, state: "EditorState", line: str) -> None:
        pass

    @classmethod
    def parse_timing_points(cls, state: "EditorState", line: str) -> None:
        pass

    @classmethod
    def parse_colors(cls, state: "EditorState", line: str) -> None:
        pass

    @classmethod
    def parse_hit_objects(cls, state: "EditorState", line: str) -> None:
        pass

    @classmethod
    def parse_variables(cls, state: "EditorState", line: str) -> None:
        pass

    @classmethod
    def parse_catch_the_beat(cls, state: "EditorState", line: str) -> None:
        pass

    @classmethod
    def parse_mania(cls, state: "EditorState", line: str) -> None:
        pass

EditorState = Editor

class EditorKey(Enum):
    Bookmarks = "Bookmarks"
    DistanceSpacing = "DistanceSpacing"
    BeatDivisor = "BeatDivisor"
    GridSize = "GridSize"
    TimelineZoom = "TimelineZoom"

    @classmethod
    def from_str(cls, key: str) -> Optional["EditorKey"]:
        return cls.__members__.get(key)

class ParseEditorError(Exception):
    def __init__(self, kind: str, source: Exception):
        self.kind = kind
        self.source = source
        super().__init__(self.get_message())
        self.__cause__ = source

    def get_message(self) -> str:
        if self.kind == "Number":
            return "failed to parse number"
        return "failed to parse editor"

    @classmethod
    def from_number(cls, err: Exception) -> "ParseEditorError":
        return cls("Number", err)