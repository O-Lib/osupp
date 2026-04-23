from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from collections.abc import Iterable

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
        mapping = {
            HitSampleDefaultName.NORMAL: "hitnormal",
            HitSampleDefaultName.WHISTLE: "hitwhistle",
            HitSampleDefaultName.FINISH: "hitfinish",
            HitSampleDefaultName.CLAP: "hitclap",
        }
        return mapping[self]

    def __str__(self) -> str:
        return self.to_lowercase_str()


class HitSampleInfoName(Enum):
    Default = HitSampleDefaultName
    File = str


class HitSampleInfo:
    HIT_NORMAL = HitSampleDefaultName.NORMAL
    HIT_WHISTLE = HitSampleDefaultName.WHISTLE
    HIT_FINISH = HitSampleDefaultName.FINISH
    HIT_CLAP = HitSampleDefaultName.CLAP

    name: HitSampleDefaultName | str
    bank: SampleBank
    suffix: int | None
    volume: int
    custom_sample_bank: int
    bank_specified: bool
    is_layered: bool = False

    def __init__(
        self,
        name: HitSampleDefaultName | str,
        bank: SampleBank | None = None,
        custom_sample_bank: int = 0,
        volume: int = 100,
    ):
        self.name = name
        self.bank = bank if bank is not None else SampleBank.NORMAL
        self.suffix = custom_sample_bank if custom_sample_bank >= 2 else None
        self.volume = volume
        self.custom_sample_bank = custom_sample_bank
        self.bank_specified = bank is not None
        self.is_layered = False

    def lookup_name(self) -> "LookupName":
        return LookupName(self)


class LookupName:
    def __init__(self, sample_info: "HitSampleInfo"):
        self.sample_info = sample_info

    def __str__(self) -> str:
        info = self.sample_info

        if isinstance(info.name, str):
            return info.name

        bank_str = str(info.bank).capitalize()
        name_str = info.name.to_lowercase_str()

        if info.suffix is not None:
            return f"Gameplay/{bank_str}-{name_str}{info.suffix}"

        return f"Gameplay/{bank_str}-{name_str}"


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
            raise ParseHitSoundTypeError() from e

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

    def read_custom_sample_banks(self, split: Iterable[str], banks_only: bool = False):
        try:
            first = next(split, None)
            if not first:
                return

            bank_val = int(first)
            bank = (
                SampleBank(bank_val) if bank_val in [0, 1, 2, 3] else SampleBank.NORMAL
            )

            add_bank_str = next(split, None)
            if add_bank_str is None:
                raise ParseSampleBankInfoError.missing_info

            add_bank_val = int(add_bank_str)
            add_bank = (
                SampleBank(add_bank_val)
                if add_bank_val in [0, 1, 2, 3]
                else SampleBank.NORMAL
            )

            normal_bank = bank if bank != SampleBank.NONE else None
            addition_bank = add_bank if add_bank != SampleBank.NONE else None

            self.bank_for_normal = normal_bank
            self.bank_for_addition = addition_bank or normal_bank

            if banks_only:
                return

            next_val = next(split, None)
            if next_val is not None:
                self.custom_sample_bank = int(next_val)

            next_val = next(split, None)
            if next_val is not None:
                self.volume = max(0, int(next_val))

            self.filename = next(split, None) or None
        except (ValueError, StopIteration):
            pass

    def convert_sound_type(self, sound_type: HitSoundType) -> list[HitSampleInfo]:
        sound_types: list[HitSampleInfo] = []

        if self.filename and self.filename.strip():
            sound_types.append(
                HitSampleInfo(
                    name=self.filename,
                    bank=None,
                    custom_sample_bank=1,
                    volume=self.volume,
                )
            )
        else:
            sample = HitSampleInfo(
                name=HitSampleDefaultName.NORMAL,
                bank=self.bank_for_normal,
                custom_sample_bank=self.custom_sample_bank,
                volume=self.volume,
            )

            sample.is_layered = (
                sound_type.value != HitSoundType.NONE
                and not sound_type.has_flag(HitSoundType.NORMAL)
            )
            sound_types.append(sample)

        if sound_type.has_flag(HitSoundType.FINISH):
            sound_types.append(
                HitSampleInfo(
                    name=HitSampleDefaultName.FINISH,
                    bank=self.bank_for_addition,
                    custom_sample_bank=self.custom_sample_bank,
                    volume=self.volume,
                )
            )

        if sound_type.has_flag(HitSoundType.WHISTLE):
            sound_types.append(
                HitSampleInfo(
                    name=HitSampleDefaultName.WHISTLE,
                    bank=self.bank_for_addition,
                    custom_sample_bank=self.custom_sample_bank,
                    volume=self.volume,
                )
            )

        if sound_type.has_flag(HitSoundType.CLAP):
            sound_types.append(
                HitSampleInfo(
                    name=HitSampleDefaultName.CLAP,
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
