from dataclasses import dataclass
from typing import Optional
from enum import Enum

from utils import KeyValue, ParseNumber, ParseNumberError, StrExtra
from beatmap import Beatmap

@dataclass
class Difficulty:
    hp_drain_rate: float = 5.0
    circle_size: float = 5.0
    overall_difficulty: float = 5.0
    approach_rate: float = 5.0
    slider_multiplier: float = 1.4
    slider_tick_rate: float = 1.0

    @classmethod
    def default(cls) -> "Difficulty":
        return cls()

    def into_beatmap(self) -> "Beatmap":
        return Beatmap(
            hp_drain_rate=self.hp_drain_rate,
            circle_size=self.circle_size,
            overall_difficulty=self.overall_difficulty,
            approach_rate=self.approach_rate,
            slider_multiplier=self.slider_multiplier,
            slider_tick_rate=self.slider_tick_rate
        )

    @classmethod
    def parse_general(cls, state: "DifficultyState", line: str) -> None:
        pass

    @classmethod
    def parse_editor(cls, state: "DifficultyState", line: str) -> None:
        pass

    @classmethod
    def parse_metadata(cls, state: "DifficultyState", line: str) -> None:
        pass

    @classmethod
    def parse_difficulty(cls, state: "DifficultyState", line: str) -> None:
        clean_line = line.split('//')[0].strip()

        kv = KeyValue.parse(clean_line, str)
        if kv is None:
            return

        key_enum = DifficultyKey.from_str(kv.key)
        if key_enum is None:
            return

        value = kv.value

        try:
            if key_enum == DifficultyKey.HPDrainRate:
                state.difficulty.hp_drain_rate = ParseNumber.parse(value)

            elif key_enum == DifficultyKey.CircleSize:
                state.difficulty.circle_size = ParseNumber.parse(value)

            elif key_enum == DifficultyKey.OverallDifficulty:
                od = ParseNumber.parse(value)
                state.difficulty.overall_difficulty = od
                if not state.has_approach_rate:
                    state.difficulty.approach_rate = od

            elif key_enum == DifficultyKey.ApproachRate:
                state.difficulty.approach_rate = ParseNumber.parse(value)
                state.has_approach_rate = True

            elif key_enum == DifficultyKey.SliderMultiplier:
                val = ParseNumber.parse(value)
                state.difficulty.slider_multiplier = max(0.4, min(3.6, val))

            elif key_enum == DifficultyKey.SliderTickRate:
                val = ParseNumber.parse(value)
                state.difficulty.slider_tick_rate = max(0.5, min(8.0, val))

        except ValueError as e:
            raise ParseDifficultyError.from_number(e)

    @classmethod
    def parse_events(cls, state: "DifficultyState", line: str) -> None:
        pass

    @classmethod
    def parse_timing_points(cls, state: "DifficultyState", line: str) -> None:
        pass

    @classmethod
    def parse_colors(cls, state: "DifficultyState", line: str) -> None:
        pass

    @classmethod
    def parse_hit_objects(cls, state: "DifficultyState", line: str) -> None:
        pass

    @classmethod
    def parse_variables(cls, state: "DifficultyState", line: str) -> None:
        pass

    @classmethod
    def parse_catch_the_beat(cls, state: "DifficultyState", line: str) -> None:
        pass

    @classmethod
    def parse_mania(cls, state: "DifficultyState", line: str) -> None:
        pass

class DifficultyKey(Enum):
    HPDrainRate = "HPDrainRate"
    CircleSize = "CircleSize"
    OverallDifficulty = "OverallDifficulty"
    ApproachRate = "ApproachRate"
    SliderMultiplier = "SliderMultiplier"
    SliderTickRate = "SliderTickRate"

    @classmethod
    def from_str(cls, key: str) -> Optional["DifficultyKey"]:
        return cls.__members__.get(key)

class ParseDifficultyError(Exception):
    def __init__(self, kind: str, source: Exception):
        self.kind = kind
        self.source = source
        super().__init__(self.get_message())
        self.__cause__ = source

    def get_message(self) -> str:
        if self.kind == "Number":
            return "failed to parse number"
        return "failed to parse difficulty"

    @classmethod
    def from_number(cls, err: Exception) -> "ParseDifficultyError":
        return cls("Number", err)

@dataclass
class DifficultyState:
    difficulty: Difficulty
    has_approach_rate: bool

    @classmethod
    def create(cls, _version: int) -> "DifficultyState":
        return cls(
            difficulty=Difficulty.default(),
            has_approach_rate=False
        )

    def to_result(self) -> Difficulty:
        return self.difficulty