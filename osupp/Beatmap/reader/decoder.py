from typing import TypeVar, Generic, BinaryIO
from encoding import Encoding
import io

R = TypeVar("R", bound=BinaryIO)

class Decoder(Generic[R]):
    __slots__ = ("inner", "read_buf", "decode_buf", "encoding")

    def __init__(self, inner: R):
        self.inner = inner
        self.read_buf: bytearray = bytearray()
        self.decode_buf: str = ""
        self.encoding: Encoding = Encoding.default()

    @classmethod
    def new(cls, inner: io.BufferedIOBase) -> "Decoder":
        encoding = cls.read_bom(inner)
        decoder = cls(inner)
        decoder.encoding = encoding
        return decoder

    @staticmethod
    def read_bom(reader: io.BufferedIOBase) -> Encoding:
        buf = reader.peek(3)[:3]

        if len(buf) == 0:
            return Encoding.default()

        encoding, consumed = Encoding.from_bom(buf)
        reader.read(consumed)

        return encoding

    def read_line(self) -> str | None:
        self.read_buf.clear()

        line = self.inner.readline()

        if not line:
            return None

        self.read_buf.extend(line)

        if self.encoding == Encoding.UTF16LE and self.read_buf.endswith(b"\n"):
            extra_byte = self.inner.read(1)
            if extra_byte:
                self.read_buf.extend(extra_byte)

        self.decode_buf = self.encoding.decode(bytes(self.read_buf), [])
        return self.decode_buf

    def curr_line(self) -> str:
        return self.decode_buf.rstrip('\r\n ')