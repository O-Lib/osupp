from enum import Enum

from .u16_iter import U16BeInterator, U16LeInterator


class Encoding(Enum):
    UTF8 = 1
    UTF16BE = 2
    UTF16LE = 3

    @classmethod
    def default(cls) -> "Encoding":
        return cls.UTF8

    @staticmethod
    def from_bom(bom: bytes) -> tuple["Encoding", int]:
        if bom.startswith(b"\xef\xbb\xbf"):
            return Encoding.UTF8, 3
        if bom.startswith(b"\xff\xfe"):
            return Encoding.UTF16LE, 2
        if bom.startswith(b"\xfe\xff"):
            return Encoding.UTF16BE, 2

        return Encoding.UTF8, 0

    def decode(self, src: bytes, dst: list[str]) -> str:
        if self == Encoding.UTF8:
            try:
                return src.decode("utf-8", errors="replace")
            except Exception:
                return "\ufffd"

        elif self == Encoding.UTF16LE:
            try:
                return src.decode("utf-16-le", errors="replace")
            except Exception:
                return "\ufffd"

        elif self == Encoding.UTF16BE:
            try:
                return src.decode("utf-16-be", errors="replace")
            except Exception:
                return "\ufffd"

        return ""

    @staticmethod
    def _decode_utf16(
        src_iter: Union[U16LeInterator, U16BeInterator], dst: list[str]
    ) -> str:
        res_chars = []
        raw_values = list(src_iter)

        if isinstance(src_iter, U16LeInterator):
            b_data = bytearray()
            for val in raw_values:
                b_data.extend(val.to_bytes(2, "little"))
            decoded = b_data.decode("utf-16-le", errors="replace")
        else:
            b_data = bytearray()
            for val in raw_values:
                b_data.extend(val.to_bytes(2, "big"))
            decoded = b_data.decode("utf-16-be", errors="replace")

        return decoded
