from dataclasses import dataclass


@dataclass(frozen=True)
class EffectFlags:
    value: int = 0

    NONE = 0
    KIAI = 1 << 0
    OMIT_FIRST_BAR_LINE = 1 << 3

    @classmethod
    def parse(cls, s: str) -> "EffectFlags":
        try:
            value = int(float(s))
            return cls(value)
        except ValueError as e:
            raise ParseEffectFlagsError(e)

    @classmethod
    def from_int(cls, flags: int) -> "EffectFlags":
        return cls(flags)

    @classmethod
    def from_str(cls, s: str) -> "EffectFlags":
        try:
            return cls(int(s))
        except (ValueError, TypeError) as e:
            raise ParseEffectFlagsError(e)

    def to_int(self) -> int:
        return self.value

    def has_flag(self, flag: int) -> bool:
        return (self.value & flag) != 0

    def __int__(self) -> int:
        return self.value


class ParseEffectFlagsError(Exception):
    def __init__(self, source: Exception):
        super().__init__(f"Failed to parse effect flags: {source}")
