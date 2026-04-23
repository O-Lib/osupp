from dataclasses import dataclass, field

from beatmap import Beatmap
from utils import KeyValue, ParseNumberError, StrExtra
from utils.parse_number import InvalidInteger

from .mod import Color, CustomColor


class ParseColorsError(Exception):
    def __init__(self, message: str, source: Exception | None = None):
        super().__init__(message)
        self.__cause__ = source

    @classmethod
    def incorrect_color(cls) -> "ParseColorsError":
        return cls("color specified in incorret format (should be R,G,B or R,G,B,A")

    @classmethod
    def number(cls, source: Exception) -> "ParseColorsError":
        return cls("failed to parse number", source)


@dataclass
class Colors:
    DEFAULT_COMBO_COLORS: list[Color] = field(
        default_factory=lambda: [
            Color.new(255, 192, 0, 255),
            Color.new(0, 202, 0, 255),
            Color.new(18, 124, 255, 255),
            Color.new(242, 24, 57, 255),
        ]
    )

    custom_combo_colors: list[Color] = field(default_factory=list)
    custom_colors: list[CustomColor] = field(default_factory=list)

    @classmethod
    def default(cls) -> "Colors":
        return cls()

    def to_beatmap(self, beatmap: "Beatmap") -> None:
        beatmap.custom_combo_colors = self.custom_combo_colors
        beatmap.custom_colors = self.custom_colors

    @staticmethod
    def parse_general(state: "ColorsState", line: str):
        pass

    @staticmethod
    def parse_editor(state: "ColorsState", line: str):
        pass

    @staticmethod
    def parse_metadata(state: "ColorsState", line: str):
        pass

    @staticmethod
    def parse_difficulty(state: "ColorsState", line: str):
        pass

    @staticmethod
    def parse_events(state: "ColorsState", line: str):
        pass

    @staticmethod
    def parse_timing_points(state: "ColorsState", line: str):
        pass

    @staticmethod
    def parse_colors(state: "ColorsState", line: str):
        trimmed = StrExtra.trim_comment(line)
        if not trimmed or ":" not in trimmed:
            return

        kv = KeyValue.parse(trimmed, str)
        if not kv:
            return

        try:
            color = Color.parse(kv.value)
            key = ColorsKey.parse(kv.key)

            if key.is_combo:
                state.custom_combo_colors.append(color)
            else:
                name = key.name

                existing = next(
                    (c for c in state.custom_colors if c.name == name), None
                )
                if existing:
                    existing.color = color
                else:
                    state.custom_colors.append(CustomColor(name=name, color=color))
        except Exception as e:
            raise ParseColorsError.incorrect_color() from e

    @staticmethod
    def parse_hit_objects(state: "ColorsState", line: str):
        pass

    @staticmethod
    def parse_variables(state: "ColorsState", line: str):
        pass

    @staticmethod
    def parse_catch_the_beat(state: "ColorsState", line: str):
        pass

    @staticmethod
    def parse_mania(state: "ColorsState", line: str):
        pass


ColorsState = Colors


class ColorsKey:
    def __init__(self, is_combo: bool, name: str | None = None):
        self.is_combo = is_combo
        self.name = name

    @classmethod
    def parse(cls, s: str) -> "ColorsKey":
        if s.startswith("Combo"):
            return cls(is_combo=True)
        else:
            return cls(is_combo=False, name=s)


def handle_int_error(err: ValueError) -> ParseColorsError:
    num_err = ParseNumberError(InvalidInteger, err)
    return ParseColorsError.number(num_err)


def create(version: int) -> ColorsState:
    return Colors.default()
