from dataclasses import dataclass
from enum import IntEnum

@dataclass(frozen=True)
class BreakPeriod:
    start_time: float = 0.0
    end_time: float = 0.0

    MIN_BREAK_DURATION: float = 650.0

    def duration(self) -> float:
        return self.end_time - self.start_time

    def has_effect(self) -> bool:
        return self.duration() >= self.MIN_BREAK_DURATION


class EventType(IntEnum):
    Background = 0
    Video = 1
    Break = 2
    Color = 3
    Sprite = 4
    Sample = 5
    Animation = 6

    @classmethod
    def from_str(cls, s: str) -> "EventType":
        if s == "0" or s == "Background":
            return cls.Background
        elif s == "1" or s == "Video":
            return cls.Video
        elif s == "2" or s == "Break":
            return cls.Break
        elif s == "3" or s == "Color" or s == "Colour":
            return cls.Color
        elif s == "4" or s == "Sprite":
            return cls.Sprite
        elif s == "5" or s == "Sample":
            return cls.Sample
        elif s == "6" or s == "Animation":
            return cls.Animation
        else:
            raise ParseEventTypeError()


class ParseEventTypeError(Exception):
    def __init__(self):
        super().__init__("invalid event type")