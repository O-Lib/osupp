import io
from enum import Enum


class Encoding(Enum):
    Utf8 = "utf-8"
    Utf16BE = "utf-16-be"
    Utf16LE = "utf-16-le"

    @classmethod
    def from_bom(cls, bom: bytes) -> tuple["Encoding", int]:
        if bom.startswith(b"\xef\xbb\xbf"):
            return cls.Utf8, 3
        elif bom.startswith(b"\xff\xfe"):
            return cls.Utf16LE, 2
        elif bom.startswith(b"\xfe\xff"):
            return cls.Utf16BE, 2

        return cls.Utf8, 0


class Decoder:
    def __init__(self, stream: io.BufferedReader):
        self.stream = stream

        bom_candidate = self.stream.peek(3)[:3]
        self.encoding, consumed = Encoding.from_bom(bom_candidate)

        self.stream.read(consumed)

    def read_line(self) -> str | None:
        raw_line = self.stream.readline()

        if not raw_line:
            return None

        if self.encoding == Encoding.Utf16LE and raw_line.endswith(b"\n"):
            extra_byte = self.stream.read(1)
            raw_line += extra_byte

        decoded = raw_line.decode(self.encoding.value, errors="replace")

        return decoded.rstrip()
