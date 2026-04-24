import io
import math
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from section.general import GameMode
    from section.hit_objects import (
        BASE_SCORING_DIST,
        CurveBuffers,
        HitObjectKind,
        HitObjectSlider,
        HitSoundType,
        PathType,
        SplineType,
    )
    from section.hit_objects.hit_samples import HitSampleInfo
    from section.hit_objects.slider import (
        SliderEvent,
        SliderEventsIter,
        SliderEventType,
    )
    from section.timing_points.control_points.timing import TimingPoint
    from section.timing_points.decode import ControlPoints
    from utils.pos import Pos

    from .beatmap import Beatmap

from section.timing_points.control_points.difficulty import DifficultyPoint
from section.timing_points.control_points.effect import EffectPoint
from section.timing_points.control_points.sample import SamplePoint
from section.timing_points.control_points.timing import TimingPoint
from section.timing_points.effect_flags import EffectFlags


@dataclass
class ControlPointProperties:
    slider_velocity: float
    timing_signature: int
    sample_bank: int
    custom_sample_bank: int
    sample_volume: int
    effect_flags: int
    time: float

    @classmethod
    def default(cls) -> "ControlPointProperties":
        return cls(
            slider_velocity=0.0,
            timing_signature=0,
            sample_bank=0,
            custom_sample_bank=0,
            sample_volume=0,
            effect_flags=0,
            time=0.0,
        )

    @classmethod
    def new(
        cls,
        time: float,
        control_points: "ControlPoints",
        last_props: "ControlPointProperties",
        update_sample_bank: bool,
    ) -> "ControlPointProperties":
        timing = control_points.timing_point_at(time)
        difficulty = control_points.difficulty_point_at(time)

        sample_point = control_points.sample_point_at(time)
        sample = sample_point if sample_point is not None else SamplePoint.default()

        effect = control_points.effect_point_at(time)

        tmp_hit_sample = HitSampleInfo.new("normal", None, 0, 0)
        sample.apply(tmp_hit_sample)

        effect_flags = EffectFlags.NONE

        kiai = effect.kiai if effect is not None else EffectPoint.DEFAULT_KIAI
        if kiai:
            effect_flags |= EffectFlags.KIAI

        omit_first_bar_line = (
            timing.omit_first_bar_line
            if timing is not None
            else TimingPoint.DEFAULT_OMIT_FIRST_BAR_LINE
        )
        if omit_first_bar_line:
            effect_flags |= EffectFlags.OMIT_FIRST_BAR_LINE

        slider_velocity = (
            difficulty.slider_velocity
            if difficulty is not None
            else DifficultyPoint.DEFAULT_SLIDER_VELOCITY
        )

        if timing is not None:
            timing_signature = timing.time_signature.numerator
        else:
            timing_signature = TimingPoint.default().time_signature.numerator

        sample_bank = (
            int(tmp_hit_sample) if update_sample_bank else last_props.sample_bank
        )
        custom_sample_bank = (
            tmp_hit_sample.custom_sample_bank
            if tmp_hit_sample.custom_sample_bank >= 0
            else last_props.custom_sample_bank
        )

        return cls(
            slider_velocity=slider_velocity,
            timing_signature=timing_signature,
            sample_bank=sample_bank,
            custom_sample_bank=custom_sample_bank,
            sample_volume=tmp_hit_sample,
            effect_flags=effect_flags,
            time=time,
        )

    def is_redundant(self, other: "ControlPointProperties") -> bool:
        return (
            abs(self.slider_velocity - other.slider_velocity) < sys.float_info.epsilon
            and self.timing_signature == other.timing_signature
            and self.sample_bank == other.sample_bank
            and self.custom_sample_bank == other.custom_sample_bank
            and self.sample_volume == other.sample_volume
            and self.effect_flags == other.effect_flags
        )


@dataclass
class ControlPointGroup:
    time: float
    timing: Optional["TimingPoint"] = None

    @classmethod
    def new(cls, time: float) -> "ControlPointGroup":
        return cls(time=time, timing=None)

    @classmethod
    def from_timing(cls, point: "TimingPoint") -> "ControlPointGroup":
        return cls(time=point.time, timing=point)


def add_path_data(
    writer: io.StringIO,
    slider: "HitObjectSlider",
    pos: "Pos",
    mode: "GameMode",
    bufs: "CurveBuffers",
) -> None:
    last_type: Optional["PathType"] = None
    control_points = slider.path.control_points
    num_points = len(control_points)

    def get_separator(index: int) -> str:
        return "," if index == num_points - 1 else "|"

    for i in range(num_points):
        point = control_points[i]

        if point.path_type is not None:
            path_type = point.path_type

            needs_explicit_segment = (
                path_type != last_type or path_type.kind == SplineType.PerfectCurve
            )

            if i > 1:
                p1 = pos + control_points[i - 1].pos
                p2 = pos + control_points[i - 2].pos

                if int(p1.x) == int(p2.x) and int(p1.y) == int(p2.y):
                    needs_explicit_segment = True

                if needs_explicit_segment:
                    kind = path_type.kind
                    if kind == SplineType.BSpline:
                        if path_type.degree is not None:
                            writer.write(f"B{path_type.degree}")
                        else:
                            writer.write("B")

                    elif kind == SplineType.Catmull:
                        writer.write("C")
                    elif kind == SplineType.PerfectCurve:
                        writer.write("P")
                    elif kind == SplineType.Linear:
                        writer.write("L")

                    writer.write(get_separator(i))
                    last_type = path_type
                else:
                    x_val = pos.x + point.pos.x
                    y_val = pos.y + point.pos.y
                    writer.write(f"{x_val}:{y_val}")

        if i != 0:
            x_val = pos.x + point.pos.x
            y_val = pos.y + point.pos.y
            writer.write(f"{x_val}:{y_val}{get_separator(i)}")

    dist = slider.path.expected_dist
    if dist is None:
        dist = slider.path.get_curve_with_bufs(bufs).dist()

    span_count = slider.span_count()
    writer.write(f"{span_count},{dist},")

    for i in range(span_count + 1):
        if i < len(slider.node_samples):
            sound_type = int(HitSoundType.from_samples(slider.node_samples[i]))
        else:
            sound_type = 0

        suffix = "," if i == span_count else "|"
        writer.write(f"{sound_type}{suffix}")

    for i in range(span_count + 1):
        if i < len(slider.node_samples):
            get_sample_bank(writer, slider.node_samples[i], True, mode)
        else:
            writer.write("0:0")

        suffix = "," if i == span_count else "|"
        writer.write(suffix)


def get_sample_bank(
    writer: io.StringIO,
    samples: list["HitSampleInfo"],
    banks_only: bool,
    mode: "GameMode",
) -> None:
    normal_bank_val = 0
    for sample in samples:
        if sample.name == HitSampleInfo.HIT_NORMAL:
            normal_bank_val = int(sample.bank)
            break

    add_bank_val = 0
    for sample in samples:
        is_file = isinstance(sample.name, str)
        if sample.name != HitSampleInfo.HIT_NORMAL and not is_file:
            add_bank_val = int(sample.bank)
            break

    writer.write(f"{normal_bank_val}:{add_bank_val}")

    if banks_only:
        return

    custom_sample_bank = 0
    for sample in samples:
        if not isinstance(sample.name, str) and sample.name != HitSampleInfo.HIT_NORMAL:
            custom_sample_bank = sample.custom_sample_bank
            break

    sample_filename = None
    for sample in samples:
        if isinstance(sample.name, str) and len(sample.name) > 0:
            sample_filename = sample.lookup_name()
            break

    volume = samples[0].volume if len(samples) > 0 else 100

    if mode.value != 3:
        custom_sample_bank = 0
        volume = 0

    writer.write(f":{custom_sample_bank}:{volume}:")

    if sample_filename is not None:
        writer.write(sample_filename)


def collect_samples(map_obj: "Beatmap", control_points: "ControlPoints") -> None:
    ticks: list[float] = []
    curve_bufs = CurveBuffers()
    collected_samples: list["ControlPointProperties"] = []

    for h in map_obj.hit_objects:
        end_time = h.end_time_with_bufs(curve_bufs)
        collect_sample(collected_samples, h.samples, end_time)

        kind = h.kind
        if isinstance(kind.inner, (HitObjectKind.Circle, HitObjectKind.Spinner)):
            pass
        elif isinstance(kind.inner, HitObjectKind.Slider):
            slider = kind.inner
            if map_obj.mode == GameMode.Osu:
                events = slider_events(
                    h.start_time,
                    slider,
                    map_obj.format_version,
                    map_obj.slider_tick_rate,
                    map_obj.control_points,
                    curve_bufs,
                    ticks,
                )

                for event in events:
                    if event.kind in (SliderEventType.Tick, SliderEventType.LastTick):
                        continue
                    elif event.kind == SliderEventType.Head:
                        samples = (
                            slider.node_samples[0] if slider.node_samples else h.samples
                        )
                        collect_sample(collected_samples, samples, event.time)
                    elif event.kind == SliderEventType.Repeat:
                        idx = event.span_idx + 1
                        samples = (
                            slider.node_samples[idx]
                            if idx < len(slider.node_samples)
                            else h.samples
                        )
                        collect_sample(collected_samples, samples, event.time)
                    elif event.kind == SliderEventType.Tail:
                        idx = slider.repeat_count + 1
                        samples = (
                            slider.node_samples[idx]
                            if idx < len(slider.node_samples)
                            else h.samples
                        )
                        collect_sample(collected_samples, samples, event.time)

            elif map_obj.mode == GameMode.Taiko:
                pass

            elif map_obj.mode == GameMode.Catch:
                events = juicestream_events(
                    h.start_time,
                    slider,
                    map_obj.format_version,
                    map_obj.slider_tick_rate,
                    map_obj.slider_multiplier,
                    map_obj.control_points,
                    curve_bufs,
                    ticks,
                )

                node_idx = 0
                for event in events:
                    if event.kind in (
                        SliderEventType.Head,
                        SliderEventType.Repeat,
                        SliderEventType.Tail,
                    ):
                        samples = (
                            slider.node_samples[node_idx]
                            if node_idx < len(slider.node_samples)
                            else h.samples
                        )
                        collect_sample(collected_samples, samples, event.time)
                        node_idx += 1
                    elif event.kind in (SliderEventType.Tick, SliderEventType.LastTick):
                        continue

            elif map_obj.mode == GameMode.Mania:
                collect_sample(collected_samples, h.samples, h.start_time)

        elif isinstance(kind, HitObjectKind.Hold):
            collect_sample(collected_samples, h.samples, h.start_time)

    collected_samples.sort(key=lambda s: s.time)

    if not collected_samples:
        return

    it = iter(collected_samples)
    try:
        first_sample = next(it)
        control_points.add(first_sample)
        last_sample = first_sample

        for current_sample in it:
            if not current_sample.is_redundant(last_sample):
                control_points.add(current_sample)
                last_sample = current_sample
    except StopIteration:
        pass


def collect_sample(
    collected_samples: list[SamplePoint],
    samples: list[HitSampleInfo],
    end_time: float,
) -> None:
    if not samples:
        return

    volume = max(sample.volume for sample in samples)
    custom_idx = max(sample.custom_sample_bank for sample in samples)

    sample_point = SamplePoint(
        time=end_time,
        sample_bank=SamplePoint.DEFAULT_SAMPLE_BANK,
        sample_volume=volume,
        custom_sample_bank=custom_idx,
    )

    collected_samples.append(sample_point)


def slider_events(
    start_time: float,
    slider: "HitObjectSlider",
    format_version: int,
    slider_tick_rate: float,
    control_points: "ControlPoints",
    curve_bufs: "CurveBuffers",
    ticks: list["SliderEvent"],
) -> "SliderEventsIter":
    timing_point = control_points.timing_point_at(start_time)
    beat_len = (
        timing_point.beat_len
        if timing_point is not None
        else TimingPoint.DEFAULT_BEAT_LEN
    )

    difficulty_point = control_points.difficulty_point_at(start_time)
    if difficulty_point is not None:
        slider_velocity = difficulty_point.slider_velocity
        generate_ticks = difficulty_point.generate_ticks
    else:
        slider_velocity = DifficultyPoint.DEFAULT_SLIDER_VELOCITY
        generate_ticks = DifficultyPoint.DEFAULT_GENERATE_TICKS

    tick_dist_multiplier = (1.0 / slider_velocity) if format_version < 8 else 1.0

    scoring_dist = slider_velocity * beat_len

    if generate_ticks:
        tick_dist = (scoring_dist / slider_tick_rate) * tick_dist_multiplier
    else:
        tick_dist = math.inf

    dist = slider.path.get_curve_with_bufs(curve_bufs).dist()
    span_count = slider.span_count()

    total_duration = slider.duration_with_bufs(curve_bufs)
    span_duration = total_duration / float(span_count)

    return SliderEventsIter.new(
        start_time, span_duration, slider_velocity, tick_dist, dist, span_count, ticks
    )


def juicestream_events(
    start_time: float,
    slider: "HitObjectSlider",
    format_version: int,
    slider_tick_rate: float,
    slider_multiplier: float,
    control_points: "ControlPoints",
    curve_bufs: "CurveBuffers",
    ticks: list["SliderEvent"],
) -> "SliderEventsIter":
    difficulty_point = control_points.difficulty_point_at(start_time)
    slider_velocity = (
        difficulty_point.slider_velocity
        if difficulty_point is not None
        else DifficultyPoint.DEFAULT_SLIDER_VELOCITY
    )

    tick_dist_multiplier = (1.0 / slider_velocity) if format_version < 8 else 1.0
    tick_dist_factor = float(BASE_SCORING_DIST) * slider_multiplier / slider_tick_rate
    tick_dist = tick_dist_factor * tick_dist_multiplier

    dist = slider.path.get_curve_with_bufs(curve_bufs).dist()
    span_count = slider.span_count()

    total_duration = slider.duration_with_bufs(curve_bufs)
    span_duration = total_duration / float(span_count)

    return SliderEventsIter.new(
        start_time, span_duration, tick_dist, dist, span_count, ticks
    )
