import math
from typing import Protocol, TypeVar, runtime_checkable, Type, Union

MAX_PARSE_VALUE: int = 2_147_483_647

T = TypeVar("T", bound="ParseNumber")

@runtime_checkable
class ParseNumber(Protocol):
    @classmethod
    def parse(cls: Type[T], s: str) -> Union[int, float]:
        ...

    @classmethod
    def parse_with_limits(cls: Type[T], s: str, limit: Union[int, float]) -> Union[int, float]:
       ...

# ------------------------------------------------------------------

class Int32:
    @classmethod
    def parse(cls, s:str) -> int:
        return cls.parse_with_limits(s, MAX_PARSE_VALUE)

    @classmethod
    def parse_with_limits(cls, s: str, limit: int) -> int:
        try:
            n = int(s.strip())
        except ValueError as e:
            raise InvalidInteger(e)

        if n < -limit:
            raise NumberUnderflow()
        elif n > limit:
            raise NumberOverflow()
        else:
            return n

# ------------------------------------------------------------------

class Float32:
    @classmethod
    def parse(cls, s: str) -> float:
        return cls.parse_with_limits(s, float(MAX_PARSE_VALUE))

    @classmethod
    def parse_with_limits(cls, s:str, limit: float) -> float:
        try:
            n = float(s.strip())
        except ValueError as e:
            raise InvalidFloat(e)

        if n < -limit:
            raise NumberUnderflow()
        elif n > limit:
            raise NumberOverflow()
        elif math.isnan(n):
            raise NaN()
        else:
            return n

# ------------------------------------------------------------------

class Float64:
    @classmethod
    def parse(cls, s: str) -> float:
        return cls.parse_with_limits(s, float(MAX_PARSE_VALUE))

    @classmethod
    def parse_with_limits(cls, s: str, limit: float) -> float:
        try:
            n = float(s.strip())
        except ValueError as e:
            raise InvalidFloat(e)

        if n < -limit:
            raise NumberUnderflow()
        elif n > limit:
            raise NumberOverflow()
        elif math.isnan(n):
            raise NaN()
        else:
            return n

# ------------------------------------------------------------------

class ParseNumberError(Exception):
    pass

class InvalidFloat(ParseNumberError):
    def __init__(self, source: Exception):
        self.source = source
        super().__init__("invalid float")

class InvalidInteger(ParseNumberError):
    def __init__(self, source: Exception):
        self.source = source
        super().__init__("invalid integer")

class NaN(ParseNumberError):
    def __init__(self):
        super().__init__("not a number")

class NumberOverflow(ParseNumberError):
    def __init__(self):
        super().__init__("value is too high")

class NumberUnderflow(ParseNumberError):
    def __init__(self):
        super().__init__("value is too low")

# ------------------------------------------------------------------