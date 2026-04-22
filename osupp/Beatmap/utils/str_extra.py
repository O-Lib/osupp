from typing import Type, TypeVar
from .parse_number import ParseNumber

N = TypeVar("N", bound=ParseNumber)

class StrExtra:
    @staticmethod
    def trim_comment(s: str) -> str:
        index = s.find("//")
        if index == -1:
            return s.rstrip()
        return s[:index].rstrip()

    @staticmethod
    def parse_num(s: str, number_type: Type[N]) -> N:
        return number_type.parse(s)

    @staticmethod
    def parse_with_limits(s: str, number_type: Type[N], limit: N) -> N:
        return number_type.parse_with_limits(s, limit)

    @staticmethod
    def to_standardized_path(s: str) -> str:
        return s.replace("\\", "/")

    @staticmethod
    def clean_filename(s: str) -> str:
        cleaned = s.strip('"')
        cleaned = cleaned.replace("\\\\", "\\")
        return StrExtra.to_standardized_path(cleaned)