import io
import unittest
from enum import Enum

from beatmap import ParseBeatmapError, UnknownFileFormatError, try_version_from_line
from reader import Decoder, Encoding
from section.enums import GameMode, Section
from section.hit_objects.slider import (
    SliderEventType,
    SliderPath,
    generate_slider_events,
)
from utils import KeyValue


class DummyKey(Enum):
    KEY = "key"

    @classmethod
    def from_str(cls, s: str) -> "DummyKey":
        try:
            return cls(s)
        except ValueError:
            raise ValueError()


class TestKeyValue(unittest.TestCase):
    def test_key_and_value(self):
        kv = KeyValue.parse("key:value", DummyKey.from_str)
        self.assertIsNotNone(kv)
        self.assertEqual(kv.key, DummyKey.KEY)
        self.assertEqual(kv.value, "value")

        kv = KeyValue.parse("  key    :  value   ", DummyKey.from_str)
        self.assertIsNotNone(kv)
        self.assertEqual(kv.key, DummyKey.KEY)
        self.assertEqual(kv.value, "value")

    def test_only_key(self):
        kv = KeyValue.parse("key:", DummyKey.from_str)
        self.assertIsNotNone(kv)
        self.assertEqual(kv.key, DummyKey.KEY)
        self.assertEqual(kv.value, "")

        kv = KeyValue.parse("   key  :   ", DummyKey.from_str)
        self.assertIsNotNone(kv)
        self.assertEqual(kv.key, DummyKey.KEY)
        self.assertEqual(kv.value, "")

    def test_only_value(self):
        self.assertIsNone(KeyValue.parse(":value", DummyKey.from_str))
        self.assertIsNone(KeyValue.parse("  :  value     ", DummyKey.from_str))

    def test_no_colon(self):
        self.assertIsNone(KeyValue.parse("key value", DummyKey.from_str))


class TestReader(unittest.TestCase):
    def test_valid_utf8(self):
        stream = io.BufferedReader(io.BytesIO(b"hello world o/\n"))
        decoder = Decoder(stream)

        self.assertEqual(decoder.read_line(), "hello world o/")

    def test_invalid_utf8(self):
        src = bytes(
            [
                32,
                209,
                44,
                49,
                44,
                55,
                56,
                50,
                52,
                53,
                44,
                57,
                48,
                50,
                52,
                53,
                44,
                48,
                44,
                48,
                44,
                48,
                44,
                50,
                53,
                53,
                44,
                50,
                53,
                53,
                44,
                50,
                53,
                53,
                10,
            ]
        )

        stream = io.BufferedReader(io.BytesIO(src))
        decoder = Decoder(stream)

        self.assertEqual(decoder.read_line(), " \ufffd,1,78245,90245,0,0,0,255,255,255")

    def test_u16_le_works(self):
        bom_utf16_le = b"\xff\xfe"
        src = bom_utf16_le + b"1\x00Z\x00\n\x00"

        stream = io.BufferedReader(io.BytesIO(src))
        decoder = Decoder(stream)

        self.assertEqual(decoder.encoding, Encoding.Utf16LE)
        self.assertEqual(decoder.read_line(), "1Z")

    def test_u16_be_works(self):
        bom_utf16_be = b"\xfe\xff"
        src = bom_utf16_be + b"\x001\x00Z\x00\n"

        stream = io.BufferedReader(io.BytesIO(src))
        decoder = Decoder(stream)

        self.assertEqual(decoder.encoding, Encoding.Utf16BE)
        self.assertEqual(decoder.read_line(), "1Z")


class TestSliderEvents(unittest.TestCase):
    START_TIME = 0.0
    SPAN_DURATION = 1000.0

    def test_single_span(self):
        events = list(
            generate_slider_events(
                self.START_TIME,
                self.SPAN_DURATION,
                1.0,
                self.SPAN_DURATION / 2.0,
                self.SPAN_DURATION,
                1,
            )
        )

        self.assertEqual(events[0].kind, SliderEventType.Head)
        self.assertAlmostEqual(events[0].time, self.START_TIME)

        self.assertEqual(events[1].kind, SliderEventType.Tick)
        self.assertAlmostEqual(events[1].time, self.SPAN_DURATION / 2.0)

        self.assertEqual(events[3].kind, SliderEventType.Tail)
        self.assertAlmostEqual(events[3].time, self.SPAN_DURATION)

    def test_repeat(self):
        events = list(
            generate_slider_events(
                self.START_TIME,
                self.SPAN_DURATION,
                1.0,
                self.SPAN_DURATION / 2.0,
                self.SPAN_DURATION,
                2,
            )
        )

        self.assertEqual(events[0].kind, SliderEventType.Head)
        self.assertAlmostEqual(events[0].time, self.START_TIME)

        self.assertEqual(events[1].kind, SliderEventType.Tick)
        self.assertAlmostEqual(events[1].time, self.SPAN_DURATION / 2.0)

        self.assertEqual(events[2].kind, SliderEventType.Repeat)
        self.assertAlmostEqual(events[2].time, self.SPAN_DURATION)

        self.assertEqual(events[3].kind, SliderEventType.Tick)
        self.assertAlmostEqual(
            events[3].time, self.SPAN_DURATION + self.SPAN_DURATION / 2.0
        )

        self.assertEqual(events[5].kind, SliderEventType.Tail)
        self.assertAlmostEqual(events[5].time, 2.0 * self.SPAN_DURATION)

    def test_non_even_ticks(self):
        events = list(
            generate_slider_events(
                self.START_TIME, self.SPAN_DURATION, 1.0, 300.0, self.SPAN_DURATION, 2
            )
        )

        self.assertEqual(events[0].kind, SliderEventType.Head)
        self.assertAlmostEqual(events[0].time, self.START_TIME)

        self.assertEqual(events[1].kind, SliderEventType.Tick)
        self.assertAlmostEqual(events[1].time, 300.0)

        self.assertEqual(events[2].kind, SliderEventType.Tick)
        self.assertAlmostEqual(events[2].time, 600.0)

        self.assertEqual(events[3].kind, SliderEventType.Tick)
        self.assertAlmostEqual(events[3].time, 900.0)

        self.assertEqual(events[4].kind, SliderEventType.Repeat)
        self.assertAlmostEqual(events[4].time, self.SPAN_DURATION)

        self.assertEqual(events[5].kind, SliderEventType.Tick)
        self.assertAlmostEqual(events[5].time, 1100.0)

        self.assertEqual(events[6].kind, SliderEventType.Tick)
        self.assertAlmostEqual(events[6].time, 1400.0)

        self.assertEqual(events[7].kind, SliderEventType.Tick)
        self.assertAlmostEqual(events[7].time, 1700.0)

        self.assertEqual(events[9].kind, SliderEventType.Tail)
        self.assertAlmostEqual(events[9].time, 2.0 * self.SPAN_DURATION)

    def test_last_tick_offset(self):
        events = list(
            generate_slider_events(
                self.START_TIME,
                self.SPAN_DURATION,
                1.0,
                self.SPAN_DURATION / 2.0,
                self.SPAN_DURATION,
                1,
            )
        )

        last_tick = events[2]
        self.assertEqual(last_tick.kind, SliderEventType.LastTick)
        self.assertAlmostEqual(last_tick.time, self.SPAN_DURATION - 36.0)

    def test_min_tick_dist(self):
        velocity = 5.0
        min_dist = velocity * 10.0

        events = list(
            generate_slider_events(
                self.START_TIME,
                self.SPAN_DURATION,
                velocity,
                velocity,
                self.SPAN_DURATION,
                2,
            )
        )

        for event in events:
            if event.kind == SliderEventType.Tick:
                self.assertTrue(
                    event.time < self.SPAN_DURATION - min_dist
                    or event.time > self.SPAN_DURATION + min_dist
                )


class TestSliderPath(unittest.TestCase):
    def test_slider_path_curve_caching(self):
        path = SliderPath(GameMode.Osu, [], None)

        curve1 = path.curve()
        curve2 = path.curve()

        self.assertIs(curve1, curve2)


class TestSection(unittest.TestCase):
    def test_finds_valid_sections(self):
        self.assertEqual(Section.try_from_line("[General]"), Section.General)
        self.assertEqual(Section.try_from_line("[Difficulty]"), Section.Difficulty)
        self.assertEqual(Section.try_from_line("[HitObjects]"), Section.HitObjects)

    def test_requires_brackets(self):
        self.assertIsNone(Section.try_from_line("General"))
        self.assertIsNone(Section.try_from_line("[General"))
        self.assertIsNone(Section.try_from_line("General]"))

    def test_denies_invalid_sections(self):
        self.assertIsNone(Section.try_from_line("abc"))
        self.assertIsNone(Section.try_from_line("HitObject"))


class TestFormatVersion(unittest.TestCase):
    def test_finds_version(self):
        line = "osu file format v42"
        self.assertEqual(try_version_from_line(line), 42)

    def test_fails_on_comment(self):
        line = "osu file format v42 // comment"
        with self.assertRaises(ParseBeatmapError):
            try_version_from_line(line)

    def test_fails_on_wrong_prefix(self):
        line = "file format v42 // comment"
        with self.assertRaises(UnknownFileFormatError):
            try_version_from_line(line)


if __name__ == "__main__":
    unittest.main()
