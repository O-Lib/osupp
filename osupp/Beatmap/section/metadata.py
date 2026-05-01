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

from utils import KeyValue, ParseNumberError, parse_int


class ParseMetadataError(Exception):
    """Raised when a line in the [Metadata] section cannot be parsed."""
    def __init__(self, message: str):
        """Initialise with an error message.

        Args:
            message: Description of the parse failure.
        """
        super().__init__(message)


class MetadataKey(Enum):
    """Known keys in the [Metadata] section."""
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
        """Parse a MetadataKey from a raw key string.

        Args:
            s: The key string as it appears in the beatmap file.

        Returns:
            The matching MetadataKey member.

        Raises:
            ValueError: If the string does not match any known key.
        """
        try:
            return cls(s)
        except ValueError:
            raise ValueError("invalid metadata key")


@dataclass(slots=True, eq=True)
class Metadata:
    """Holds all parsed fields from the [Metadata] section."""
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
        """Initialise with empty strings and -1 for numeric IDs."""
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
        """Parse a single key-value line from the [Metadata] section.

        Args:
            line: A single raw line from the [Metadata] section.

        Raises:
            ParseMetadataError: If a numeric field cannot be parsed.
        """
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
