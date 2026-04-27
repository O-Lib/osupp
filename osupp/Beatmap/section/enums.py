from enum import Enum, IntEnum, IntFlag


class ParseGameModeError(Exception):
    def __init__(self, message: str = "invalid game mode"):
        super().__init__(message)


class GameMode(IntEnum):
    Osu = 0
    Taiko = 1
    Catch = 2
    Mania = 3

    @classmethod
    def from_str(cls, mode: str) -> "GameMode":
        match mode:
            case "0":
                return cls.Osu
            case "1":
                return cls.Taiko
            case "2":
                return cls.Catch
            case "3":
                return cls.Mania
            case _:
                raise ParseGamemodeError()

    @classmethod
    def from_int(cls, mode: int) -> "GameMode":
        match mode:
            case 0:
                return cls.Osu
            case 1:
                return cls.Taiko
            case 2:
                return cls.Catch
            case 3:
                return cls.Mania
            case _:
                return cls.Osu


class ParseCountdownTypeError(Exception):
    def __init__(self, message: str = "invalid countdown type"):
        super().__init__(message)


class CountdownType(IntEnum):
    NONE = 0
    NORMAL = 1
    HALFSPEED = 2
    DOUBLESPEED = 3

    @classmethod
    def from_str(cls, s: str) -> "CountdownType":
        match s:
            case "0" | "None":
                return cls.NONE
            case "1" | "Normal":
                return cls.NORMAL
            case "2" | "Half speed":
                return cls.HALFSPEED
            case "3" | "Double speed":
                return cls.DOUBLESPEED
            case _:
                raise ParseCountdownTypeError()


class SampleBank(IntEnum):
    None_ = 0
    Normal = 1
    Soft = 2
    Drum = 3

    def to_lowercase_str(self) -> str:
        return self.name.lower().replace("none_", "none")

    def __str__(self) -> str:
        return self.to_lowercase_str()


class HitSoundType(IntFlag):
    NONE = 0
    NORMAL = 1
    WHISTLE = 2
    FINISH = 4
    CLAP = 8

    def has_flag(self, flag: "HitSoundType") -> bool:
        return (self.value & flag.value) != 0


class SplineType(Enum):
    Catmull = 0
    BSpline = 1
    Linear = 2
    PerfectCurve = 3


class Section(Enum):
    General = "General"
    Editor = "Editor"
    Metadata = "Metadata"
    Difficulty = "Difficulty"
    Events = "Events"
    TimingPoints = "TimingPoints"
    Colors = "Colours"
    HitObjects = "HitObjects"
    Variables = "Variables"
    CatchTheBeat = "CatchTheBeat"
    Mania = "Mania"

    @classmethod
    def try_from_line(cls, line: str) -> "Section | None":
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            name = line[1:-1]
            try:
                return cls(name)
            except ValueError:
                return None
        return None