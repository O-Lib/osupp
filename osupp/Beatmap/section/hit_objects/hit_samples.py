from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from typing import Union

from utils import ParseNumberError


class SampleBank(IntEnum):
    NONE = 0
    NORMAL = 1
    SOFT = 2
    DRUM = 3

    @classmethod
    def from_int(cls, value: int) -> "SampleBank":
        try:
            return cls(value)
        except ValueError:
            raise ParseSampleBankError()

    def to_lowercase_str(self) -> str:
        mapping = {
            SampleBank.NONE: "none",
            SampleBank.NORMAL: "normal",
            SampleBank.SOFT: "soft",
            SampleBank.DRUM: "drum",
        }
        return mapping[self]

    @classmethod
    def parse(cls, s: str) -> "SampleBank":
        if s == "0" or s == "None":
            return cls.NONE
        if s == "1" or s == "Normal":
            return cls.NORMAL
        if s == "2" or s == "Soft":
            return cls.SOFT
        if s == "3" or s == "Drum":
            return cls.DRUM

        return cls.NONE

    @classmethod
    def from_lowercase(cls, s: str) -> "SampleBank":
        s = s.lower()
        if s == "normal":
            return cls.NORMAL
        if s == "soft":
            return cls.SOFT
        if s == "drum":
            return cls.DRUM

        return cls.NONE

    def __str__(self) -> str:
        return self.to_lowercase_str()


class HitSampleDefaultName(Enum):
    NORMAL = auto()
    WHISTLE = auto()
    FINISH = auto()
    CLAP = auto()

    def to_lowercase_str(self) -> str:
        if self == HitSampleDefaultName.NORMAL:
            return "hitnormal"
        elif self == HitSampleDefaultName.WHISTLE:
            return "hitwhistle"
        elif self == HitSampleDefaultName.FINISH:
            return "hitfinish"
        elif self == HitSampleDefaultName.CLAP:
            return "hitclap"
        return ""

    def __str__(self) -> str:
        return self.to_lowercase_str()


@dataclass
class HitSampleInfoName:
    inner: HitSampleDefaultName | str


@dataclass
class HitSampleInfo:
    name: HitSampleInfoName
    bank: SampleBank
    suffix: int | None
    volume: int
    custom_sample_bank: int
    bank_specified: bool
    is_layered: bool = False

    HIT_NORMAL = HitSampleInfoName(HitSampleDefaultName.NORMAL)
    HIT_WHISTLE = HitSampleInfoName(HitSampleDefaultName.WHISTLE)
    HIT_FINISH = HitSampleInfoName(HitSampleDefaultName.FINISH)
    HIT_CLAP = HitSampleInfoName(HitSampleDefaultName.CLAP)

    @classmethod
    def new(
        cls,
        name: HitSampleInfoName,
        bank: SampleBank | None,
        custom_sample_bank: int,
        volume: int,
    ) -> "HitSampleInfo":
        resolved_bank = bank if bank is not None else SampleBank.NORMAL

        suffix: int | None = custom_sample_bank if custom_sample_bank >= 2 else None

        return cls(
            name=name,
            bank=resolved_bank,
            suffix=suffix,
            volume=volume,
            custom_sample_bank=custom_sample_bank,
            bank_specified=bank is not None,
            is_layered=False,
        )

    def lookup_name(self) -> "LookupName":
        return LookupName(self)


class LookupName:
    def __init__(self, sample_info: "HitSampleInfo") -> None:
        self.sample_info = sample_info

    def __str__(self) -> str:
        info = self.sample_info

        if isinstance(info.inner, HitSampleDefaultName):
            bank = str(self.sample_info.bank).lower()
            sample_name = info.inner.to_lowercase_str()

            if self.sample_info.suffix is not None:
                return f"Gameplay/{bank}-{sample_name}{self.sample_info.suffix}"

            return f"Gameplay/{bank}-{sample_name}"

        elif isinstance(info.inner, str):
            return info.inner

        return ""


class ParseSampleBankError(ValueError):
    def __init__(self):
        super().__init__("invalid sample bank value")


class HitSoundType:
    NONE = 0
    NORMAL = 1
    WHISTLE = 2
    FINISH = 4
    CLAP = 8

    def __init__(self, value: int = 0):
        self.value = value

    @classmethod
    def from_str(cls, s: str) -> "HitSoundType":
        try:
            n = int(s)
            return cls(n)
        except ValueError as e:
            raise ParseHitSoundTypeError(e) from e

    def __eq__(self, other: object) -> bool:
        if isinstance(other, int):
            return self.value == (other & 0xFF)
        if isinstance(other, HitSoundType):
            return self.value == other.value
        return False

    def __and__(self, rhs: int) -> int:
        return self.value & rhs

    def __iand__(self, rhs: int) -> "HitSoundType":
        self.value &= rhs & 0xFF
        return self

    def __int__(self) -> int:
        return self.value

    def has_flag(self, flag: int) -> bool:
        if flag == self.NONE:
            return self.value == self.NONE
        return (self.value & flag) != 0

    @classmethod
    def from_samples(cls, samples: list["HitSampleInfo"]) -> "HitSoundType":
        kind = cls.NONE

        for sample in samples:
            if sample.name == HitSampleDefaultName.WHISTLE:
                kind |= cls.WHISTLE
            elif sample.name == HitSampleDefaultName.FINISH:
                kind |= cls.FINISH
            elif sample.name == HitSampleDefaultName.CLAP:
                kind |= cls.CLAP

        return cls(kind)


class ParseHitSoundTypeError(Exception):
    def __init__(self, source: Exception):
        self.source = source
        super().__init__(f"invalid hit sound type: {source}")


@dataclass
class SampleBankInfo:
    filename: str | None = None
    bank_for_normal: SampleBank | None = None
    bank_for_addition: SampleBank | None = None
    volume: int = 0
    custom_sample_bank: int = 0

    def read_custom_sample_banks(self, split: iter, banks_only: bool) -> None:
        try:
            first = next(split_iter, None)
            if not first:
                return

            bank_val = int(first)
            bank = (
                SampleBank(bank_val)
                if bank_val in [s.value for s in SampleBank]
                else SampleBank.NORMAL
            )

            second = next(split, None)
            if second is None:
                raise ValueError("Missing addition bank info")

            add_bank_val = int(second)
            add_bank = (
                SampleBank(add_bank_val)
                if add_bank_val in [s.value for s in SampleBank]
                else SampleBank.NORMAL
            )

            self.bank_for_normal = bank if bank != SampleBank.NONE else None

            effective_add = add_bank if add_bank != SampleBank.NONE else None
            self.bank_for_addition = (
                effective_add if effective_add is not None else self.bank_for_normal
            )

            if banks_only:
                return

            next_val = next(split, None)
            if next_val is not None:
                self.custom_sample_bank = int(next_val)

            next_val = next(split, None)
            if next_val is not None:
                self.volume = max(0, int(next_val))

            self.filename = next(split, None)

        except (ValueError, StopIteration):
            pass

    def convert_sound_type(self, sound_type: "HitSoundType") -> list[HitSampleInfo]:
        sound_types: list[HitSampleInfo] = []

        if self.filename and self.filename.strip():
            sound_types.append(
                HitSampleInfo.new(
                    name=HitSampleInfoName(self.filename),
                    bank=None,
                    custom_sample_bank=1,
                    volume=self.volume,
                )
            )
        else:
            sample = HitSampleInfo.new(
                name=HitSampleInfo.HIT_NORMAL,
                bank=self.bank_for_normal,
                custom_sample_bank=self.custom_sample_bank,
                volume=self.volume,
            )

            sample.is_layered = (
                sound_type != HitSoundType.NONE
                and not sound_type.has_flag(HitSoundType.NORMAL)
            )
            sound_types.append(sample)

        if sound_type.has_flag(HitSoundType.FINISH):
            sound_types.append(
                HitSampleInfo.new(
                    name=HitSampleInfo.HIT_FINISH,
                    bank=self.bank_for_addition,
                    custom_sample_bank=self.custom_sample_bank,
                    volume=self.volume,
                )
            )

        if sound_type.has_flag(HitSoundType.WHISTLE):
            sound_types.append(
                HitSampleInfo.new(
                    name=HitSampleInfo.HIT_WHISTLE,
                    bank=self.bank_for_addition,
                    custom_sample_bank=self.custom_sample_bank,
                    volume=self.volume,
                )
            )

        if sound_type.has_flag(HitSoundType.CLAP):
            sound_types.append(
                HitSampleInfo.new(
                    name=HitSampleInfo.HIT_CLAP,
                    bank=self.bank_for_addition,
                    custom_sample_bank=self.custom_sample_bank,
                    volume=self.volume,
                )
            )

        return sound_types


class ParseSampleBankInfoError(Exception):
    def __init__(self, message: str, source: Exception | None = None):
        self.message = message
        self.source = source
        super().__init__(f"{message}" + (f" (caused by: {source})" if source else ""))

    @classmethod
    def missing_info(cls):
        return cls("missing info")

    @classmethod
    def from_number(cls, error: "ParseNumberError"):
        return cls("failed to parse number", source=error)
