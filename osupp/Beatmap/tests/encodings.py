import unittest
from osupp.Beatmap import Beatmap

class TestEncodings(unittest.TestCase):
    def test_utf8_no_bom(self):
        bytes_data = b"osu file format v42\n\n"
        map_obj = Beatmap.from_bytes(bytes_data)
        self.assertEqual(map_obj.format_version, 42)

        bytes_data = b"\x20\x09\n\nosu file format v42\n\n"
        map_obj = Beatmap.from_bytes(bytes_data)
        self.assertEqual(map_obj.format_version, 42)

    def test_utf8_bom(self):
        bytes_data = b"\xef\xbb\xbfosu file format v42\n\n"
        map_obj = Beatmap.from_bytes(bytes_data)
        self.assertEqual(map_obj.format_version, 42)

        bytes_data = b"\xef\xbb\xbf\x20\x09\n\nosu file format v42\n\n"
        map_obj = Beatmap.from_bytes(bytes_data)
        self.assertEqual(map_obj.format_version, 42)

    def test_utf16_le(self):
        bytes_data = b"\xff\xfeo\0s\0u\0 \0f\0i\0l\0e\0 \0f\0o\0r\0m\0a\0t\0 \0v\04\02\0\n\0\n\0"
        map_obj = Beatmap.from_bytes(bytes_data)
        self.assertEqual(map_obj.format_version, 42)

        bytes_data = b"\xff\xfe\x09\x20\n\0\n\0o\0s\0u\0 \0f\0i\0l\0e\0 \0f\0o\0r\0m\0a\0t\0 \0v\04\02\0\n\0\n\0"
        map_obj = Beatmap.from_bytes(bytes_data)
        self.assertEqual(map_obj.format_version, 42)

    def test_utf16_be(self):
        bytes_data = b"\xfe\xff\0o\0s\0u\0 \0f\0i\0l\0e\0 \0f\0o\0r\0m\0a\0t\0 \0v\04\02\0\n\0\n"
        map_obj = Beatmap.from_bytes(bytes_data)
        self.assertEqual(map_obj.format_version, 42)

        bytes_data = b"\xfe\xff\x20\x09\0\n\0\n\0o\0s\0u\0 \0f\0i\0l\0e\0 \0f\0o\0r\0m\0a\0t\0 \0v\04\02\0\n\0\n"
        map_obj = Beatmap.from_bytes(bytes_data)
        self.assertEqual(map_obj.format_version, 42)

if __name__ == "__main__":
    unittest.main()
