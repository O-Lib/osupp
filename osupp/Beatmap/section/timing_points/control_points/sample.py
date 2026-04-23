from dataclasses import dataclass
import bisect
from typing import TYPE_CHECKING

from section.hit_objects.hit_samples import HitSampleInfo, HitSampleInfoName, SampleBank, HitSampleDefaultName

if TYPE_CHECKING:
    from section.timing_points import ControlPoints


@dataclass
class SamplePoint:
    time: float
    sample_bank: SampleBank
    sample_volume: int
    custom_sample_bank: int

    DEFAULT_SAMPLE_BANK: SampleBank = SampleBank.NORMAL
    DEFAULT_SAMPLE_VOLUME: int = 100
    DEFAULT_CUSTOM_SAMPLE_BANK: int = 0

    @classmethod
    def default(cls) -> "SamplePoint":
        return cls(
            time= 0.0,
            sample_bank=cls.DEFAULT_SAMPLE_BANK,
            sample_volume=cls.DEFAULT_SAMPLE_VOLUME,
            custom_sample_bank=cls.DEFAULT_CUSTOM_SAMPLE_BANK
        )

    @classmethod
    def new(cls, time: float, sample_bank: SampleBank, sample_volume: int, custom_sample_bank: int) -> "SamplePoint":
        return cls(
            time=time,
            sample_bank=sample_bank,
            sample_volume=max(0, min(100, sample_volume)),
            custom_sample_bank=custom_sample_bank
        )

    def check_already_existing(self, control_points: "ControlPoints") -> bool:
        points = control_points.sample_points
        idx = bisect.bisect_left(points, self.time, key=lambda p: p.time)

        target_idx = None
        if idx < len(points) and points[idx].time == self.time:
            target_idx = idx
        elif idx > 0:
            target_idx = idx - 1

        if target_idx is not None:
            return self.is_redundant(points[target_idx])

        return False

    def add_to(self, control_points: "ControlPoints") -> None:
        points = control_points.sample_points
        idx = bisect.bisect_left(points, self.time, key=lambda p: p.time)

        if idx < len(points) and points[idx].time == self.time:
            points[idx] = self
        else:
            points.insert(idx, self)

    def is_redundant(self, existing: "SamplePoint") -> bool:
        return (
            self.sample_bank == existing.sample_bank and
            self.sample_volume == existing.sample_volume and
            self.custom_sample_bank == existing.custom_sample_bank
        )

    def apply(self, sample: "HitSampleInfo") -> None:
        if isinstance(sample.name, HitSampleDefaultName):
            if sample.custom_sample_bank == 0:
                sample.custom_sample_bank = self.custom_sample_bank

                if sample.custom_sample_bank >= 2:
                    sample.suffix = sample.custom_sample_bank

            if sample.volume == 0:
                sample.volume = max(0, min(100, self.sample_volume))

            if not sample.bank_specified:
                sample.bank = self.sample_bank
                sample.bank_specified = True

        else:
            sample.bank = self.DEFAULT_SAMPLE_BANK
            sample.suffix = None

            if sample.volume == 0:
                sample.volume = max(0, min(100, self.sample_volume))

            sample.custom_sample_bank = 1
            sample.bank_specified = False
            sample.is_layered = False

    def __lt__(self, other: "SamplePoint") -> bool:
        if not isinstance(other, SamplePoint):
            return NotImplemented
        return self.time < other.time

    def __le__(self, other: "SamplePoint") -> bool:
        if not isinstance(other, SamplePoint):
            return NotImplemented
        return self.time <= other.time

    def __gt__(self, other: "SamplePoint") -> bool:
        if not isinstance(other, SamplePoint):
            return NotImplemented
        return self.time > other.time

    def __ge__(self, other: "SamplePoint") -> bool:
        if not isinstance(other, SamplePoint):
            return NotImplemented
        return self.time >= other.time