from enum import Enum
from typing import Union, Optional
from dataclasses import dataclass
from utils import ParseNumber, ParseNumberError

VERSION_PREFIX = "osu file format v"
LATEST_FORMAT_VERSION = 14

class ParseVersionError(Exception):
    pass

class UnknownFileFormat(ParseVersionError):
    def __init__(self):
        super().__init__("unknown file format")

class InvalidNumberFormat(ParseVersionError):
    def __init__(self, cause: ParseNumberError):
        super().__init__("failed to parse number")
        self.__cause__ = cause

def try_version_from_line(line: str) -> Optional[Union[int, ParseVersionError]]:
    if not line.startswith(VERSION_PREFIX):
        if not line:
            return None
        else:
            return UnknownFileFormat()

    version_part = line[len(VERSION_PREFIX):].strip()

    if not version_part:
        return LATEST_FORMAT_VERSION

    try:
        return int(version_part)
    except ValueError:
        p_error = ParseNumberError("Invalid integer string")
        return InvalidNumberFormat(p_error)