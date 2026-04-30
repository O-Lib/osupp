from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from utils import ParseNumberError, clean_filename, parse_float, trim_comment


class ParseEventsError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class EventType(Enum):
    Background = 0
    Video = 1
    Break = 2
    Color = 3
    Sprite = 4
    Sample = 5
    Animation = 6

    @classmethod
    def from_str(cls, s: str) -> EventType:
        match s:
            case "0" | "Background":
                return cls.Background
            case "1" | "Video":
                return cls.Video
            case "2" | "Break":
                return cls.Break
            case "3" | "Colour":
                return cls.Color
            case "4" | "Sprite":
                return cls.Sprite
            case "5" | "Sample":
                return cls.Sample
            case "6" | "Animation":
                return cls.Animation
            case _:
                raise ParseEventsError("invalid event type")


@dataclass(slots=True, eq=True)
class BreakPeriod:
    start_time: float
    end_time: float

    def duration(self) -> float:
        return self.end_time - self.start_time

    def has_effect(self) -> bool:
        return self.duration() >= 650.0


VIDEO_EXTENSIONS = {"mp4", "mov", "avi", "flv", "mpg", "wmv", "m4v"}


@dataclass(slots=True, eq=True)
class Events:
    background_file: str
    breaks: list[BreakPeriod]

    def __init__(self):
        self.background_file = ""
        self.breaks = []

    def parse_events(self, line: str) -> None:
        clean_file = trim_comment(line)

        parts = clean_file.split(",")

        if len(parts) < 3:
            raise ParseEventsError("invalid line")

        event_type_str = parts[0]
        start_time_str = parts[1]
        event_params = parts[2]

        event_type = EventType.from_str(event_type_str)

        try:
            match event_type:
                case EventType.Sprite:
                    if not self.background_file:
                        if len(parts) > 3:
                            self.background_file = clean_filename(parts[3])
                        else:
                            raise ParseEventsError("invalid line")

                case EventType.Video:
                    filename = clean_filename(event_params)
                    if len(filename) >= 3:
                        ext = filename[-3:].lower()
                        if ext not in VIDEO_EXTENSIONS:
                            self.background_file = filename
                    else:
                        self.background_file = filename

                case EventType.Background:
                    self.background_file = clean_filename(event_params)

                case EventType.Break:
                    start_time = parse_float(start_time_str)
                    end_time_raw = parse_float(event_params)

                    end_time = max(start_time, end_time_raw)
                    self.breaks.append(
                        BreakPeriod(start_time=start_time, end_time=end_time)
                    )

                case EventType.Color | EventType.Sample | EventType.Animation:
                    pass

        except ParseNumberError as e:
            raise ParseEventsError(f"failed to parse number: {e}")


EventsState = Events
