from dataclasses import dataclass
from typing import Generic, TypeVar

K = TypeVar('K')

# ------------------------------------------------------------------

@dataclass
class KeyValue(Generic[K]):
    key: K
    value: str

    @classmethod
    def parse (cls, s: str, key_type: Type[K]) -> KeyValue[K]:
        parts = s.split(':', 1)

        if len(parts) == 1:
            key_raw = parts[0].strip()
            value = ""
        else:
            key_raw = parts[0].strip()
            value = parts[1].strip()

        return cls(
            key=key_type(key_raw),
            value=value
        )

# ------------------------------------------------------------------

class Key:
    def __init__(self, s: str):
        if s == "key":
            pass
        else:
            raise ValueError("Invalid key")

    def __eq__(self, other):
        return isinstance(other, Key)

    def __repr__(self):
        return "Key"

# ------------------------------------------------------------------