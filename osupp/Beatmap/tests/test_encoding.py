import unittest
import os
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
        bytes_data = b"\xEF\xBB\xBFosu file format v42\n\n"
        beatmap = Beatmap.from_bytes(bytes_data)
        self.assertEqual(beatmap.format_version, 42)

        bytes_data = b"\xEF\xBB\xBF\x20\x09\n\nosu file format v42\n\n"
        beatmap = Beatmap.from_bytes(bytes_data)
        self.assertEqual(beatmap.format_version, 42)

    def test_utf16_le(self):
        # Usamos o encode nativo do Python para evitar problemas com bytes octais
        bytes_data = b"\xFF\xFE" + "osu file format v42\n\n".encode("utf-16-le")
        beatmap = Beatmap.from_bytes(bytes_data)
        self.assertEqual(beatmap.format_version, 42)

        # O \x09\x20 em UTF-16 LE representa o caractere invisível U+2009 (Thin Space)
        bytes_data = b"\xFF\xFE\x09\x20\n\x00\n\x00" + "osu file format v42\n\n".encode("utf-16-le")
        beatmap = Beatmap.from_bytes(bytes_data)
        self.assertEqual(beatmap.format_version, 42)

    def test_utf16_be(self):
        bytes_data = b"\xFE\xFF" + "osu file format v42\n\n".encode("utf-16-be")
        beatmap = Beatmap.from_bytes(bytes_data)
        self.assertEqual(beatmap.format_version, 42)

        bytes_data = b"\xFE\xFF\x20\x09\x00\n\x00\n" + "osu file format v42\n\n".encode("utf-16-be")
        beatmap = Beatmap.from_bytes(bytes_data)
        self.assertEqual(beatmap.format_version, 42)