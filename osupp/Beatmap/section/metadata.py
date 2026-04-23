from dataclasses import dataclass
from enum import Enum
from typing import Optional

from beatmap import Beatmap
from utils import KeyValue, ParseNumber


@dataclass
class Metadata:
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

    def into_beatmap(self) -> "Beatmap":
        return Beatmap(
            title=self.title,
            title_unicode=self.title_unicode,
            artist=self.artist,
            artist_unicode=self.artist_unicode,
            creator=self.creator,
            version=self.version,
            source=self.source,
            tags=self.tags,
            beatmap_id=self.beatmap_id,
            beatmap_set_id=self.beatmap_set_id,
        )

    @classmethod
    def default(cls) -> "Metadata":
        return cls()

    @classmethod
    def create(cls, version: int) -> "MetadataState":
        return cls.default()

    @classmethod
    def parse_metadata(cls, state: "MetadataState", line: str) -> None:
        kv = KeyValue.parse(line, str)
        if kv is None:
            return

        key_enum = MetadataKey.from_str(kv.key)
        if key_enum is None:
            return

        value = kv.value

        try:
            if key_enum == MetadataKey.Title:
                state.title = value
            elif key_enum == MetadataKey.TitleUnicode:
                state.title_unicode = value
            elif key_enum == MetadataKey.Artist:
                state.artist = value
            elif key_enum == MetadataKey.ArtistUnicode:
                state.artist_unicode = value
            elif key_enum == MetadataKey.Creator:
                state.creator = value
            elif key_enum == MetadataKey.Version:
                state.version = value
            elif key_enum == MetadataKey.Source:
                state.source = value
            elif key_enum == MetadataKey.Tags:
                state.tags = value
            elif key_enum == MetadataKey.BeatmapID:
                state.beatmap_id = ParseNumber.parse(value)
            elif key_enum == MetadataKey.BeatmapSetID:
                state.beatmap_set_id = ParseNumber.parse(value)
        except ValueError as e:
            raise ParseMetadataError.from_number(e)

    @classmethod
    def parse_general(cls, state: "MetadataState", line: str) -> None:
        pass

    @classmethod
    def parse_editor(cls, state: "MetadataState", line: str) -> None:
        pass

    @classmethod
    def parse_difficulty(cls, state: "MetadataState", line: str) -> None:
        pass

    @classmethod
    def parse_events(cls, state: "MetadataState", line: str) -> None:
        pass

    @classmethod
    def parse_timing_points(cls, state: "MetadataState", line: str) -> None:
        pass

    @classmethod
    def parse_colors(cls, state: "MetadataState", line: str) -> None:
        pass

    @classmethod
    def parse_hit_objects(cls, state: "MetadataState", line: str) -> None:
        pass

    @classmethod
    def parse_variables(cls, state: "MetadataState", line: str) -> None:
        pass

    @classmethod
    def parse_catch_the_beat(cls, state: "MetadataState", line: str) -> None:
        pass

    @classmethod
    def parse_mania(cls, state: "MetadataState", line: str) -> None:
        pass


MetadataState = Metadata


class MetadataKey(Enum):
    Title = "Title"
    TitleUnicode = "TitleUnicode"
    Artist = "Artist"
    ArtistUnicode = "ArtistUnicode"
    Creator = "Creator"
    Version = "Version"
    Source = "Source"
    Tags = "Tags"
    BeatmapID = "BeatmapID"
    BeatmapSetID = "BeatmapSetID"

    @classmethod
    def from_str(cls, key: str) -> Optional["MetadataKey"]:
        try:
            return cls[key]
        except KeyError:
            return None


class ParseMetadataError(Exception):
    def __init__(self, kind: str, source: Exception):
        self.kind = kind
        self.source = source
        super().__init__(self.get_message())
        self.__cause__ = source

    def get_message(self) -> str:
        if self.kind == "Number":
            return "failed to parse number"
        return "failed to parse metadata"

    @classmethod
    def from_number(cls, err: Exception) -> "ParseMetadataError":
        return cls("Number", err)


@dataclass
class MetadataState:
    metadata: Metadata

    @classmethod
    def create(cls, _version: int) -> "MetadataState":
        return cls(metadata=Metadata.default())

    def to_result(self) -> Metadata:
        return self.metadata
