from __future__ import annotations

import io
from dataclasses import dataclass

from encode import encode_beatmap
from reader import Decoder
from section.colors import Colors
from section.difficulty import Difficulty, DifficultyState
from section.editor import Editor
from section.enums import Section, SampleBank
from section.events import Events
from section.general import General
from section.hit_objects.hit_objects import HitObjectsState
from section.metadata import Metadata
from section.timing_points import TimingPointsState

LATEST_FORMAT_VERSION = 14


class ParseBeatmapError(Exception):
    pass


class UnknownFileFormatError(ParseBeatmapError):
    pass


def try_version_from_line(line: str) -> int | None:
    if not line.startswith("osu file format v"):
        if not line:
            return None
        raise UnknownFileFormatError("unknown file format")

    parts = line.split("v", 1)
    if len(parts) > 1:
        try:
            return int(parts[-1])
        except ValueError:
            raise ParseBeatmapError("failed to parse number in format version")

    return LATEST_FORMAT_VERSION


@dataclass(slots=True, eq=True)
class Beatmap:
    format_version: int
    general: General
    editor: Editor
    metadata: Metadata
    difficulty: Difficulty
    events: Events
    timing_points: TimingPointsState
    colors: Colors
    hit_objects: HitObjectsState

    @classmethod
    def from_path(cls, path: str) -> Beatmap:
        with open(path, "rb") as f:
            decoder = Decoder(f)
            return cls._decode(decoder)

    @classmethod
    def from_bytes(cls, data: bytes) -> Beatmap:
        reader = io.BytesIO(data)
        decoder = Decoder(reader)
        return cls._decode(decoder)

    @classmethod
    def _decode(cls, decoder: Decoder) -> Beatmap:
        format_version = LATEST_FORMAT_VERSION
        use_current_line = False
        current_line_content = ""

        while True:
            line = decoder.read_line()
            if line is None:
                break

            try:
                version = try_version_from_line(line)
                if version is not None:
                    format_version = int(version)
                    break

            except Exception:
                use_current_line = True
                current_line_content = line
                break

        general = General()
        editor = Editor()
        metadata = Metadata()
        difficulty = DifficultyState()
        events = Events()
        timing_points = TimingPointsState(
            general.mode, getattr(general, "sample_bank", SampleBank.Normal), 100
        )
        colors = Colors()
        hit_objects = HitObjectsState()

        current_section: Section | None = None

        if use_current_line:
            sec = Section.try_from_line(current_line_content)
            if sec is not None:
                current_section = sec

        if current_section is None:
            while True:
                line = decoder.read_line()
                if line is None:
                    break
                sec = Section.try_from_line(line)
                if sec is not None:
                    current_section = sec
                    break

        while True:
            line = decoder.read_line()
            if line is None:
                break

            if not line or line.lstrip().startswith("//"):
                continue

            next_section = Section.try_from_line(line)
            if next_section is not None:
                current_section = next_section
                continue

            if current_section is None:
                continue

            try:
                if current_section == Section.General:
                    general.parse_general(line)
                elif current_section == Section.Editor:
                    editor.parse_editor(line)
                elif current_section == Section.Metadata:
                    metadata.parse_metadata(line)
                elif current_section == Section.Difficulty:
                    difficulty.parse_difficulty(line)
                elif current_section == Section.Events:
                    events.parse_events(line)
                elif current_section == Section.TimingPoints:
                    timing_points.parse_timing_points(line)
                elif current_section == Section.Colors:
                    colors.parse_colors(line)
                elif current_section == Section.HitObjects:
                    hit_objects.parse_hit_object(line)
            except Exception:
                pass

        if hasattr(timing_points, "flush_pending"):
            timing_points.flush_pending()

        return cls(
            format_version=format_version,
            general=general,
            editor=editor,
            metadata=metadata,
            difficulty=difficulty.difficulty,
            events=events,
            timing_points=timing_points,
            colors=colors,
            hit_objects=hit_objects,
        )

    def encode_to_path(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            encode_beatmap(self, f)

    def encode_to_string(self) -> str:
        import io

        writer = io.StringIO()
        encode_beatmap(self, writer)
        return writer.getvalue()
