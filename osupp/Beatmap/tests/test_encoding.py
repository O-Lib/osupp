import unittest

from beatmap import Beatmap


class TestEncodings(unittest.TestCase):
    def test_utf8_no_bom(self):
        bytes_data = b"osu file format v42\n\n"
        beatmap = Beatmap.from_bytes(bytes_data)
        self.assertEqual(beatmap.format_version, 42)

        bytes_data = b"\x20\x09\n\nosu file format v42\n\n"
        beatmap = Beatmap.from_bytes(bytes_data)
        self.assertEqual(beatmap.format_version, 42)

    def test_utf8_bom(self):
        bytes_data = b"\xef\xbb\xbfosu file format v42\n\n"
        beatmap = Beatmap.from_bytes(bytes_data)
        self.assertEqual(beatmap.format_version, 42)

        bytes_data = b"\xef\xbb\xbf\x20\x09\n\nosu file format v42\n\n"
        beatmap = Beatmap.from_bytes(bytes_data)
        self.assertEqual(beatmap.format_version, 42)

    def test_utf16_le(self):
        bytes_data = b"\xff\xfe" + "osu file format v42\n\n".encode("utf-16-le")
        beatmap = Beatmap.from_bytes(bytes_data)
        self.assertEqual(beatmap.format_version, 42)

        bytes_data = b"\xff\xfe\x09\x20\n\x00\n\x00" + "osu file format v42\n\n".encode(
            "utf-16-le"
        )
        beatmap = Beatmap.from_bytes(bytes_data)
        self.assertEqual(beatmap.format_version, 42)

    def test_utf16_be(self):
        bytes_data = b"\xfe\xff" + "osu file format v42\n\n".encode("utf-16-be")
        beatmap = Beatmap.from_bytes(bytes_data)
        self.assertEqual(beatmap.format_version, 42)

        bytes_data = b"\xfe\xff\x20\x09\x00\n\x00\n" + "osu file format v42\n\n".encode(
            "utf-16-be"
        )
        beatmap = Beatmap.from_bytes(bytes_data)
        self.assertEqual(beatmap.format_version, 42)
