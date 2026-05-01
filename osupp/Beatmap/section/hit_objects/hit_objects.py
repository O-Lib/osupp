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

from section.enums import GameMode, HitSoundType, SampleBank, SplineType
from section.hit_objects.slider import PathControlPoint, PathType, SliderPath
from utils import ParseNumberError, Pos, parse_float, parse_int, trim_comment


class ParseHitObjectsError(Exception):
    """Raised when a hit object line cannot be parsed."""
    def __init__(self, message: str) -> None:
        """Initialise with an error message.

        Args:
            message: Description of the parse failure.
        """
        super().__init__(message)


MAX_COORDINATE_VALUE = 131072


class HitObjectType:
    """Bit flag constants for the type field of a hit object line."""
    CIRCLE = 1 << 0
    SLIDER = 1 << 1
    NEW_COMBO = 1 << 2
    SPINNER = 1 << 3
    COMBO_OFFSET = (1 << 4) | (1 << 5) | (1 << 6)
    HOLD = 1 << 7

    @staticmethod
    def has_flag(value: int, flag: int) -> bool:
        """Check whether ``flag`` is set in ``value``.

        Args:
            value: The raw type integer from the hit object line.
            flag: The flag constant to test.

        Returns:
            ``True`` if the flag bits are set.
        """
        return (value & flag) != 0


class HitSampleDefaultName(Enum):
    """Default hit sound sample filenames."""
    Normal = "hitnormal"
    Whistle = "hitwhistle"
    Finish = "hitfinish"
    Clap = "hitclap"


@dataclass(slots=True, eq=True)
class HitSampleInfo:
    """Describes a single hit sound sample associated with a hit object."""
    name_default: HitSampleDefaultName | None
    name_file: str | None
    bank: SampleBank
    suffix: int | None
    volume: int
    custom_sample_bank: int
    bank_specified: bool
    is_layered: bool


@dataclass(slots=True, eq=True)
class SampleBankInfo:
    """Accumulates hit sound bank information while parsing a hit object line."""
    filename: str | None = None
    bank_for_normal: SampleBank | None = None
    bank_for_addition: SampleBank | None = None
    volume: int = 0
    custom_sample_bank: int = 0

    def read_custom_sample_bank(self, parts: list[str], banks_only: bool) -> None:
        """Parse the hit sound bank fields from a colon-separated list.

        Args:
            parts: The colon-split fields from the hit sound section of a line.
            banks_only: If ``True``, only bank fields are read; volume and filename are ignored.
        """
        if not parts or not parts[0]:
            return

        try:
            bank_val = parse_int(parts[0])
        except ParseNumberError:
            bank_val = 0
        bank = SampleBank(bank_val) if bank_val in (1, 2, 3) else SampleBank.Normal

        try:
            add_bank_val = parse_int(parts[1]) if len(parts) > 1 else 0
        except ParseNumberError:
            add_bank_val = 0
        add_bank = (
            SampleBank(add_bank_val) if add_bank_val in (1, 2, 3) else SampleBank.Normal
        )

        self.bank_for_normal = bank if bank != SampleBank.None_ else None
        self.bank_for_addition = (
            add_bank if add_bank != SampleBank.None_ else self.bank_for_normal
        )

        if banks_only:
            return

        if len(parts) > 2 and parts[2]:
            self.custom_sample_bank = parse_int(parts[2])
        if len(parts) > 3 and parts[3]:
            self.volume = max(0, parse_int(parts[3]))
        if len(parts) > 4 and parts[4]:
            self.filename = parts[4]

    def convert_sound_type(self, sound_type: HitSoundType) -> list[HitSampleInfo]:
        """Convert a HitSoundType bitmask to a list of HitSampleInfo objects.

        Args:
            sound_type: The hit sound flags active on the hit object.

        Returns:
            A list of HitSampleInfo objects representing all active hit sounds.
        """
        samples = []
        if self.filename:
            samples.append(
                HitSampleInfo(
                    None,
                    self.filename,
                    SampleBank.Normal,
                    1,
                    self.volume,
                    self.custom_sample_bank,
                    False,
                    False,
                )
            )
        else:
            is_layered = (
                sound_type != HitSoundType.NONE
            ) and not HitSoundType.has_flag(sound_type, HitSoundType.NORMAL)
            samples.append(
                HitSampleInfo(
                    HitSampleDefaultName.Normal,
                    None,
                    self.bank_for_normal or SampleBank.Normal,
                    self.custom_sample_bank if self.custom_sample_bank >= 2 else None,
                    self.volume,
                    self.custom_sample_bank,
                    self.bank_for_normal is not None,
                    is_layered,
                )
            )

        if HitSoundType.has_flag(sound_type, HitSoundType.FINISH):
            samples.append(
                HitSampleInfo(
                    HitSampleDefaultName.Finish,
                    None,
                    self.bank_for_addition or SampleBank.Normal,
                    self.custom_sample_bank if self.custom_sample_bank >= 2 else None,
                    self.volume,
                    self.custom_sample_bank,
                    self.bank_for_addition is not None,
                    False,
                )
            )
        if HitSoundType.has_flag(sound_type, HitSoundType.WHISTLE):
            samples.append(
                HitSampleInfo(
                    HitSampleDefaultName.Whistle,
                    None,
                    self.bank_for_addition or SampleBank.Normal,
                    self.custom_sample_bank if self.custom_sample_bank >= 2 else None,
                    self.volume,
                    self.custom_sample_bank,
                    self.bank_for_addition is not None,
                    False,
                )
            )
        if HitSoundType.has_flag(sound_type, HitSoundType.CLAP):
            samples.append(
                HitSampleInfo(
                    HitSampleDefaultName.Clap,
                    None,
                    self.bank_for_addition or SampleBank.Normal,
                    self.custom_sample_bank if self.custom_sample_bank >= 2 else None,
                    self.volume,
                    self.custom_sample_bank,
                    self.bank_for_addition is not None,
                    False,
                )
            )

        return samples


@dataclass(slots=True, eq=True)
class HitObjectCircle:
    """A circle hit object."""
    pos: Pos
    new_combo: bool
    combo_offset: int


@dataclass(slots=True, eq=True)
class HitObjectSpinner:
    """A spinner hit object."""
    pos: Pos
    duration: float
    new_combo: bool


@dataclass(slots=True, eq=True)
class HitObjectHold:
    """An osu!mania hold note."""
    pos_x: float
    duration: float


@dataclass(slots=True, eq=True)
class HitObjectSlider:
    """A slider hit object."""
    pos: Pos
    new_combo: bool
    combo_offset: int
    path: SliderPath
    node_samples: list[list[HitSampleInfo]]
    repeat_count: int
    velocity: float


@dataclass(slots=True, eq=True)
class HitObject:
    """A single parsed hit object."""
    start_time: float
    kind: HitObjectCircle | HitObjectSpinner | HitObjectHold | HitObjectSlider
    samples: list[HitSampleInfo]


def is_linear(p0: Pos, p1: Pos, p2: Pos) -> bool:
    """Test whether three points are collinear.

    Uses the cross-product area test with a small epsilon tolerance.

    Args:
        p0: First point.
        p1: Second point.
        p2: Third point.

    Returns:
        ``True`` if the points lie on a single line within floating-point tolerance.
    """
    return abs((p1.y - p0.y) * (p2.x - p0.x) - (p1.x - p0.x) * (p2.y - p0.y)) < 1e-7


def convert_points(
    curve_points: list[PathControlPoint],
    points: list[str],
    end_points: str | None,
    first: bool,
    offset: Pos,
) -> None:
    """Parse a segment of slider path tokens into PathControlPoint objects.

    Args:
        curve_points: Output list to append parsed control points to.
        points: Pipe-split tokens for this path segment (first token is the type char).
        end_points: An optional extra endpoint token for this segment.
        first: Whether this is the first segment in the path string.
        offset: The slider start position used to make coordinates relative.
    """
    path_type = PathType.new_from_str(points[0])

    def read_point(val: str) -> Pos:
        v = val.split(":")
        if len(v) < 2:
            raise ParseHitObjectsError("invalid point format")
        x = float(parse_int(v[0]))
        y = float(parse_int(v[1]))
        return Pos(x, y) - offset

    vertices: list[PathControlPoint] = []
    if first:
        vertices.append(PathControlPoint(Pos(0.0, 0.0), None))

    for point in points[1:]:
        vertices.append(PathControlPoint(read_point(point), None))

    if end_points:
        vertices.append(PathControlPoint(read_point(end_points), None))

    end_point_len = 1 if end_points else 0

    if path_type.kind == SplineType.PerfectCurve:
        if len(vertices) == 3:
            if is_linear(vertices[0].pos, vertices[1].pos, vertices[2].pos):
                path_type = PathType(SplineType.Linear)
        else:
            path_type = PathType(SplineType.BSpline)

    vertices[0].path_type = path_type

    start_idx = 0
    end_idx = 0

    while True:
        end_idx += 1
        if end_idx >= len(vertices) - end_point_len:
            break

        if vertices[end_idx].pos != vertices[end_idx - 1].pos:
            continue

        if path_type.kind == SplineType.Catmull and end_idx > 1:
            continue

        if end_idx == len(vertices) - end_point_len - 1:
            continue

        vertices[end_idx - 1].path_type = path_type
        curve_points.extend(vertices[start_idx:end_idx])
        start_idx = end_idx + 1

    if end_idx > start_idx:
        curve_points.extend(vertices[start_idx:end_idx])


def convert_path_str(point_str: str, offset: Pos) -> list[PathControlPoint]:
    """Parse the full slider path string into a list of control points.

    Args:
        point_str: The raw path string from the hit object line (pipe-separated).
        offset: The slider start position used to make coordinates relative.

    Returns:
        A list of PathControlPoint objects.
    """
    point_split = point_str.split("|")
    curve_points: list[PathControlPoint] = []

    start_idx = 0
    end_idx = 0
    first = True

    while end_idx < len(point_split):
        end_idx += 1
        if end_idx < len(point_split):
            if point_split[end_idx] and point_split[end_idx][0].isalpha():
                end_points = (
                    point_split[end_idx + 1] if end_idx + 1 < len(point_split) else None
                )
                convert_points(
                    curve_points,
                    point_split[start_idx:end_idx],
                    end_points,
                    first,
                    offset,
                )
                start_idx = end_idx
                first = False

    if end_idx > start_idx:
        convert_points(
            curve_points, point_split[start_idx:end_idx], None, first, offset
        )

    return curve_points


class HitObjectsState:
    """Accumulates parsed hit objects during beatmap decoding."""
    def __init__(self) -> None:
        """Initialise with an empty hit object list and no last object type."""
        self.last_object_type: int | None = None
        self.hit_objects: list[HitObject] = []

    def last_object_was_spinner(self) -> bool:
        """Return ``True`` if the most recently parsed object was a spinner."""
        return self.last_object_type is not None and HitObjectType.has_flag(
            self.last_object_type, HitObjectType.SPINNER
        )

    def parse_hit_object(self, line: str) -> None:
        """Parse a single hit object line and append it to hit_objects.

        Args:
            line: A raw comma-separated hit object line.

        Raises:
            ParseHitObjectsError: If the line has fewer than 5 fields, the type
                is unknown, or a numeric value cannot be parsed.
        """
        clean_line = trim_comment(line)
        split = clean_line.split(",")
        if len(split) < 5:
            raise ParseHitObjectsError("invalid line")

        try:
            x = float(parse_int(split[0]))
            y = float(parse_int(split[1]))
            pos = Pos(x, y)
            start_time = parse_float(split[2])

            type_flag = parse_int(split[3])
            combo_offset = (type_flag & HitObjectType.COMBO_OFFSET) >> 4
            new_combo = HitObjectType.has_flag(type_flag, HitObjectType.NEW_COMBO)

            sound_type = HitSoundType(parse_int(split[4]))
            bank_info = SampleBankInfo()

            is_first_obj = self.last_object_type is None
            force_new_combo = (
                is_first_obj or self.last_object_was_spinner() or new_combo
            )

            kind: HitObjectCircle | HitObjectSpinner | HitObjectHold | HitObjectSlider

            if HitObjectType.has_flag(type_flag, HitObjectType.CIRCLE):
                if len(split) > 5:
                    bank_info.read_custom_sample_bank(split[5].split(":"), False)

                circle = HitObjectCircle(
                    pos, force_new_combo, combo_offset if new_combo else 0
                )
                kind = circle

            elif HitObjectType.has_flag(type_flag, HitObjectType.SPINNER):
                end_time = parse_float(split[5]) if len(split) > 5 else start_time
                duration = max(0.0, end_time - start_time)

                if len(split) > 6:
                    bank_info.read_custom_sample_bank(split[6].split(":"), False)

                spinner = HitObjectSpinner(Pos(256.0, 192.0), duration, new_combo)
                kind = spinner

            elif HitObjectType.has_flag(type_flag, HitObjectType.HOLD):
                end_time_raw = start_time
                if len(split) > 5 and split[5]:
                    ss = split[5].split(":")
                    end_time_raw = parse_float(ss[0])
                    bank_info.read_custom_sample_bank(ss[1:], False)

                hold = HitObjectHold(pos.x, max(start_time, end_time_raw) - start_time)
                kind = hold

            elif HitObjectType.has_flag(type_flag, HitObjectType.SLIDER):
                if len(split) < 7:
                    raise ParseHitObjectsError("Invalid Line for Slider")

                point_str = split[5]
                repeat_count = max(0, parse_int(split[6]) - 1)
                expected_dist = parse_float(split[7]) if len(split) > 7 else None

                control_points = convert_path_str(point_str, pos)

                slider = HitObjectSlider(
                    pos,
                    force_new_combo,
                    combo_offset if new_combo else 0,
                    SliderPath(GameMode.Osu, control_points, expected_dist),
                    [],
                    repeat_count,
                    1.0,
                )
                kind = slider

            else:
                raise ParseHitObjectsError(f"Unknown Hit Object Type: {type_flag}")

            obj = HitObject(start_time, kind, bank_info.convert_sound_type(sound_type))
            self.hit_objects.append(obj)
            self.last_object_type = type_flag

        except Exception as e:
            raise ParseHitObjectsError(f"Failed to parse HitObject: {e}")
