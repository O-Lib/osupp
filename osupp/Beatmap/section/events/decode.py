from dataclasses import dataclass, field
from typing import List

from beatmap import Beatmap
from utils import StrExtra

from .mod import BreakPeriod, EventType


class ParseEventsError(Exception):
    def __init__(self, message: str, source: Exception = None):
        self.source = source
        super().__init__(message)
        if source:
            self.__cause__ = source

    @classmethod
    def from_event_type(cls, err: Exception) -> "ParseEventsError":
        return cls("failed to parse event type", err)

    @classmethod
    def invalid_line(cls) -> "ParseEventsError":
        return cls("invalid line")

    @classmethod
    def from_number(cls, err: Exception) -> "ParseEventsError":
        return cls("failed to parse number", err)


@dataclass
class Events:
    background_file: str = ""
    breaks: list[BreakPeriod] = field(default_factory=list)

    @classmethod
    def default(cls) -> "Events":
        return cls()

    def into_beatmap(self, beatmap: "Beatmap") -> None:
        beatmap.background_file = self.background_file
        beatmap.breaks = self.breaks

    @classmethod
    def create(cls, version: int) -> "Events":
        return cls.default()

    def to_result(self) -> "Events":
        return self

    @staticmethod
    def clean_filename(s: str) -> str:
        return s.strip().strip('"')

    @classmethod
    def parse_general(cls, state: "EventsState", line: str) -> None:
        pass

    @classmethod
    def parse_editor(cls, state: "EventsState", line: str) -> None:
        pass

    @classmethod
    def parse_metadata(cls, state: "EventsState", line: str) -> None:
        pass

    @classmethod
    def parse_difficulty(cls, state: "EventsState", line: str) -> None:
        pass

    @classmethod
    def parse_events(cls, state: "EventsState", line: str) -> None:
        clean_line = StrExtra.trim_comment(line).strip()
        if not clean_line:
            return

        parts = clean_line.split(",")

        if len(parts) < 3:
            return

        raw_type, raw_start, raw_params = parts[0], parts[1], parts[2]

        try:
            event_type = EventType.from_str(raw_type)
        except Exception:
            return

        try:
            if event_type == EventType.Sprite:
                if not state.background_file and len(parts) > 3:
                    state.background_file = cls.clean_filename(parts[3])

            elif event_type == EventType.Video:
                video_extensions = {
                    ".mp4",
                    ".mov",
                    ".avi",
                    ".flv",
                    ".mpg",
                    ".wmv",
                    ".m4v",
                }
                filename = cls.clean_filename(raw_params)

                ext = filename[-4:].lower()
                if ext not in video_extensions:
                    state.background_file = filename

            elif event_type == EventType.Background:
                state.background_file = cls.clean_filename(raw_params)

            elif event_type == EventType.Break:
                try:
                    start_time = float(raw_start)
                    end_time = float(raw_params)

                    state.breaks.append(
                        BreakPeriod(
                            start_time=start_time, end_time=max(start_time, end_time)
                        )
                    )
                except ValueError:
                    raise ParseEventsError.from_number(
                        ValueError("Invalid break times")
                    )

            elif event_type in (EventType.Color, EventType.Sample, EventType.Animation):
                pass
        except ValueError as e:
            raise ParseEventsError.from_number(e)

    @classmethod
    def parse_timing_points(cls, state: "EventsState", line: str) -> None:
        pass

    @classmethod
    def parse_colors(cls, state: "EventsState", line: str) -> None:
        pass

    @classmethod
    def parse_hit_objects(cls, state: "EventsState", line: str) -> None:
        pass

    @classmethod
    def parse_variables(cls, state: "EventsState", line: str) -> None:
        pass

    @classmethod
    def parse_catch_the_beat(cls, state: "EventsState", line: str) -> None:
        pass

    @classmethod
    def parse_mania(cls, state: "EventsState", line: str) -> None:
        pass


EventsState = Events
