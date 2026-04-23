from typing import TypeVar

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
    def parse_num(s: str, number_type: type[N]) -> int | float:
        return number_type.parse(s)

    @staticmethod
    def parse_with_limits(
        s: str, number_type: type[N], limit: int | float
    ) -> int | float:
        return number_type.parse_with_limits(s, limit)

    @staticmethod
    def to_standardized_path(s: str) -> str:
        return s.replace("\\", "/")

    @staticmethod
    def clean_filename(s: str) -> str:
        cleaned = s.strip().strip('"')
        cleaned = cleaned.replace("\\\\", "\\")
        return StrExtra.to_standardized_path(cleaned)
