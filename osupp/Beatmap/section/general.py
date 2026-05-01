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

from section.enums import CountdownType, GameMode, SampleBank
from utils import (
    KeyValue,
    ParseNumberError,
    clean_filename,
    parse_float,
    parse_int,
    trim_comment,
)


class ParseGeneralError(Exception):
    """Raised when a line in the [General] section cannot be parsed."""
    def __init__(self, message: str):
        """Initialise with an error message.

        Args:
            message: Description of the parse failure.
        """
        super().__init__(message)


class GeneralKey(Enum):
    """Known keys in the [General] section."""
    AudioFilename = "AudioFilename"
    AudioLeadIn = "AudioLeadIn"
    AudioHash = "AudioHash"
    PreviewTime = "PreviewTime"
    Countdown = "Countdown"
    SampleSet = "SampleSet"
    StackLeniency = "StackLeniency"
    Mode = "Mode"
    LetterboxInBreaks = "LetterboxInBreaks"
    StoryFireInFront = "StoryFireInFront"
    UseSkinSprites = "UseSkinSprites"
    AlwaysShowPlayfield = "AlwaysShowPlayfield"
    OverlayPosition = "OverlayPosition"
    SkinPreference = "SkinPreference"
    EpilepsyWarning = "EpilepsyWarning"
    CountdownOffset = "CountdownOffset"
    SpecialStyle = "SpecialStyle"
    WidescreenStoryboard = "WidescreenStoryboard"
    SamplesMatchPlaybackRate = "SamplesMatchPlaybackRate"

    @classmethod
    def from_str(cls, s: str) -> GeneralKey:
        """Parse a GeneralKey from a raw key string.

        Args:
            s: The key string as it appears in the beatmap file.

        Returns:
            The matching GeneralKey member.

        Raises:
            ValueError: If the string does not match any known key.
        """
        try:
            return cls(s)
        except ValueError:
            raise ValueError("invalid general key")


@dataclass(slots=True, eq=True)
class General:
    """Holds all parsed fields from the [General] section."""
    audio_filename: str
    audio_lead_in: int
    preview_time: int
    countdown: CountdownType
    sample_bank: SampleBank
    stack_leniency: float
    mode: GameMode
    letterbox_in_breaks: bool
    special_style: bool
    widescreen_storyboard: bool
    epilepsy_warning: bool
    samples_match_playback_rate: bool

    def __init__(self):
        """Initialise with default values matching the osu! specification."""
        self.audio_filename = ""
        self.audio_lead_in = 0
        self.preview_time = -1
        self.countdown = CountdownType.NORMAL
        self.sample_bank = SampleBank.Normal
        self.stack_leniency = 0.7
        self.mode = GameMode.Osu
        self.letterbox_in_breaks = False
        self.special_style = False
        self.widescreen_storyboard = False
        self.epilepsy_warning = False
        self.samples_match_playback_rate = False

    def parse_general(self, line: str) -> None:
        """Parse a single key-value line from the [General] section.

        Unknown keys are silently ignored.

        Args:
            line: A single raw line from the [General] section.

        Raises:
            ParseGeneralError: If a numeric value cannot be parsed.
        """
        clean_line = trim_comment(line)

        kv = KeyValue.parse(clean_line, GeneralKey.from_str)
        if kv is None:
            return

        try:
            match kv.key:
                case GeneralKey.AudioFilename:
                    self.audio_filename = clean_filename(kv.value)
                case GeneralKey.AudioLeadIn:
                    self.audio_lead_in = parse_int(kv.value)
                case GeneralKey.PreviewTime:
                    self.preview_time = parse_int(kv.value)
                case GeneralKey.Countdown:
                    try:
                        self.countdown = CountdownType.from_str(kv.value)
                    except Exception:
                        pass
                case GeneralKey.SampleSet:
                    val = kv.value.lower()
                    if val == "none":
                        self.sample_bank = SampleBank.None_
                    elif val == "normal":
                        self.sample_bank = SampleBank.Normal
                    elif val == "soft":
                        self.sample_bank = SampleBank.Soft
                    elif val == "drum":
                        self.sample_bank = SampleBank.Drum
                case GeneralKey.StackLeniency:
                    self.stack_leniency = parse_float(kv.value)
                case GeneralKey.Mode:
                    self.mode = GameMode.from_str(kv.value)
                case GeneralKey.LetterboxInBreaks:
                    self.letterbox_in_breaks = parse_int(kv.value) != 0
                case GeneralKey.SpecialStyle:
                    self.special_style = parse_int(kv.value) != 0
                case GeneralKey.WidescreenStoryboard:
                    self.widescreen_storyboard = parse_int(kv.value) != 0
                case GeneralKey.EpilepsyWarning:
                    self.epilepsy_warning = parse_int(kv.value) != 0
                case GeneralKey.SamplesMatchPlaybackRate:
                    self.samples_match_playback_rate = parse_int(kv.value) != 0

        except (ParseNumberError, ValueError) as e:
            raise ParseGeneralError(f"failed to parse general: {e}")


GeneralState = General
