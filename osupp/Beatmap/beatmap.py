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

import io
from dataclasses import dataclass

from encode import encode_beatmap
from reader import Decoder
from section.colors import Colors
from section.difficulty import Difficulty, DifficultyState
from section.editor import Editor
from section.enums import GameMode, SampleBank, Section
from section.events import Events
from section.general import General
from section.hit_objects.hit_objects import HitObjectsState
from section.metadata import Metadata
from section.timing_points import ControlPoints, TimingPointsState

LATEST_FORMAT_VERSION = 14


class ParseBeatmapError(Exception):
    """Raised when a beatmap file cannot be parsed."""
    pass


class UnknownFileFormatError(ParseBeatmapError):
    """Raised when the file header does not match the osu! format."""
    pass


def try_version_from_line(line: str) -> int | None:
    """Attempt to parse the format version from the first line of a beatmap file.

    Args:
        line: The first non-empty line of the beatmap file.

    Returns:
        The parsed format version as an integer, or ``None`` if the line is empty.

    Raises:
        UnknownFileFormatError: If the line does not start with the expected header.
        ParseBeatmapError: If the version number cannot be parsed as an integer.
    """
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
    """A fully parsed osu! beatmap.

    Holds all sections of an ``.osu`` file and exposes convenience properties
    for the most commonly accessed fields.

    Attributes:
        format_version: The osu! file format version (e.g. ``14``).
        general: General beatmap settings such as audio filename and game mode.
        editor: Editor-specific settings (bookmarks, grid size, etc.).
        metadata: Song and beatmap metadata (title, artist, creator, IDs).
        difficulty: Difficulty parameters (CS, AR, OD, HP, slider multiplier).
        events: Background, video, and break period declarations.
        timing_points: Timing and control point data.
        colors: Custom combo and skin colours.
        hit_objects: All parsed hit objects.
    """
    format_version: int
    general: General
    editor: Editor
    metadata: Metadata
    difficulty: Difficulty
    events: Events
    timing_points: TimingPointsState
    colors: Colors
    hit_objects: HitObjectsState

    @property
    def control_points(self) -> ControlPoints:
        """Shortcut to the resolved control points from timing data."""
        return self.timing_points.control_points

    # General
    @property
    def mode(self) -> GameMode:
        """The game mode this beatmap is designed for."""
        return self.general.mode

    @property
    def audio_filename(self) -> str:
        """Filename of the beatmap's audio track."""
        return self.general.audio_filename

    @property
    def audio_lead_in(self) -> int:
        """Milliseconds of silence before the audio starts."""
        return self.general.audio_lead_in

    @property
    def preview_time(self) -> int:
        """Timestamp (ms) at which the audio preview starts in song select."""
        return self.general.preview_time

    @property
    def stack_leniency(self) -> float:
        """How often closely stacked notes will be stacked together (0.0-1.0)."""
        return self.general.stack_leniency

    @property
    def letterbox_in_breaks(self) -> bool:
        """Whether to letterbox the playfield during break periods."""
        return self.general.letterbox_in_breaks

    @property
    def widescreen_storyboard(self) -> bool:
        """Whether the storyboard should be rendered at 16:9 aspect ratio."""
        return self.general.widescreen_storyboard

    @property
    def epilepsy_warning(self) -> bool:
        """Whether an epilepsy warning is displayed before the map."""
        return self.general.epilepsy_warning

    @property
    def special_style(self) -> bool:
        """Whether the N+1 key layout is used (osu!mania only)."""
        return self.general.special_style

    @property
    def samples_match_playback_rate(self) -> bool:
        """Whether hitsound samples are pitch-shifted with DT/HT."""
        return self.general.samples_match_playback_rate

    # Metadata
    @property
    def title(self) -> str:
        """Romanised song title."""
        return self.metadata.title

    @property
    def title_unicode(self) -> str:
        """Song title in its original script (may be empty)."""
        return self.metadata.title_unicode

    @property
    def artist(self) -> str:
        """Romanised artist name."""
        return self.metadata.artist

    @property
    def artist_unicode(self) -> str:
        """Artist name in its original script (may be empty)."""
        return self.metadata.artist_unicode

    @property
    def creator(self) -> str:
        """Username of the beatmap creator."""
        return self.metadata.creator

    @property
    def version(self) -> str:
        """Difficulty name (e.g. "Hard", "Insane")."""
        return self.metadata.version

    @property
    def source(self) -> str:
        """Origin of the song (anime, game, etc.)."""
        return self.metadata.source

    @property
    def tags(self) -> str:
        """Space-separated search tags."""
        return self.metadata.tags

    @property
    def beatmap_id(self) -> int:
        """Online beatmap ID, or ``-1`` if not submitted."""
        return self.metadata.beatmap_id

    @property
    def beatmap_set_id(self) -> int:
        """Online beatmap set ID, or ``-1`` if not submitted."""
        return self.metadata.beatmap_set_id

    # Difficulty
    @property
    def hp_drain_rate(self) -> float:
        """HP drain rate (0.0-10.0)."""
        return self.difficulty.hp_drain_rate

    @property
    def circle_size(self) -> float:
        """Circle size / key count (0.0-10.0)."""
        return self.difficulty.circle_size

    @property
    def overall_difficulty(self) -> float:
        """Overall difficulty (0.0-10.0)."""
        return self.difficulty.overall_difficulty

    @property
    def approach_rate(self) -> float:
        """Approach rate (0.0-10.0)."""
        return self.difficulty.approach_rate

    @property
    def slider_multiplier(self) -> float:
        """Base slider velocity in hundreds of osu! pixels per beat."""
        return self.difficulty.slider_multiplier

    @property
    def slider_tick_rate(self) -> float:
        """Number of slider ticks per beat."""
        return self.difficulty.slider_tick_rate

    # Construction
    @classmethod
    def from_path(cls, path: str) -> Beatmap:
        """Parse a beatmap from a file path.

        Args:
            path: Absolute or relative path to a ``.osu`` file.

        Returns:
            A fully parsed Beatmap instance.

        Raises:
            FileNotFoundError: If the file does not exist.
            UnknownFileFormatError: If the file is not a valid osu! beatmap.
            ParseBeatmapError: If any section cannot be parsed.
        """
        with open(path, "rb") as f:
            decoder = Decoder(f)
            return cls._decode(decoder)

    @classmethod
    def from_bytes(cls, data: bytes) -> Beatmap:
        """Parse a beatmap from raw bytes.

        Args:
            data: Raw bytes of a ``.osu`` file.

        Returns:
            A fully parsed Beatmap instance.

        Raises:
            UnknownFileFormatError: If the data is not a valid osu! beatmap.
            ParseBeatmapError: If any section cannot be parsed.
        """
        reader = io.BytesIO(data)
        decoder = Decoder(reader)
        return cls._decode(decoder)

    @classmethod
    def _decode(cls, decoder: Decoder) -> Beatmap:
        """Internal decode implementation shared by all ``from_*`` constructors.

        Args:
            decoder: A Decoder wrapping the beatmap stream.

        Returns:
            A fully parsed Beatmap instance.
        """
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
        colors = Colors()
        hit_objects = HitObjectsState()
        timing_points = TimingPointsState(
            general.mode, general.sample_bank, 100
        )

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
                    timing_points.general_mode = general.mode
                    timing_points.general_default_sample_bank = general.sample_bank
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

        timing_points.flush_pending()

        for break_period in events.breaks:
            if not break_period.has_effect():
                continue

            for obj in hit_objects.hit_objects:
                if obj.start_time > break_period.end_time and hasattr(obj.kind, "new_combo"):
                    obj.kind.new_combo = True
                    break

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

    def to_bytes(self, *, lazer_compatible: bool = False) -> bytes:
        """Encode this beatmap to UTF-8 bytes.

        Args:
            lazer_compatible: If ``True``, encode sample points in lazer format.

        Returns:
            The encoded beatmap as a UTF-8 byte string.
        """
        return self.encode_to_string(lazer_compatible=lazer_compatible).encode("utf-8")

    def encode_to_path(self, path: str, *, lazer_compatible: bool = False) -> None:
        """Write this beatmap to a file.

        Args:
            path: Destination file path.
            lazer_compatible: If ``True``, encode sample points in lazer format.
        """
        with open(path, "w", encoding="utf-8") as f:
            encode_beatmap(self, f, lazer_compatible=lazer_compatible)

    def encode_to_string(self, *, lazer_compatible: bool = False) -> str:
        """Encode this beatmap to a string.

        Args:
            lazer_compatible: If ``True``, encode sample points in lazer format.

        Returns:
            The full ``.osu`` file content as a string.
        """
        writer = io.StringIO()
        encode_beatmap(self, writer, lazer_compatible=lazer_compatible)
        return writer.getvalue()
