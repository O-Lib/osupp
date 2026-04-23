from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class SliderEventType(Enum):
    Head = auto()
    Tick = auto()
    Repeat = auto()
    LastTick = auto()
    Tail = auto()


class SliderEventsIterState(Enum):
    Head = auto()
    Ticks = auto()
    LastTick = auto()
    Tail = auto()
    Done = auto()


@dataclass
class SliderEvent:
    kind: SliderEventType
    span_idx: int
    span_start_time: float
    time: float
    path_progress: float


class SliderEventsIter:
    MAX_LEN = 100000.0
    TAIL_LENIENCY = -36.0

    def __init__(
        self,
        start_time: float,
        span_duration: float,
        velocity: float,
        tick_dist: float,
        total_dist: float,
        span_count: int,
        ticks_buf: list["SliderEvent"],
    ):
        self.len = min(self.MAX_LEN, total_dist)
        self.tick_dist = max(0.0, min(tick_dist, self.len))
        self.ticks = ticks_buf
        self.ticks.clear()

        self.start_time = start_time
        self.span_duration = span_duration
        self.span_count = span_count
        self.min_dist_from_end = velocity * 10.0
        self.state = SliderEventsIterState.Head

        self.current_span = 0
        self.current_tick = 0

    def __next__(self) -> SliderEvent:
        while True:
            if self.state == SliderEventsIterState.Head:
                self.state = SliderEventsIterState.Ticks
                self.current_span = 0

                return SliderEvent(
                    kind=SliderEventType.Head,
                    span_idx=0,
                    span_start_time=self.start_time,
                    time=self.start_time,
                    path_progress=0.0,
                )
            elif self.state == SliderEventsIterState.Ticks:
                if self.ticks:
                    return self.ticks.pop()

                if self.current_span == self.span_count:
                    self.state = SliderEventsIterState.LastTick
                    continue
                else:
                    curr_span = self.current_span
                    self.current_span += 1
                    generate_ticks(self, curr_span)
                    continue

            elif self.state == SliderEventsIterState.LastTick:
                total_duration = float(self.span_count) * self.span_duration
                final_span_idx = self.span_count - 1
                final_span_start_time = self.start_time + (
                    float(final_span_idx) * self.span_duration
                )

                last_tick_time = max(
                    self.start_time + total_duration / 2.0,
                    (final_span_start_time + self.span_duration) + self.TAIL_LENIENCY,
                )

                last_tick_progress = (
                    last_tick_time - final_span_start_time
                ) / self.span_duration

                if self.span_count % 2 == 0:
                    last_tick_progress = 1.0 - last_tick_progress

                self.state = SliderEventsIterState.Tail
                return SliderEvent(
                    kind=SliderEventType.LastTick,
                    span_idx=final_span_idx,
                    span_start_time=final_span_start_time,
                    time=last_tick_time,
                    path_progress=last_tick_progress,
                )

            elif self.state == SliderEventsIterState.Tail:
                total_duration = float(self.span_count) * self.span_duration
                final_span_idx = self.span_count - 1

                self.state = SliderEventsIterState.Done
                return SliderEvent(
                    kind=SliderEventType.Tail,
                    span_idx=final_span_idx,
                    span_start_time=self.start_time
                    + (float(self.span_count - 1) * self.span_duration),
                    time=self.start_time + total_duration,
                    path_progress=float(self.span_count % 2),
                )

            elif self.state == SliderEventsIterState.Done:
                raise StopIteration

    def __length_hint__(self) -> int:
        if self.state == SliderEventsIterState.Head:
            return 3
        elif self.state == SliderEventsIterState.Ticks:
            return 2 + len(self.ticks)

        elif self.state == SliderEventsIterState.LastTick:
            return 2

        elif self.state == SliderEventsIterState.Tail:
            return 1

        else:
            return 0


def generate_ticks(iter_obj: "SliderEventsIter", span: int):
    reversed_span = span % 2 == 1
    span_start_time = iter_obj.start_time + float(span) * iter_obj.span_duration
    with_repeat = span < iter_obj.span_count - 1

    if reversed_span and with_repeat:
        repeat = new_repeat_point(span, span_start_time, iter_obj.span_duration)
        iter_obj.ticks.append(repeat)

    d = iter_obj.tick_dist

    if d > 0.0:
        while d <= iter_obj.len:
            if d >= iter_obj.len - iter_obj.min_dist_from_end:
                break

            path_progress = d / iter_obj.len
            time_progress = (1.0 - path_progress) if reversed_span else path_progress

            tick = SliderEvent(
                kind=SliderEventType.Tick,
                span_idx=span,
                span_start_time=span_start_time,
                time=span_start_time + time_progress * iter_obj.span_duration,
                path_progress=path_progress,
            )

            iter_obj.ticks.append(tick)
            d += iter_obj.tick_dist

    if not reversed_span:
        if with_repeat:
            repeat = new_repeat_point(span, span_start_time, iter_obj.span_duration)
            iter_obj.ticks.append(repeat)

        iter_obj.ticks.reverse()


def new_repeat_point(
    span: int, span_start_time: float, span_duration: float
) -> SliderEvent:
    path_progress = float((span + 1) % 2)

    return SliderEvent(
        kind=SliderEventType.Repeat,
        span_idx=span,
        span_start_time=span_start_time,
        time=span_start_time + span_duration,
        path_progress=path_progress,
    )
