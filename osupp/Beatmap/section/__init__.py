from enum import Enum, auto
from typing import Optional


class UnknownKeyError(Exception):
    def __init__(self, message: str = "unknown key"):
        super().__init__(message)


class Section(Enum):
    General = auto()
    Editor = auto()
    Metadata = auto()
    Difficulty = auto()
    Events = auto()
    TimingPoints = auto()
    Colors = auto()
    HitObjects = auto()
    Variables = auto()
    CatchTheBeat = auto()
    Mania = auto()

    @classmethod
    def try_from_line(cls, line: str) -> Optional["Section"]:
        if not (line.startswith("[") and line.endswith("]")):
            return None
        section_name = line[1:-1]

        mapping = {
            "General": cls.General,
            "Editor": cls.Editor,
            "Metadata": cls.Metadata,
            "Difficulty": cls.Difficulty,
            "Events": cls.Events,
            "TimingPoints": cls.TimingPoints,
            "Colours": cls.Colors,
            "HitObjects": cls.HitObjects,
            "Variables": cls.Variables,
            "CatchTheBeat": cls.CatchTheBeat,
            "Mania": cls.Mania,
        }
        return mapping.get(section_name)

    def __str__(self) -> str:
        return self.name
