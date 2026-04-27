from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from utils import KeyValue, ParseNumberError, parse_int


class ParseMetadataError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


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
    def from_str(cls, s: str) -> MetadataKey:
        try:
            return cls(s)
        except ValueError:
            raise ValueError("invalid metadata key")


@dataclass(slots=True, eq=True)
class Metadata:
    title: str
    title_unicode: str
    artist: str
    artist_unicode: str
    creator: str
    version: str
    source: str
    tags: str
    beatmap_id: int
    beatmap_set_id: int

    def __init__(self):
        self.title = ""
        self.title_unicode = ""
        self.artist = ""
        self.artist_unicode = ""
        self.creator = ""
        self.version = ""
        self.source = ""
        self.tags = ""
        self.beatmap_id = -1
        self.beatmap_set_id = -1

    def parse_metadata(self, line: str) -> None:
        kv = KeyValue.parse(line, MetadataKey.from_str)
        if kv is None:
            return

        try:
            match kv.key:
                case MetadataKey.Title:
                    self.title = kv.value
                case MetadataKey.TitleUnicode:
                    self.title_unicode = kv.value
                case MetadataKey.Artist:
                    self.artist = kv.value
                case MetadataKey.ArtistUnicode:
                    self.artist_unicode = kv.value
                case MetadataKey.Creator:
                    self.creator = kv.value
                case MetadataKey.Version:
                    self.version = kv.value
                case MetadataKey.Source:
                    self.source = kv.value
                case MetadataKey.Tags:
                    self.tags = kv.value
                case MetadataKey.BeatmapID:
                    self.beatmap_id = parse_int(kv.value)
                case MetadataKey.BeatmapSetID:
                    self.beatmap_set_id = parse_int(kv.value)

        except ParseNumberError as e:
            raise ParseMetadataError(f"failed to parse number: {e}")


MetadataState = Metadata
