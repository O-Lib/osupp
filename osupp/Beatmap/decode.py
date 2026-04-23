import io
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generic, Optional, Tuple, Type, TypeVar, Union

import format_version
from reader import Decoder
from section import Section

D = TypeVar("D", bound="DecodeBeatmap")
S = TypeVar("S", bound="DecodeState")


def from_path(target_class: type[D], path: str | Path) -> D:
    with open(path, "rb") as f:
        reader = io.BufferedReader(f)
        return target_class.decode(reader)


def from_bytes(target_class: type[D], bytes_data: bytes) -> D:
    return target_class.decode(io.BytesIO(bytes_data))


def from_str(target_class: type[D], s: str) -> D:
    return target_class.decode(io.BytesIO(s.encode("utf-8")))


class DecodeState(ABC):
    @classmethod
    @abstractmethod
    def create(cls, version: int) -> "DecodeState":
        pass

    @abstractmethod
    def to_result(self) -> Any:
        pass


class DecodeBeatmap(ABC, Generic[S]):
    Error = Exception
    State = type[S]

    @classmethod
    def decode(cls, src: io.BufferedIOBase) -> Any:
        reader = Decoder.new(src)
        version, use_curr_line = parse_version(reader)

        actual_version = (
            version if version is not None else format_version.LATEST_FORMAT_VERSION
        )
        state = cls.State.create(actual_version)

        section = parse_first_section(reader, use_curr_line)
        if section is None:
            return state.to_result()

        while True:
            parse_map = {
                Section.General: cls.parse_general,
                Section.Editor: cls.parse_editor,
                Section.Metadata: cls.parse_metadata,
                Section.Difficulty: cls.parse_difficulty,
                Section.Events: cls.parse_events,
                Section.TimingPoints: cls.parse_timing_points,
                Section.Colors: cls.parse_colors,
                Section.HitObjects: cls.parse_hit_objects,
                Section.Variables: cls.parse_variables,
                Section.CatchTheBeat: cls.parse_catch_the_beat,
                Section.Mania: cls.parse_mania,
            }
            parse_fn = parse_map.get(section)

            try:
                flow = parse_section(cls, reader, state, parse_fn)

                if flow.section is not None:
                    section = flow.section

                elif flow.break_loop:
                    break

            except OSError as err:
                raise err

        return state.to_result()

    @staticmethod
    def should_skip_line(line: str) -> bool:
        return not line or line.lstrip().startswith("//")

    @classmethod
    @abstractmethod
    def parse_general(cls, state: State, line: str):
        pass

    @classmethod
    @abstractmethod
    def parse_editor(cls, state: State, line: str):
        pass

    @classmethod
    @abstractmethod
    def parse_metadata(cls, state: State, line: str):
        pass

    @classmethod
    @abstractmethod
    def parse_difficulty(cls, state: State, line: str):
        pass

    @classmethod
    @abstractmethod
    def parse_events(cls, state: State, line: str):
        pass

    @classmethod
    @abstractmethod
    def parse_timing_points(cls, state: State, line: str):
        pass

    @classmethod
    @abstractmethod
    def parse_colors(cls, state: State, line: str):
        pass

    @classmethod
    @abstractmethod
    def parse_hit_objects(cls, state: State, line: str):
        pass

    @classmethod
    @abstractmethod
    def parse_variables(cls, state: State, line: str):
        pass

    @classmethod
    @abstractmethod
    def parse_catch_the_beat(cls, state: State, line: str):
        pass

    @classmethod
    @abstractmethod
    def parse_mania(cls, state: State, line: str):
        pass


@dataclass
class UseCurrentLine:
    value: bool

    def __bool__(self):
        return self.value


def parse_version(reader: "Decoder") -> tuple[int | None, UseCurrentLine]:
    while True:
        line = reader.read_line()

        if line is None:
            return None, UseCurrentLine(False)

        res = format_version.try_version_from_line(line)

        if res is None:
            continue

        if isinstance(res, int):
            return res, UseCurrentLine(False)

        logger.error(f"Failed to parse format version: {res}")
        return None, UseCurrentLine(True)


def parse_first_section(
    reader: "Decoder", use_curr_line: UseCurrentLine
) -> Section | None:
    current_line_section = Section.try_from_line(reader.curr_line())
    if current_line_section is not None:
        return current_line_section

    while True:
        line = reader.read_line()
        if line is not None:
            section = Section.try_from_line(line)
            if section is not None:
                return section

            continue

        return None


class SectionFlow:
    def __init__(self, section: Section | None = None, break_loop: bool = False):
        self.section = section
        self.break_loop = break_loop


def parse_section(
    reader: Decoder, state: S, f: Any, cls: type[DecodeBeatmap]
) -> SectionFlow:
    while True:
        try:
            line = reader.read_line()
        except OSError as err:
            raise err

        if line is not None:
            if cls.should_skip_line(line):
                continue

            next_section = Section.try_from_line(line)
            if next_section is not None:
                return SectionFlow(section=next_section)

            try:
                f(cls, state, line)
            except Exception as err:
                logging.getLogger("osupp_beatmap").error(
                    f"Failed to process line {line!r}: {err}"
                )
                log_error_cause(err)

            continue

        return SectionFlow(break_loop=True)


def log_error_cause(err: Exception):
    current_err = err.__cause__ if err.__cause__ is not None else err.__context__

    while current_err is not None:
        logger.error(f" - caused by: {current_err}")
        current_err = (
            current_err.__cause__
            if current_err.__cause__ is not None
            else current_err.__context__
        )
