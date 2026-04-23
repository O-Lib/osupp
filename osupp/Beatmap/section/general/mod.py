from enum import IntEnum


class GameMode(IntEnum):
    Osu = 0
    Taiko = 1
    Catch = 2
    Mania = 3

    @classmethod
    def default(cls) -> "GameMode":
        return cls.Osu

    @classmethod
    def from_str(cls, mode: str) -> "GameMode":
        if mode == "0":
            return cls.Osu
        elif mode == "1":
            return cls.Taiko
        elif mode == "2":
            return cls.Catch
        elif mode == "3":
            return cls.Mania
        else:
            raise ParseGameModeError()

    @classmethod
    def from_uint(cls, mode: int) -> "GameMode":
        try:
            return cls(mode)
        except ValueError:
            return cls.Osu


class ParseGameModeError(Exception):
    def __init__(self):
        super().__init__("invalid game mode")


class CountdownType(IntEnum):
    None_ = 0
    Normal = 1
    HalfSpeed = 2
    DoubleSpeed = 3

    @classmethod
    def default(cls) -> "CountdownType":
        return cls.None_

    @classmethod
    def from_str(cls, s: str) -> "CountdownType":
        if s == "0" or s == "None":
            return cls.None_
        elif s == "1" or s == "Normal":
            return cls.Normal
        elif s == "2" or s == "Half speed":
            return cls.HalfSpeed
        elif s == "3" or s == "Double speed":
            return cls.DoubleSpeed
        else:
            raise ParseCountdownTypeError()


class ParseCountdownTypeError(Exception):
    def __init__(self):
        super().__init__("invalid countdown type")
