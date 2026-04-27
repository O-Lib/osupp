from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from utils import KeyValue, ParseNumberError, parse_float, trim_comment


class ParseDifficultyError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class DifficultyKey(Enum):
    HPDrainRate = "HPDrainRate"
    CircleSize = "CircleSize"
    OverallDifficulty = "OverallDifficulty"
    ApproachRate = "ApproachRate"
    SliderMultiplier = "SliderMultiplier"
    SliderTickRate = "SliderTickRate"

    @classmethod
    def from_str(cls, s: str) -> DifficultyKey:
        try:
            return cls(s)
        except ValueError:
            raise ValueError("invalid difficulty key")


@dataclass(slots=True)
class Difficulty:
    hp_drain_rate: float
    circle_size: float
    overall_difficulty: float
    approach_rate: float
    slider_multiplier: float
    slider_tick_rate: float

    def __init__(self):
        self.hp_drain_rate = 5.0
        self.circle_size = 5.0
        self.overall_difficulty = 5.0
        self.approach_rate = 5.0
        self.slider_multiplier = 1.4
        self.slider_tick_rate = 1.0


class DifficultyState:
    __slots__ = ("has_approach_rate", "difficulty")

    def __init__(self, format_version: int = 14):
        self.has_approach_rate: bool = False
        self.difficulty: Difficulty = Difficulty()

    def parse_difficulty(self, line: str) -> None:
        clean_line = trim_comment(line)

        kv = KeyValue.parse(clean_line, DifficultyKey.from_str)
        if kv is None:
            return

        try:
            match kv.key:
                case DifficultyKey.HPDrainRate:
                    self.difficulty.hp_drain_rate = parse_float(kv.value)
                case DifficultyKey.CircleSize:
                    self.difficulty.circle_size = parse_float(kv.value)
                case DifficultyKey.OverallDifficulty:
                    self.difficulty.overall_difficulty = parse_float(kv.value)

                    if not self.has_approach_rate:
                        self.difficulty.approach_rate = (
                            self.difficulty.overall_difficulty
                        )

                case DifficultyKey.ApproachRate:
                    self.difficulty.approach_rate = parse_float(kv.value)
                    self.has_approach_rate = True
                case DifficultyKey.SliderMultiplier:
                    val = parse_float(kv.value)
                    self.difficulty.slider_multiplier = max(0.4, min(3.6, val))
                case DifficultyKey.SliderTickRate:
                    val = parse_float(kv.value)
                    self.difficulty.slider_tick_rate = max(0.5, min(8.0, val))

        except ParseNumberError as e:
            raise ParseDifficultyError(f"failed to parse number: {e}")
