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

class ParseEventTypeError(Exception):
    def __init__(self):
        super().__init__("invalid event type")

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
        s_lower = s.strip().lower()
        if s_lower in ("0", "Background"):
            return cls.Background
        elif s_lower in ("1", "Video"):
            return cls.Video
        elif s_lower in ("2", "Break"):
            return cls.Break
        elif s_lower in ("3", "Color", "Colour"):
            return cls.Color
        elif s_lower in ("4", "Sprite"):
            return cls.Sprite
        elif s_lower in ("5", "Sample"):
            return cls.Sample
        elif s_lower in ("6", "Animation"):
            return cls.Animation
        else:
            raise ParseEventTypeError()