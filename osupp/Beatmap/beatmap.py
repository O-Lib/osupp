from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING, Union

from section.timing_points import TimingPoints

if TYPE_CHECKING:
    from section.colors import Color, Colors, ColorsState, CustomColor, ParseColorsError
    from section.editor import Editor, EditorState, ParseEditorError
    from section.events import BreakPeriod
    from section.general import CountdownType, GameMode
    from section.hit_objects import (
    SampleBank, HitObject, HitObjects,HitObjectsState, ParseHitObjectsError
    )
    from section.metadata import Metadata, MetadataState, ParseMetadataError
    from section.timing_points import ControlPoints
from format_version import LATEST_FORMAT_VERSION

@dataclass
class Beatmap:
    format_version: int = LATEST_FORMAT_VERSION

    #General
    audio_file: str = ""
    audio_lead_in: float = 0.0
    preview_time: int = 0
    default_sample_bank: "SampleBank" = field(default_factory=lambda: SampleBank.Normal)
    default_sample_volume: int = 100
    stack_leniency: float = 0.7
    mode: "GameMode" = field(default_factory=lambda: GameMode.Osu)
    letterbox_in_breaks: bool = False
    special_style: bool = False
    widescreen_storyboard: bool = False
    epilepsy_warning: bool = False
    samples_match_playback_rate: bool = False
    countdown: "CountdownType" = field(default_factory=lambda: CountdownType.Normal)
    countdown_offset: int = 0

    #Editor
    bookmarks: List[int] = field(default_factory=list)
    distance_spacing: float = 1.0
    beat_divisor: int = 4
    grid_size: int = 4
    timeline_zoom: float = 1.0

    #Metadata
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

    #Difficulty
    hp_drain_rate: float = 5.0
    circle_size: float = 5.0
    overall_difficulty: float = 5.0
    approach_rate: float = 5.0
    slider_multiplier: float = 1.4
    slider_tick_rate: float = 1.0

    #Events
    background_file: str = ""
    breaks: List["BreakPeriod"] = field(default_factory=list)

    #TimingPoints
    control_points: "ControlPoints" = field(default_factory=lambda: ControlPoints())

    #Colors
    custom_combo_colors: List["Color"] = field(default_factory=list)
    custom_colors: List["CustomColor"] = field(default_factory=list)

    #HitObjects
    hit_objects: List["HitObject"] = field(default_factory=list)

    @staticmethod
    def from_path(path: Union[str, Path]) -> "Beatmap":
        from decode import from_path
        return from_path(Beatmap, path)

    @staticmethod
    def from_bytes(bytes_data: bytes) -> "Beatmap":
        from decode import from_bytes
        return from_bytes(Beatmap, bytes_data)

    @staticmethod
    def from_str(s: str) -> "Beatmap":
        from decode import from_str
        return from_str(Beatmap, s)

    @classmethod
    def default(cls) -> "Beatmap":
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
    def from_timing_points(cls, timing_points: "TimingPoints"):
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
    def from_hit_objects(cls, hit_objects: 'HitObjects') -> 'Beatmap':
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

class ParseBeatmapError(Exception):
    def __init__(self, kind: str, source: Exception):
        self.kind = kind
        self.source = source
        super().__init__(self.get_message)
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
    def from_colors(cls, err: "ParseColorsError") -> "ParseBeatmapError":
        return cls("Colors", err)

    @classmethod
    def from_editor(cls, err: "ParseEditorError") -> "ParseBeatmapError":
        return cls("Editor", err)

    @classmethod
    def from_hit_objects(cls, err: "ParseHitObjectsError") -> "ParseBeatmapError":
        return cls("HitObjects", err)

    @classmethod
    def from_metadata(cls, err: "ParseMetadataError") -> "ParseBeatmapError":
        return cls("Metadata", err)

@dataclass
class BeatmapState:
    version: int
    editor: "EditorState"
    metadata: "MetadataState"
    colors: "ColorsState"
    hit_objects: "HitObjectsState"

    @classmethod
    def create(cls, version: int) -> "BeatmapState":
        return cls(
            version=version,
            editor=EditorState.create(version),
            metadata=MetadataState.create(version),
            colors=ColorsState.create(version),
            hit_objects=HitObjectsState.create(version),
        )

    def to_beatmap(self) -> "Beatmap":
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