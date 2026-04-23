from __future__ import annotations

import bisect
import copy
import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, TextIO

from utils import Pos

if TYPE_CHECKING:
    from section.colors import Color, Colors, ColorsState, CustomColor, ParseColorsError
    from section.editor import Editor, EditorKey, EditorState, ParseEditorError
    from section.events import BreakPeriod, EventType
    from section.general import CountdownType, GameMode, GeneralKey
    from section.hit_objects import (
        CurveBuffers,
        HitObject,
        HitObjectCircle,
        HitObjectHold,
        HitObjects,
        HitObjectSlider,
        HitObjectSpinner,
        HitObjectsState,
        HitObjectType,
        ParseHitObjectsError,
        SampleBank,
    )
    from section.metadata import (
        Metadata,
        MetadataKey,
        MetadataState,
        ParseMetadataError,
    )
    from section.timing_points import ControlPoints, SamplePoint, TimingPoints
from format_version import LATEST_FORMAT_VERSION

from .encode import (
    ControlPointGroup,
    ControlPointProperties,
    add_path_data,
    collect_samples,
    get_sample_bank,
)


@dataclass
class Beatmap:
    format_version: int = LATEST_FORMAT_VERSION

    # General
    audio_file: str = ""
    audio_lead_in: float = 0.0
    preview_time: int = 0
    default_sample_bank: SampleBank = field(default_factory=lambda: SampleBank.NORMAL)
    default_sample_volume: int = 100
    stack_leniency: float = 0.7
    mode: GameMode = field(default_factory=lambda: GameMode.Osu)
    letterbox_in_breaks: bool = False
    special_style: bool = False
    widescreen_storyboard: bool = False
    epilepsy_warning: bool = False
    samples_match_playback_rate: bool = False
    countdown: CountdownType = field(default_factory=lambda: CountdownType.Normal)
    countdown_offset: int = 0

    # Editor
    bookmarks: list[int] = field(default_factory=list)
    distance_spacing: float = 1.0
    beat_divisor: int = 4
    grid_size: int = 4
    timeline_zoom: float = 1.0

    # Metadata
    title: str = ""
    title_unicode: str = ""
    artist: str = ""
    artist_unicode: str = ""
    creator: str = ""
    version: str = ""
    source: str = ""
    tags: str = ""
    beatmap_id: int = -1
    beatmap_set_id: int = -1

    # Difficulty
    hp_drain_rate: float = 5.0
    circle_size: float = 5.0
    overall_difficulty: float = 5.0
    approach_rate: float = 5.0
    slider_multiplier: float = 1.4
    slider_tick_rate: float = 1.0

    # Events
    background_file: str = ""
    breaks: list[BreakPeriod] = field(default_factory=list)

    # TimingPoints
    control_points: ControlPoints = field(default_factory=lambda: ControlPoints())

    # Colors
    custom_combo_colors: list[Color] = field(default_factory=list)
    custom_colors: list[CustomColor] = field(default_factory=list)

    # HitObjects
    hit_objects: list[HitObject] = field(default_factory=list)

    @staticmethod
    def from_path(path: str | Path) -> Beatmap:
        from decode import from_path

        return from_path(Beatmap, path)

    @staticmethod
    def from_bytes(bytes_data: bytes) -> Beatmap:
        from decode import from_bytes

        return from_bytes(Beatmap, bytes_data)

    @staticmethod
    def from_str(s: str) -> Beatmap:
        from decode import from_str

        return from_str(Beatmap, s)

    @classmethod
    def default(cls) -> Beatmap:
        from section.colors import Colors
        from section.editor import Editor
        from section.hit_objects.decode import HitObjects
        from section.metadata import Metadata

        editor = Editor.default()
        metadata = Metadata.default()
        colors = Colors.default()
        hit_objects = HitObjects.default()

        return cls(
            format_version=LATEST_FORMAT_VERSION,
            # General
            audio_file=hit_objects.audio_file,
            audio_lead_in=hit_objects.audio_lead_in,
            preview_time=hit_objects.preview_time,
            default_sample_bank=hit_objects.default_sample_bank,
            default_sample_volume=hit_objects.default_sample_volume,
            stack_leniency=hit_objects.stack_leniency,
            mode=hit_objects.mode,
            letterbox_in_breaks=hit_objects.letterbox_in_breaks,
            special_style=hit_objects.special_style,
            widescreen_storyboard=hit_objects.widescreen_storyboard,
            epilepsy_warning=hit_objects.epilepsy_warning,
            samples_match_playback_rate=hit_objects.samples_match_playback_rate,
            countdown=hit_objects.countdown,
            countdown_offset=hit_objects.countdown_offset,
            # Editor
            bookmarks=editor.bookmarks,
            distance_spacing=editor.distance_spacing,
            beat_divisor=editor.beat_divisor,
            grid_size=editor.grid_size,
            timeline_zoom=editor.timeline_zoom,
            # Metadata
            title=metadata.title,
            title_unicode=metadata.title_unicode,
            artist=metadata.artist,
            artist_unicode=metadata.artist_unicode,
            creator=metadata.creator,
            version=metadata.version,
            source=metadata.source,
            tags=metadata.tags,
            beatmap_id=metadata.beatmap_id,
            beatmap_set_id=metadata.beatmap_set_id,
            # Difficulty
            hp_drain_rate=hit_objects.hp_drain_rate,
            circle_size=hit_objects.circle_size,
            overall_difficulty=hit_objects.overall_difficulty,
            approach_rate=hit_objects.approach_rate,
            slider_multiplier=hit_objects.slider_multiplier,
            slider_tick_rate=hit_objects.slider_tick_rate,
            # Events
            background_file=hit_objects.background_file,
            breaks=hit_objects.breaks,
            # TimingPoints
            control_points=hit_objects.control_points,
            # Colors
            custom_combo_colors=colors.custom_combo_colors,
            custom_colors=colors.custom_colors,
            # HitObjects
            hit_objects=hit_objects.hit_objects,
        )

    @classmethod
    def from_timing_points(cls, timing_points: TimingPoints):
        beatmap = cls.default()

        beatmap.audio_file = timing_points.audio_file
        beatmap.audio_lead_in = timing_points.audio_lead_in
        beatmap.preview_time = timing_points.preview_time
        beatmap.default_sample_bank = timing_points.default_sample_bank
        beatmap.default_sample_volume = timing_points.default_sample_volume
        beatmap.stack_leniency = timing_points.stack_leniency
        beatmap.mode = timing_points.mode
        beatmap.letterbox_in_breaks = timing_points.letterbox_in_breaks
        beatmap.special_style = timing_points.special_style
        beatmap.widescreen_storyboard = timing_points.widescreen_storyboard
        beatmap.epilepsy_warning = timing_points.epilepsy_warning
        beatmap.samples_match_playback_rate = timing_points.samples_match_playback_rate
        beatmap.countdown = timing_points.countdown
        beatmap.countdown_offset = timing_points.countdown_offset
        beatmap.control_points = timing_points.control_points

        return beatmap

    @classmethod
    def from_hit_objects(cls, hit_objects: HitObjects) -> Beatmap:
        beatmap = cls()

        # Mapeamos os campos do container para o objeto real
        beatmap.audio_file = hit_objects.audio_file
        beatmap.audio_lead_in = hit_objects.audio_lead_in
        beatmap.preview_time = hit_objects.preview_time
        beatmap.default_sample_bank = hit_objects.default_sample_bank
        beatmap.default_sample_volume = hit_objects.default_sample_volume
        beatmap.stack_leniency = hit_objects.stack_leniency
        beatmap.mode = hit_objects.mode
        beatmap.letterbox_in_breaks = hit_objects.letterbox_in_breaks
        beatmap.special_style = hit_objects.special_style
        beatmap.widescreen_storyboard = hit_objects.widescreen_storyboard
        beatmap.epilepsy_warning = hit_objects.epilepsy_warning
        beatmap.samples_match_playback_rate = hit_objects.samples_match_playback_rate
        beatmap.countdown = hit_objects.countdown
        beatmap.countdown_offset = hit_objects.countdown_offset

        # Difficulty
        beatmap.hp_drain_rate = hit_objects.hp_drain_rate
        beatmap.circle_size = hit_objects.circle_size
        beatmap.overall_difficulty = hit_objects.overall_difficulty
        beatmap.approach_rate = hit_objects.approach_rate
        beatmap.slider_multiplier = hit_objects.slider_multiplier
        beatmap.slider_tick_rate = hit_objects.slider_tick_rate

        # Events & Timing
        beatmap.background_file = hit_objects.background_file
        beatmap.breaks = hit_objects.breaks
        beatmap.control_points = hit_objects.control_points
        beatmap.hit_objects = hit_objects.hit_objects

        return beatmap

    @classmethod
    def parse_general(cls, state: BeatmapState, line: str):
        try:
            HitObjects.parse_general(state.hit_objects, line)
        except Exception as e:
            raise ParseBeatmapError.from_hit_objects(e)

    @classmethod
    def parse_editor(cls, state: BeatmapState, line: str):
        try:
            Editor.parse_editor(state.editor, line)
        except Exception as e:
            raise ParseBeatmapError.from_editor(e)

    @classmethod
    def parse_metadata(cls, state: BeatmapState, line: str):
        try:
            Metadata.parse_metadata(state.metadata, line)
        except Exception as e:
            raise ParseBeatmapError.from_metadata(e)

    @classmethod
    def parse_difficulty(cls, state: BeatmapState, line: str):
        try:
            HitObjects.parse_difficulty(state.hit_objects, line)
        except Exception as e:
            raise ParseBeatmapError.from_hit_objects(e)

    @classmethod
    def parse_events(cls, state: BeatmapState, line: str):
        try:
            HitObjects.parse_events(state.hit_objects, line)
        except Exception as e:
            raise ParseBeatmapError.from_hit_objects(e)

    @classmethod
    def parse_timing_points(cls, state: BeatmapState, line: str):
        try:
            HitObjects.parse_timing_points(state.hit_objects, line)
        except Exception as e:
            raise ParseBeatmapError.from_hit_objects(e)

    @classmethod
    def parse_colors(cls, state: BeatmapState, line: str):
        try:
            Colors.parse_colors(state.colors, line)
        except Exception as e:
            raise ParseBeatmapError.from_colors(e)

    @classmethod
    def parse_hit_objects(cls, state: BeatmapState, line: str):
        try:
            HitObjects.parse_hit_objects(state.hit_objects, line)
        except Exception as e:
            raise ParseBeatmapError.from_hit_objects(e)

    @classmethod
    def parse_variables(cls, state: BeatmapState, line: str):
        pass

    @classmethod
    def parse_catch_the_beat(cls, state: BeatmapState, line: str):
        pass

    @classmethod
    def parse_mania(cls, state: BeatmapState, line: str):
        pass

    def encode_to_path(self, path: str) -> None:
        with open(path, "w", enconding="utf-8") as file:
            self.encode(file)

    def encode_to_string(self) -> str:
        writer = io.StringIO()
        self.encode(writer)

    def encode(self, writer: TextIO) -> None:
        writer.write(f"osu file format v{self.format_version}\n")

        writer.write("\n")
        self._encode_general(writer)

        writer.write("\n")
        self._encode_editor(writer)

        writer.write("\n")
        self._encode_metadata(writer)

        writer.write("\n")
        self._encode_difficulty(writer)

        writer.write("\n")
        self._encode_events(writer)

        writer.write("\n")
        self._encode_timing_points(writer)

        writer.write("\n")
        self._encode_colors(writer)

        writer.write("\n")
        self._encode_hit_objects(writer)

    def _encode_general(self, writer: TextIO) -> None:
        writer.write(
            "[General]\n"
            f"{GeneralKey.AudioFilename}: {self.audio_file}\n"
            f"{GeneralKey.AudioLeadIn}: {self.audio_file}\n"
            f"{GeneralKey.PreviewTime}: {self.preview_time}\n"
            f"{GeneralKey.Countdown}: {int(self.countdown)}\n"
        )

        sample_set = SamplePoint.DEFAULT_SAMPLE_BANK
        if self.control_points.sample_points:
            sample_set = self.control_points.sample_points[0].sample_bank

        writer.write(
            f"{GeneralKey.SampleSet}: {int(sample_set)}\n"
            f"{GeneralKey.StackLeniency}: {self.stack_leniency}\n"
            f"{GeneralKey.Mode}: {int(self.mode)}\n"
            f"{GeneralKey.LetterboxInBreaks}: {int(self.letterbox_in_breaks)}\n"
        )

        if self.epilepsy_warning:
            writer.write(f"{GeneralKey.EpilepsyWarning}: 1\n")

        if self.countdown_offset > 0:
            writer.write(f"{GeneralKey.CountdownOffset}: {self.countdown_offset}\n")

        if self.mode == (GameMode.Mania):
            writer.write(f"{GeneralKey.SpecialStyle}: {int(self.special_style)}\n")

        writer.write(
            f"{GeneralKey.WidescreenStoryboard}: {int(self.widescreen_storyboard)}\n"
        )

        if self.sample_match_playback_rate:
            writer.write(f"{GeneralKey.SamplesMatchPlaybackRate}: 1\n")

    def _encode_editor(self, writer: TextIO) -> None:
        writer.write("[Editor]\n")

        if self.bookmarks:
            bookmarks_str = ",".join(str(b) for b in self.bookmarks)
            writer.write(f"Bookmarks: {bookmarks_str}\n")

        writer.write(
            f"{EditorKey.DistanceSpacing}: {self.distance_spacing}\n"
            f"{EditorKey.BeatDivisor}: {self.beat_divisor}\n"
            f"{EditorKey.GridSize}: {self.grid_size}\n"
            f"{EditorKey.TimelineZoom}: {self.timeline_zoom}\n"
        )

    def _encode_metadata(self, writer: TextIO) -> None:
        writer.write("[Metadata]\n")
        writer.write(f"{MetadataKey.Title}: {self.title}\n")

        if self.title_unicode:
            writer.write(f"{MetadataKey.TitleUnicode}: {self.title_unicode}\n")

        writer.write(f"{MetadataKey.Artist}: {self.artist}\n")

        if self.artist_unicode:
            writer.write(f"{MetadataKey.ArtistUnicode}: {self.artist_unicode}\n")

        writer.write(f"{MetadataKey.Creator}: {self.creator}\n")
        writer.write(f"{MetadataKey.Version}: {self.version}\n")

        if self.source:
            writer.write(f"{MetadataKey.Source}: {self.source}\n")

        if self.tags:
            writer.write(f"{MetadataKey.Tags}: {self.tags}\n")

    def _encode_events(self, writer: TextIO) -> None:
        writer.write("[Events]\n")

        if self.background_file:
            writer.write(f'{int(EventType.Break)},0,"{self.background_file}",0,0\n')

        for b in self.breaks:
            writer.write(f"{int(EventType.Break)},{b.start_time},{b.end_time}\n")

    def _encode_timing_points(self, writer: TextIO) -> None:
        def output_control_point_at(
            writer: TextIO, props: ControlPointProperties, is_timing: bool
        ) -> None:
            timing_change = "1" if is_timing else "0"
            writer.write(
                f"{props.timing_signature},{int(props.sample_bank)},"
                f"{props.custom_sample_bank},{props.sample_volume}"
                f"{timing_change},{int(props.effect_flags)}\n"
            )

        control_points = copy.deepcopy(self.control_points)
        collect_samples(self, control_points)

        groups = [
            ControlPointGroup.from_timing(tp) for tp in control_points.timing_points
        ]
        groups.sort(key=lambda a: a.time)

        times = []
        for point in control_points.difficulty_points:
            times.append(point.time)
        for point in control_points.effect_points:
            times.append(point.time)
        for point in control_points.sample_points:
            times.append(point.time)

        for time in times:
            group_times = [g.time for g in groups]
            idx = bisect.bisect_left(group_times, time)
            if idx >= len(groups) or groups[idx].time != time:
                groups.insert(idx, ControlPointGroup.new(time))

        writer.write("[TimingPoints]\n")
        last_props = ControlPointProperties.default()

        for group in groups:
            props = ControlPointProperties.new(
                group.time, control_points, last_props, group.timing is not None
            )

            if group.timing is not None:
                timing = group.timing
                writer.write(f"{timing.time},{timing.beat_len},")
                output_control_point_at(writer, props, True)

                last_props = copy.copy(props)
                last_props.slider_velocity = 1.0

            if props.is_redundant(last_props):
                continue

    def _encode_colors(self, writer: TextIO) -> None:
        writer.write("[Colours]\n")

        for i, color in enumerate(self.custom_combo_colors, start=1):
            writer.write(
                f"Combo{i}: {custom.color.red()},{custom.color.green()},{custom.color.blue()},{custom.color.alpha()}\n"
            )

        for custom in self.custom_colors:
            writer.write(
                f"{custom.name}: {custom.color.red()},{custom.color.green()},{custom.color.blue()},{custom.color.alpha()}\n"
            )

    def _encode_hit_objects(self, writer: TextIO) -> None:
        writer.write("[HitObjects]\n")
        bufs = CurveBuffers

        for hit_object in self.hit_objects:
            if isinstance(hit_object.kind, HitObjectCircle):
                pos = hit_object.kind.pos
            elif isinstance(hit_object.kind, HitObjectSlider):
                pos = hit_object.kind.pos
            elif isinstance(hit_object.kind, HitObjectSpinner):
                pos = hit_object.kind.pos
            elif isinstance(hit_object, HitObjectHold):
                pos = Pos.new(hit_object.pos_x, 192.0)
            else:
                pos = Pos.new(0, 0)

            writer.write(
                f"{pos.x},{pos.y},{hit_object.start_time},"
                f"{int(HitObjectType.from_hit_object(hit_object))},"
                f"{int(HitObjectType.from_hit_object(hit_object.samples))},"
            )

            if isinstance(hit_object.kind, HitObjectCircle):
                pass
            elif isinstance(hit_object.kind, HitObjectSlider):
                add_path_data(writer, hit_object.kind, pos, self.mode, bufs)
            elif isinstance(hit_object.kind, HitObjectSpinner):
                writer.write(f"{hit_object.start_time + hit_object.kind.duration},")
            elif isinstance(hit_object.kind, HitObjectHold):
                writer.write(f"{hit_object.start_time + hit_object.kind.duration}:")

            get_sample_bank(writer, hit_object.samples, False, self.mode)
            writer.write("\n")


class ParseBeatmapError(Exception):
    def __init__(self, kind: str, source: Exception):
        self.kind = kind
        self.source = source
        super().__init__(self.get_message())
        self.__cause__ = source

    def get_message(self) -> str:
        if self.kind == "Colors":
            return "failed to parse colors section"
        elif self.kind == "Editor":
            return "failed to parse editor section"
        elif self.kind == "HitObjects":
            return "failed to parse hit objects"
        elif self.kind == "Metadata":
            return "failed to parse metadata section"
        return "failed to parse beatmap"

    @classmethod
    def from_colors(cls, err: ParseColorsError) -> ParseBeatmapError:
        return cls("Colors", err)

    @classmethod
    def from_editor(cls, err: ParseEditorError) -> ParseBeatmapError:
        return cls("Editor", err)

    @classmethod
    def from_hit_objects(cls, err: ParseHitObjectsError) -> ParseBeatmapError:
        return cls("HitObjects", err)

    @classmethod
    def from_metadata(cls, err: ParseMetadataError) -> ParseBeatmapError:
        return cls("Metadata", err)


@dataclass
class BeatmapState:
    version: int
    editor: EditorState
    metadata: MetadataState
    colors: ColorsState
    hit_objects: HitObjectsState

    @classmethod
    def create(cls, version: int) -> BeatmapState:
        return cls(
            version=version,
            editor=EditorState.create(version),
            metadata=MetadataState.create(version),
            colors=ColorsState.create(version),
            hit_objects=HitObjectsState.create(version),
        )

    def to_beatmap(self) -> Beatmap:
        editor = self.editor.to_result()
        metadata = self.metadata.to_result()
        colors = self.colors.to_result()
        hit_objects = self.hit_objects.to_result()

        return Beatmap(
            format_version=self.version,
            # General
            audio_file=hit_objects.audio_file,
            audio_lead_in=hit_objects.audio_lead_in,
            preview_time=hit_objects.preview_time,
            default_sample_bank=hit_objects.default_sample_bank,
            default_sample_volume=hit_objects.default_sample_volume,
            stack_leniency=hit_objects.stack_leniency,
            mode=hit_objects.mode,
            letterbox_in_breaks=hit_objects.letterbox_in_breaks,
            special_style=hit_objects.special_style,
            widescreen_storyboard=hit_objects.widescreen_storyboard,
            epilepsy_warning=hit_objects.epilepsy_warning,
            samples_match_playback_rate=hit_objects.samples_match_playback_rate,
            countdown=hit_objects.countdown,
            countdown_offset=hit_objects.countdown_offset,
            # Editor
            bookmarks=editor.bookmarks,
            distance_spacing=editor.distance_spacing,
            beat_divisor=editor.beat_divisor,
            grid_size=editor.grid_size,
            timeline_zoom=editor.timeline_zoom,
            # Metadata
            title=metadata.title,
            title_unicode=metadata.title_unicode,
            artist=metadata.artist,
            artist_unicode=metadata.artist_unicode,
            creator=metadata.creator,
            version=metadata.version,
            source=metadata.source,
            tags=metadata.tags,
            beatmap_id=metadata.beatmap_id,
            beatmap_set_id=metadata.beatmap_set_id,
            # Difficulty
            hp_drain_rate=hit_objects.hp_drain_rate,
            circle_size=hit_objects.circle_size,
            overall_difficulty=hit_objects.overall_difficulty,
            approach_rate=hit_objects.approach_rate,
            slider_multiplier=hit_objects.slider_multiplier,
            slider_tick_rate=hit_objects.slider_tick_rate,
            # Events
            background_file=hit_objects.background_file,
            breaks=hit_objects.breaks,
            # TimingPoints
            control_points=hit_objects.control_points,
            # Colors
            custom_combo_colors=colors.custom_combo_colors,
            custom_colors=colors.custom_colors,
            # HitObjects
            hit_objects=hit_objects.hit_objects,
        )
