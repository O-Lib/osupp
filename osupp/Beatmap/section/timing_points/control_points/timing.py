from dataclasses import dataclass

@dataclass
class TimingPoint:
    time: float
    beat_len: float
    omit_first_bar_line: bool
    time_signature: TimeSignature

    DEFAULT_BEAT_LEN: float = 60000.0 / 60.0
    DEFAULT_OMIT_FIRST_BAR_LINE: bool = False

    @classmethod
    def default(cls) -> "TimingPoint":
        return cls(
            time=0.0,
            beat_len=cls.DEFAULT_BEAT_LEN,
            omit_first_bar_line=cls.DEFAULT_OMIT_FIRST_BAR_LINE,
            time_signature=TimeSignature.new_simple_quadruple()
        )

    @classmethod
    def new(cls, time: float, beat_len: float, omit_first_bar_line: bool, time_signature: TimeSignature) -> "TimingPoint":
        clamped_beat_len = max(6.0, min(60000.0, beat_len))

        return cls(
            time=time,
            beat_len=clamped_beat_len,
            omit_first_bar_line=omit_first_bar_line,
            time_signature=time_signature
        )

    def __lt__(self, other: "TimingPoint") -> bool:
        if not isinstance(other, TimingPoint):
            return NotImplemented
        return self.time < other.time

    def __le__(self, other: "TimingPoint") -> bool:
        if not isinstance(other, TimingPoint):
            return NotImplemented
        return self.time <= other.time

    def __gt__(self, other: "TimingPoint") -> bool:
        if not isinstance(other, TimingPoint):
            return NotImplemented
        return self.time > other.time

    def __ge__(self, other: "TimingPoint") -> bool:
        if not isinstance(other, TimingPoint):
            return NotImplemented
        return self.time >= other.time

@dataclass(frozen=True)
class TimeSignature:
    numerator: int

    @classmethod
    def new(cls, numerator: int) -> "TimeSignature":
        if numerator <= 0:
            raise TimeSignatureError()
        return cls(numerator)

    @classmethod
    def try_from(cls, numerator: int) -> "TimeSignature":
        return cls.new(numerator)

    @classmethod
    def new_simple_triple(cls) -> "TimeSignature":
        return cls(3)

    @classmethod
    def new_simple_quadruple(cls) -> "TimeSignature":
        return cls(4)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TimeSignature):
            return NotImplemented
        return self.numerator == other.numerator

    def __repr__(self) -> str:
        return f"TimeSignature({self.numerator})"

class TimeSignatureError(Exception):
    def __init__(self):
        super().__init__("time signature numerator must be positive")