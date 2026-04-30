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

    @property
    def control_points(self) -> ControlPoints:
        return self.timing_points.control_points

    # General
    @property
    def mode(self) -> GameMode:
        return self.general.mode

    @property
    def audio_filename(self) -> str:
        return self.general.audio_filename

    @property
    def audio_lead_in(self) -> int:
        return self.general.audio_lead_in

    @property
    def preview_time(self) -> int:
        return self.general.preview_time

    @property
    def stack_leniency(self) -> float:
        return self.general.stack_leniency

    @property
    def letterbox_in_breaks(self) -> bool:
        return self.general.letterbox_in_breaks

    @property
    def widescreen_storyboard(self) -> bool:
        return self.general.widescreen_storyboard

    @property
    def epilepsy_warning(self) -> bool:
        return self.general.epilepsy_warning

    @property
    def special_style(self) -> bool:
        return self.general.special_style

    @property
    def samples_match_playback_rate(self) -> bool:
        return self.general.samples_match_playback_rate

    # Metadata
    @property
    def title(self) -> str:
        return self.metadata.title

    @property
    def title_unicode(self) -> str:
        return self.metadata.title_unicode

    @property
    def artist(self) -> str:
        return self.metadata.artist

    @property
    def artist_unicode(self) -> str:
        return self.metadata.artist_unicode

    @property
    def creator(self) -> str:
        return self.metadata.creator

    @property
    def version(self) -> str:
        return self.metadata.version

    @property
    def source(self) -> str:
        return self.metadata.source

    @property
    def tags(self) -> str:
        return self.metadata.tags

    @property
    def beatmap_id(self) -> int:
        return self.metadata.beatmap_id

    @property
    def beatmap_set_id(self) -> int:
        return self.metadata.beatmap_set_id

    # Difficulty
    @property
    def hp_drain_rate(self) -> float:
        return self.difficulty.hp_drain_rate

    @property
    def circle_size(self) -> float:
        return self.difficulty.circle_size

    @property
    def overall_difficulty(self) -> float:
        return self.difficulty.overall_difficulty

    @property
    def approach_rate(self) -> float:
        return self.difficulty.approach_rate

    @property
    def slider_multiplier(self) -> float:
        return self.difficulty.slider_multiplier

    @property
    def slider_tick_rate(self) -> float:
        return self.difficulty.slider_tick_rate

    # Construction
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
        return self.encode_to_string(lazer_compatible=lazer_compatible).encode("utf-8")

    def encode_to_path(self, path: str, *, lazer_compatible: bool = False) -> None:
        with open(path, "w", encoding="utf-8") as f:
            encode_beatmap(self, f, lazer_compatible=lazer_compatible)

    def encode_to_string(self, *, lazer_compatible: bool = False) -> str:
        writer = io.StringIO()
        encode_beatmap(self, writer, lazer_compatible=lazer_compatible)
        return writer.getvalue()
