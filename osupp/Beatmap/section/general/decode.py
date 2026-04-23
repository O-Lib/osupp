from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from beatmap import Beatmap
from section.hit_objects.hit_samples import SampleBank
from utils import KeyValue, StrExtra

from .mod import CountdownType, GameMode


class ParseGeneralError(Exception):
    def __init__(self, kind: str, source: Exception):
        self.kind = kind
        self.source = source
        super().__init__(self.get_message())
        self.__cause__ = source

    def get_message(self) -> str:
        messages = {
            "CountdownType": "failed to parse countdown type",
            "Mode": "failed to parse mode",
            "Number": "failed to parse number",
            "SampleBank": "failed to parse sample bank",
        }
        return messages.get(self.kind, "failed to parse general section")

    @classmethod
    def from_countdown_type(cls, err: Exception) -> ParseGeneralError:
        return cls("CountdownType", err)

    @classmethod
    def from_mode(cls, err: Exception) -> ParseGeneralError:
        return cls("Mode", err)

    @classmethod
    def from_number(cls, err: Exception) -> ParseGeneralError:
        return cls("Number", err)

    @classmethod
    def from_sample_bank(cls, err: Exception) -> ParseGeneralError:
        return cls("SampleBank", err)


@dataclass
class General:
    audio_file: str = ""
    audio_lead_in: float = 0.0
    preview_time: int = -1
    default_sample_bank: SampleBank = 0
    default_sample_volume: int = 100
    stack_leniency: float = 0.7
    mode: GameMode = GameMode.default()
    letterbox_in_breaks: bool = False
    special_style: bool = False
    widescreen_storyboard: bool = False
    epilepsy_warning: bool = False
    samples_match_playback_rate: bool = False
    countdown: CountdownType = CountdownType.default()
    countdown_offset: int = 0

    @classmethod
    def default(cls) -> General:
        return cls()

    def into_beatmap(self) -> Beatmap:
        return Beatmap(
            audio_file=self.audio_file,
            audio_lead_in=self.audio_lead_in,
            preview_time=self.preview_time,
            default_sample_bank=self.default_sample_bank,
            default_sample_volume=self.default_sample_volume,
            stack_leniency=self.stack_leniency,
            mode=self.mode,
            letterbox_in_breaks=self.letterbox_in_breaks,
            special_style=self.special_style,
            widescreen_storyboard=self.widescreen_storyboard,
            epilepsy_warning=self.epilepsy_warning,
            samples_match_playback_rate=self.samples_match_playback_rate,
            countdown=self.countdown,
            countdown_offset=self.countdown_offset,
        )

    @classmethod
    def create(cls, version: int) -> GeneralState:
        return cls.default()

    def to_result(self) -> GeneralState:
        return self

    @classmethod
    def parse_general(cls, state: GeneralState, line: str) -> None:
        clean_line = line.split("//")[0].strip()

        kv = KeyValue.parse(clean_line, str)
        if kv is None:
            return

        key_enum = GeneralKey.from_str(kv.key)
        if key_enum is None:
            return

        value = kv.value

        try:
            if key_enum == GeneralKey.AudioFilename:
                state.audio_file = StrExtra.clean_filename(value)

            elif key_enum == GeneralKey.AudioLeadIn:
                state.audio_lead_in = float(value)

            elif key_enum == GeneralKey.PreviewTime:
                state.preview_time = int(value)

            elif key_enum == GeneralKey.SampleSet:
                try:
                    if value.isdigit():
                        state.default_sample_bank = int(value)
                    else:
                        pass
                except ValueError as e:
                    raise ParseGeneralError.from_sample_bank(e)

            elif key_enum == GeneralKey.SampleVolume:
                state.default_sample_volume = int(value)

            elif key_enum == GeneralKey.StackLeniency:
                state.stack_leniency = float(value)

            elif key_enum == GeneralKey.Mode:
                try:
                    state.mode = GameMode.from_str(value)
                except Exception as e:
                    raise ParseGeneralError.from_mode(e)

            elif key_enum == GeneralKey.LetterboxInBreaks:
                state.letterbox_in_breaks = int(value) == 1

            elif key_enum == GeneralKey.SpecialStyle:
                state.special_style = int(value) == 1

            elif key_enum == GeneralKey.WidescreenStoryboard:
                state.widescreen_storyboard = int(value) == 1

            elif key_enum == GeneralKey.EpilepsyWarning:
                state.epilepsy_warning = int(value) == 1

            elif key_enum == GeneralKey.SamplesMatchPlaybackRate:
                state.samples_match_playback_rate = int(value) == 1

            elif key_enum == GeneralKey.Countdown:
                try:
                    state.countdown = CountdownType.from_str(value)
                except Exception as e:
                    raise ParseGeneralError.from_countdown_type(e)

            elif key_enum == GeneralKey.CountdownOffset:
                state.countdown_offset = int(value)

        except ValueError as e:
            raise ParseGeneralError.from_number(e)

    @classmethod
    def parse_editor(cls, state: GeneralState, line: str) -> None:
        pass

    @classmethod
    def parse_metadata(cls, state: GeneralState, line: str) -> None:
        pass

    @classmethod
    def parse_difficulty(cls, state: GeneralState, line: str) -> None:
        pass

    @classmethod
    def parse_events(cls, state: GeneralState, line: str) -> None:
        pass

    @classmethod
    def parse_timing_points(cls, state: GeneralState, line: str) -> None:
        pass

    @classmethod
    def parse_colors(cls, state: GeneralState, line: str) -> None:
        pass

    @classmethod
    def parse_hit_objects(cls, state: GeneralState, line: str) -> None:
        pass

    @classmethod
    def parse_variables(cls, state: GeneralState, line: str) -> None:
        pass

    @classmethod
    def parse_catch_the_beat(cls, state: GeneralState, line: str) -> None:
        pass

    @classmethod
    def parse_mania(cls, state: GeneralState, line: str) -> None:
        pass


GeneralState = General


class GeneralKey(Enum):
    AudioFilename = "AudioFilename"
    AudioLeadIn = "AudioLeadIn"
    PreviewTime = "PreviewTime"
    SampleSet = "SampleSet"
    SampleVolume = "SampleVolume"
    StackLeniency = "StackLeniency"
    Mode = "Mode"
    LetterboxInBreaks = "LetterboxInBreaks"
    SpecialStyle = "SpecialStyle"
    WidescreenStoryboard = "WidescreenStoryboard"
    EpilepsyWarning = "EpilepsyWarning"
    SamplesMatchPlaybackRate = "SamplesMatchPlaybackRate"
    Countdown = "Countdown"
    CountdownOffset = "CountdownOffset"

    @classmethod
    def from_str(cls, key: str) -> GeneralKey | None:
        return cls.__members__.get(key)
