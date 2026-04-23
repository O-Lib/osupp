import unittest
from pathlib import Path

from osupp.Beatmap import Beatmap
from osupp.Beatmap.section.colors import Color

# from osupp.Beatmap.section.difficulty import Difficulty
from osupp.Beatmap.section.events import BreakPeriod  # , Events
from osupp.Beatmap.section.general import CountdownType, GameMode
from osupp.Beatmap.section.hit_objects import (
    HitObjectCircle,
    HitObjectSlider,
    SplineType,
)
from osupp.Beatmap.section.hit_objects.hit_samples import HitSampleInfo, SampleBank
from osupp.Beatmap.section.hit_objects.slider import CurveBuffers
from osupp.Beatmap.section.timing_points import (
    DifficultyPoint,
    EffectPoint,
    SamplePoint,
    TimeSignature,
    TimingPoint,
)
from osupp.Beatmap.utils.pos import Pos


def get_renatus_path():
    resources_dir = Path("./resources")
    if not resources_dir.exists():
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
    return resources_dir / "Soleily - Renatus (Gamu) [Insane].osu"


class TestDecode(unittest.TestCase):
    def test_format_version(self):
        resources_dir = Path("./resources")
        if not resources_dir.exists():
            resources_dir = Path(__file__).parent.parent.parent.parent / "resources"

        path = resources_dir / "beatmap-version-4.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)

        self.assertEqual(map_obj.format_version, 4)
        self.assertEqual(map_obj.preview_time, -1)

    def test_general(self):
        path = get_renatus_path()
        if not path.exists():
            self.skipTest(f"File {path} not found")

        content = path.read_text(encoding="utf-8")
        map_obj = Beatmap.from_str(content)

        self.assertEqual(map_obj.audio_file, "03. Renatus - Soleily 192kbps.mp3")
        self.assertEqual(map_obj.audio_lead_in, 0.0)
        self.assertEqual(map_obj.preview_time, 164471)
        self.assertEqual(map_obj.stack_leniency, 0.7)
        self.assertEqual(map_obj.mode, GameMode.Osu)
        self.assertEqual(map_obj.letterbox_in_breaks, False)
        self.assertEqual(map_obj.special_style, False)
        self.assertEqual(map_obj.widescreen_storyboard, False)
        self.assertEqual(map_obj.samples_match_playback_rate, False)
        self.assertEqual(map_obj.countdown, CountdownType.None_)
        self.assertEqual(map_obj.countdown_offset, 0)

    def test_editor(self):
        path = get_renatus_path()
        if not path.exists():
            self.skipTest(f"File {path} not found")

        content = path.read_text(encoding="utf-8")
        map_obj = Beatmap.from_str(content)

        expected_bookmarks = [
            11505,
            22054,
            32604,
            43153,
            53703,
            64252,
            74802,
            85351,
            95901,
            106450,
            116999,
            119637,
            130186,
            140735,
            151285,
            161834,
            164471,
            175020,
            185570,
            196119,
            206669,
            209306,
        ]

        self.assertEqual(map_obj.bookmarks, expected_bookmarks)
        self.assertEqual(map_obj.distance_spacing, 1.8)
        self.assertEqual(map_obj.beat_divisor, 4)
        self.assertEqual(map_obj.grid_size, 4)
        self.assertEqual(map_obj.timeline_zoom, 2.0)

    def test_metadata(self):
        path = get_renatus_path()
        if not path.exists():
            self.skipTest(f"File {path} not found")

        content = path.read_text(encoding="utf-8")
        map_obj = Beatmap.from_str(content)

        self.assertEqual(map_obj.title, "Renatus")
        self.assertEqual(map_obj.title_unicode, "Renatus")
        self.assertEqual(map_obj.artist, "Soleily")
        self.assertEqual(map_obj.artist_unicode, "Soleily")
        self.assertEqual(map_obj.creator, "Gamu")
        self.assertEqual(map_obj.version, "Insane")
        self.assertEqual(map_obj.source, "")
        self.assertEqual(map_obj.tags, "MBC7 Unisphere 地球ヤバイEP Chikyu Yabai")
        self.assertEqual(map_obj.beatmap_id, 557821)
        self.assertEqual(map_obj.beatmap_set_id, 241526)

    def test_difficulty(self):
        path = get_renatus_path()
        if not path.exists():
            self.skipTest(f"File {path} not found")

        content = path.read_text(encoding="utf-8")
        map_obj = Beatmap.from_str(content)

        self.assertEqual(map_obj.hp_drain_rate, 6.5)
        self.assertEqual(map_obj.circle_size, 4.0)
        self.assertEqual(map_obj.overall_difficulty, 8.0)
        self.assertEqual(map_obj.approach_rate, 9.0)
        self.assertEqual(map_obj.slider_multiplier, 1.8)
        self.assertEqual(map_obj.slider_tick_rate, 2.0)

    def test_events(self):
        path = get_renatus_path()
        if not path.exists():
            self.skipTest(f"File {path} not found")

        content = path.read_text(encoding="utf-8")
        map_obj = Beatmap.from_str(content)

        break_period = BreakPeriod(
            start_time=122474.0,
            end_time=140135.0,
        )

        self.assertEqual(map_obj.background_file, "machinetop_background.jpg")
        self.assertEqual(map_obj.breaks[0], break_period)
        self.assertTrue(map_obj.breaks[0].has_effect())

    def test_video_lowercase_ext(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "video-with-lowercase-extension.osb"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        self.assertEqual(map_obj.background_file, "BG.jpg")

    def test_video_uppercase_ext(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "video-with-uppercase-extension.osb"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        self.assertEqual(map_obj.background_file, "BG.jpg")

    def test_image_as_video(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "image-specified-as-video.osb"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        self.assertEqual(map_obj.background_file, "BG.jpg")

    def test_timing_points(self):
        path = get_renatus_path()
        if not path.exists():
            self.skipTest(f"File {path} not found")

        content = path.read_text(encoding="utf-8")
        map_obj = Beatmap.from_str(content)
        control_points = map_obj.control_points

        self.assertEqual(len(control_points.timing_points), 4)
        self.assertEqual(len(control_points.difficulty_points), 5)
        self.assertEqual(len(control_points.sample_points), 34)
        self.assertEqual(len(control_points.effect_points), 8)

        # Timing Points
        tp = control_points.timing_point_at(0.0) or TimingPoint.default()
        self.assertEqual(tp.time, 956.0)
        self.assertAlmostEqual(tp.beat_len, 329.67032967033, places=10)
        self.assertEqual(tp.time_signature, TimeSignature.new_simple_quadruple())
        self.assertEqual(tp.omit_first_bar_line, False)

        tp = control_points.timing_point_at(48428.0) or TimingPoint.default()
        self.assertEqual(tp.time, 956.0)
        self.assertAlmostEqual(tp.beat_len, 329.67032967033, places=10)
        self.assertEqual(tp.time_signature, TimeSignature.new_simple_quadruple())
        self.assertEqual(tp.omit_first_bar_line, False)

        tp = control_points.timing_point_at(119637.0) or TimingPoint.default()
        self.assertEqual(tp.time, 119637.0)
        self.assertAlmostEqual(tp.beat_len, 659.340659340659, places=10)
        self.assertEqual(tp.time_signature, TimeSignature.new_simple_quadruple())
        self.assertEqual(tp.omit_first_bar_line, False)

        # Difficulty Points
        dp = control_points.difficulty_point_at(0.0) or DifficultyPoint.default()
        self.assertEqual(dp.time, 0.0)
        self.assertEqual(dp.slider_velocity, 1.0)

        dp = control_points.difficulty_point_at(48428.0) or DifficultyPoint.default()
        self.assertEqual(dp.time, 0.0)
        self.assertEqual(dp.slider_velocity, 1.0)

        dp = control_points.difficulty_point_at(116999.0) or DifficultyPoint.default()
        self.assertEqual(dp.time, 116999.0)
        self.assertAlmostEqual(dp.slider_velocity, 0.75, delta=0.1)

        # Sample Points
        sp = control_points.sample_point_at(0.0) or SamplePoint.default()
        self.assertEqual(sp.time, 956.0)
        self.assertEqual(sp.sample_bank, SampleBank.SOFT)
        self.assertEqual(sp.sample_volume, 60)

        sp = control_points.sample_point_at(53373.0) or SamplePoint.default()
        self.assertEqual(sp.time, 53373.0)
        self.assertEqual(sp.sample_bank, SampleBank.SOFT)
        self.assertEqual(sp.sample_volume, 60)

        sp = control_points.sample_point_at(119637.0) or SamplePoint.default()
        self.assertEqual(sp.time, 119637.0)
        self.assertEqual(sp.sample_bank, SampleBank.SOFT)
        self.assertEqual(sp.sample_volume, 80)

        # Effect Points
        ep = control_points.effect_point_at(0.0) or EffectPoint.default()
        self.assertEqual(ep.time, 0.0)
        self.assertEqual(ep.kiai, False)

        ep = control_points.effect_point_at(53703.0) or EffectPoint.default()
        self.assertEqual(ep.time, 53703.0)
        self.assertEqual(ep.kiai, True)

        ep = control_points.effect_point_at(116637.0) or EffectPoint.default()
        self.assertEqual(ep.time, 95901.0)
        self.assertEqual(ep.kiai, False)

    def test_overlapping_timing_points(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "overlapping-control-points.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        control_points = map_obj.control_points

        self.assertEqual(len(control_points.timing_points), 4)
        self.assertEqual(len(control_points.difficulty_points), 3)
        self.assertEqual(len(control_points.effect_points), 3)
        self.assertEqual(len(control_points.sample_points), 3)

        def slider_velocity_at(time):
            p = control_points.difficulty_point_at(time)
            return p.slider_velocity if p else DifficultyPoint.DEFAULT_SLIDER_VELOCITY

        def kiai_at(time):
            p = control_points.effect_point_at(time)
            return p.kiai if p else EffectPoint.DEFAULT_KIAI

        def sample_bank_at(time):
            p = control_points.sample_point_at(time)
            return p.sample_bank if p else SamplePoint.DEFAULT_SAMPLE_BANK

        def beat_len_at(time):
            p = control_points.timing_point_at(time)
            return p.beat_len if p else TimingPoint.DEFAULT_BEAT_LEN

        # Velocity
        self.assertAlmostEqual(slider_velocity_at(500.0), 1.5, delta=0.1)
        self.assertAlmostEqual(slider_velocity_at(1500.0), 1.5, delta=0.1)
        self.assertAlmostEqual(slider_velocity_at(2500.0), 0.75, delta=0.1)
        self.assertAlmostEqual(slider_velocity_at(3500.0), 1.5, delta=0.1)

        # Kiai
        self.assertEqual(kiai_at(500.0), True)
        self.assertEqual(kiai_at(1500.0), True)
        self.assertEqual(kiai_at(2500.0), False)
        self.assertEqual(kiai_at(3500.0), True)

        # Sample Bank
        self.assertEqual(sample_bank_at(500.0), SampleBank.DRUM)
        self.assertEqual(sample_bank_at(1500.0), SampleBank.DRUM)
        self.assertEqual(sample_bank_at(2500.0), SampleBank.NORMAL)
        self.assertEqual(sample_bank_at(3500.0), SampleBank.DRUM)

        # Beat Len
        self.assertAlmostEqual(beat_len_at(500.0), 500.0, delta=0.1)
        self.assertAlmostEqual(beat_len_at(1500.0), 500.0, delta=0.1)
        self.assertAlmostEqual(beat_len_at(2500.0), 250.0, delta=0.1)
        self.assertAlmostEqual(beat_len_at(3500.0), 500.0, delta=0.1)

    def test_omit_bar_line_effect(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "omit-barline-control-points.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        control_points = map_obj.control_points

        self.assertEqual(len(control_points.timing_points), 6)
        self.assertEqual(len(control_points.effect_points), 0)

        def omit_first_bar_line_at(time):
            p = control_points.timing_point_at(time)
            return (
                p.omit_first_bar_line if p else TimingPoint.DEFAULT_OMIT_FIRST_BAR_LINE
            )

        self.assertEqual(omit_first_bar_line_at(500.0), False)
        self.assertEqual(omit_first_bar_line_at(1500.0), True)
        self.assertEqual(omit_first_bar_line_at(2500.0), False)
        self.assertEqual(omit_first_bar_line_at(3500.0), False)
        self.assertEqual(omit_first_bar_line_at(4500.0), False)
        self.assertEqual(omit_first_bar_line_at(5500.0), True)

    def test_timing_point_resets_speed_multiplier(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "timingpoint-speedmultiplier-reset.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        control_points = map_obj.control_points

        def slider_velocity_at(time):
            p = control_points.difficulty_point_at(time)
            return p.slider_velocity if p else DifficultyPoint.DEFAULT_SLIDER_VELOCITY

        self.assertAlmostEqual(slider_velocity_at(0.0), 0.5, delta=0.1)
        self.assertAlmostEqual(slider_velocity_at(2000.0), 1.0, delta=0.1)

    def test_colors(self):
        path = get_renatus_path()
        if not path.exists():
            self.skipTest(f"File {path} not found")

        content = path.read_text(encoding="utf-8")
        map_obj = Beatmap.from_str(content)

        expected_colors = [
            Color.new(142, 199, 255, 255),
            Color.new(255, 128, 128, 255),
            Color.new(128, 255, 128, 255),
            Color.new(128, 255, 255, 255),
            Color.new(255, 187, 255, 255),
            Color.new(255, 177, 140, 255),
            Color.new(100, 100, 100, 255),
        ]

        self.assertEqual(map_obj.custom_combo_colors, expected_colors)

    def test_get_last_object_time(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "mania-last-object-not-latest.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        hit_objects = map_obj.hit_objects

        last_object = hit_objects[-1]

        self.assertEqual(last_object.start_time, 2494.0)
        self.assertEqual(last_object.end_time(), 2494.0)

        max_end_time = 0.0
        for h in hit_objects:
            max_end_time = max(max_end_time, h.end_time())

        self.assertEqual(max_end_time, 2582.0)

    def test_hit_objects(self):
        path = get_renatus_path()
        if not path.exists():
            self.skipTest(f"File {path} not found")

        content = path.read_text(encoding="utf-8")
        map_obj = Beatmap.from_str(content)
        hit_objects = map_obj.hit_objects

        # Test 0: Slider
        self.assertEqual(hit_objects[0].start_time, 956.0)

        has_normal = Any(
            sample.name == HitSampleInfo.HIT_NORMAL for sample in hit_objects[0].samples
        )
        self.assertTrue(has_normal)

        slider = hit_objects[0].kind
        self.assertIsInstance(slider, HitObjectSlider)
        self.assertEqual(slider.pos, Pos.new(192.0, 168.0))

        # Test 1: Circle
        self.assertEqual(hit_objects[1].start_time, 1285.0)

        has_clap = Any(
            sample.name == HitSampleInfo.HIT_CLAP for sample in hit_objects[1].samples
        )
        self.assertTrue(has_clap)

        circle = hit_objects[1].kind
        self.assertIsInstance(circle, HitObjectCircle)
        self.assertEqual(circle.pos, Pos.new(304.0, 56.0))

    def test_control_point_difficulty_change(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "controlpoint-difficulty-multiplier.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        control_points = map_obj.control_points

        def slider_velocity_at(time):
            p = control_points.difficulty_point_at(time)
            return p.slider_velocity if p else DifficultyPoint.DEFAULT_SLIDER_VELOCITY

        self.assertEqual(slider_velocity_at(5.0), 1.0)
        self.assertEqual(slider_velocity_at(1000.0), 10.0)
        self.assertEqual(slider_velocity_at(2000.0), 1.8518518518518519)
        self.assertEqual(slider_velocity_at(3000.0), 0.5)

    def test_control_point_custom_sample_bank(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "controlpoint-custom-samplebank.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        hit_objects = map_obj.hit_objects

        def assert_lookup_name(hit_obj, name):
            self.assertEqual(str(hit_obj.samples[0].lookup_name()), name)

        assert_lookup_name(hit_objects[0], "Gameplay/Normal-hitnormal")
        assert_lookup_name(hit_objects[1], "Gameplay/Normal-hitnormal")
        assert_lookup_name(hit_objects[2], "Gameplay/Normal-hitnormal2")
        assert_lookup_name(hit_objects[3], "Gameplay/Normal-hitnormal")
        assert_lookup_name(hit_objects[4], "Gameplay/Soft-hitnormal8")

    def test_hit_object_custom_sample_bank(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "hitobject-custom-samplebank.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        hit_objects = map_obj.hit_objects

        def assert_lookup_name(hit_obj, name):
            self.assertEqual(str(hit_obj.samples[0].lookup_name()), name)

        assert_lookup_name(hit_objects[0], "Gameplay/Normal-hitnormal")
        assert_lookup_name(hit_objects[1], "Gameplay/Normal-hitnormal2")
        assert_lookup_name(hit_objects[2], "Gameplay/Normal-hitnormal3")

    def test_hit_object_file_samples(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "hitobject-file-samples.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        hit_objects = map_obj.hit_objects

        def assert_lookup_name(hit_obj, name):
            self.assertEqual(str(hit_obj.samples[0].lookup_name()), name)

        assert_lookup_name(hit_objects[0], "hit_1.wav")
        assert_lookup_name(hit_objects[1], "hit_2.wav")
        assert_lookup_name(hit_objects[2], "Gameplay/Normal-hitnormal2")
        assert_lookup_name(hit_objects[3], "hit_1.wav")
        self.assertEqual(hit_objects[3].samples[0].volume, 70)

    def test_slider_samples(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "slider-samples.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        hit_objects = map_obj.hit_objects

        slider1 = hit_objects[0].kind
        slider2 = hit_objects[1].kind
        slider3 = hit_objects[2].kind

        # Slider 1
        self.assertEqual(len(slider1.node_samples[0]), 1)
        self.assertEqual(slider1.node_samples[0][0].name, HitSampleInfo.HIT_NORMAL)
        self.assertEqual(len(slider1.node_samples[1]), 1)
        self.assertEqual(slider1.node_samples[1][0].name, HitSampleInfo.HIT_NORMAL)
        self.assertEqual(len(slider1.node_samples[2]), 1)
        self.assertEqual(slider1.node_samples[2][0].name, HitSampleInfo.HIT_NORMAL)

        # Slider 2
        self.assertEqual(len(slider2.node_samples[0]), 2)
        self.assertEqual(slider2.node_samples[0][0].name, HitSampleInfo.HIT_NORMAL)
        self.assertEqual(slider2.node_samples[0][1].name, HitSampleInfo.HIT_CLAP)
        self.assertEqual(len(slider2.node_samples[1]), 2)
        self.assertEqual(slider2.node_samples[1][0].name, HitSampleInfo.HIT_NORMAL)
        self.assertEqual(slider2.node_samples[1][1].name, HitSampleInfo.HIT_CLAP)
        self.assertEqual(len(slider2.node_samples[2]), 2)
        self.assertEqual(slider2.node_samples[2][0].name, HitSampleInfo.HIT_NORMAL)
        self.assertEqual(slider2.node_samples[2][1].name, HitSampleInfo.HIT_CLAP)

        # Slider 3
        self.assertEqual(len(slider3.node_samples[0]), 2)
        self.assertEqual(slider3.node_samples[0][0].name, HitSampleInfo.HIT_NORMAL)
        self.assertEqual(slider3.node_samples[0][1].name, HitSampleInfo.HIT_WHISTLE)
        self.assertEqual(len(slider3.node_samples[1]), 1)
        self.assertEqual(slider3.node_samples[1][0].name, HitSampleInfo.HIT_NORMAL)
        self.assertEqual(len(slider3.node_samples[2]), 2)
        self.assertEqual(slider3.node_samples[2][0].name, HitSampleInfo.HIT_NORMAL)
        self.assertEqual(slider3.node_samples[2][1].name, HitSampleInfo.HIT_CLAP)

    def test_hit_object_no_addition_bank(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "hitobject-no-addition-bank.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        hit_objects = map_obj.hit_objects

        self.assertEqual(hit_objects[0].samples[0].bank, hit_objects[0].samples[1].bank)

    def test_invalid_event_pass(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "invalid-events.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        # Just ensuring it doesn't raise an exception during decoding
        Beatmap.from_path(path)

    def test_invalid_bank_defaults_to_normal(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "invalid-bank.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        hit_objects = map_obj.hit_objects

        def assert_object_has_banks(h, normal_bank, additions_bank=None):
            self.assertEqual(h.samples[0].bank, normal_bank)
            if additions_bank is not None:
                self.assertEqual(h.samples[1].bank, additions_bank)

        assert_object_has_banks(hit_objects[0], SampleBank.DRUM, None)
        assert_object_has_banks(hit_objects[1], SampleBank.NORMAL, None)
        assert_object_has_banks(hit_objects[2], SampleBank.SOFT, None)
        assert_object_has_banks(hit_objects[3], SampleBank.DRUM, None)
        assert_object_has_banks(hit_objects[4], SampleBank.NORMAL, None)

        assert_object_has_banks(hit_objects[5], SampleBank.DRUM, SampleBank.DRUM)
        assert_object_has_banks(hit_objects[6], SampleBank.DRUM, SampleBank.NORMAL)
        assert_object_has_banks(hit_objects[7], SampleBank.DRUM, SampleBank.SOFT)
        assert_object_has_banks(hit_objects[8], SampleBank.DRUM, SampleBank.DRUM)
        assert_object_has_banks(hit_objects[9], SampleBank.DRUM, SampleBank.NORMAL)

    def test_corrupted_header(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "corrupted-header.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        self.assertEqual(map_obj.title, "Beatmap with corrupted header")
        self.assertEqual(map_obj.creator, "Evil Hacker")

    def test_missing_header(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "missing-header.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        self.assertEqual(map_obj.title, "Beatmap with no header")
        self.assertEqual(map_obj.creator, "Incredibly Evil Hacker")

    def test_empty_lines_at_start(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "empty-lines-at-start.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        self.assertEqual(map_obj.title, "Empty lines at start")
        self.assertEqual(map_obj.creator, "Edge Case Hunter")

    def test_empty_lines_without_header(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "empty-line-instead-of-header.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        self.assertEqual(map_obj.title, "The dog ate the file header")
        self.assertEqual(map_obj.creator, "Why does this keep happening")

    def test_no_blank_after_header(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "no-empty-line-after-header.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        self.assertEqual(map_obj.title, "No empty line delimiting header from contents")
        self.assertEqual(map_obj.creator, "Edge Case Hunter")

    def test_empty_file(self):
        self.assertEqual(Beatmap.from_bytes(b""), Beatmap.default())

    def test_multi_segment_sliders(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "multi-segment-slider.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        hit_objects = map_obj.hit_objects

        # Slider 0
        slider = hit_objects[0].kind
        self.assertIsInstance(slider, HitObjectSlider)
        first = slider.path.control_points

        self.assertEqual(first[0].pos, Pos.new(0.0, 0.0))
        self.assertEqual(first[0].path_type.kind, SplineType.PerfectCurve)
        self.assertEqual(first[1].pos, Pos.new(161.0, -244.0))
        self.assertIsNone(first[1].path_type)

        self.assertEqual(first[2].pos, Pos.new(376.0, -3.0))
        self.assertEqual(first[2].path_type.kind, SplineType.BSpline)
        self.assertEqual(first[3].pos, Pos.new(68.0, 15.0))
        self.assertIsNone(first[3].path_type)
        self.assertEqual(first[4].pos, Pos.new(259.0, -132.0))
        self.assertIsNone(first[4].path_type)
        self.assertEqual(first[5].pos, Pos.new(92.0, -107.0))
        self.assertIsNone(first[5].path_type)

        # Slider 1
        slider = hit_objects[1].kind
        self.assertIsInstance(slider, HitObjectSlider)
        second = slider.path.control_points

        self.assertEqual(second[0].pos, Pos.new(0.0, 0.0))
        self.assertEqual(second[0].path_type.kind, SplineType.PerfectCurve)
        self.assertEqual(second[1].pos, Pos.new(161.0, -244.0))
        self.assertIsNone(second[1].path_type)
        self.assertEqual(second[2].pos, Pos.new(376.0, -3.0))
        self.assertIsNone(second[2].path_type)

        # Slider 2
        slider = hit_objects[2].kind
        self.assertIsInstance(slider, HitObjectSlider)
        third = slider.path.control_points

        self.assertEqual(third[0].pos, Pos.new(0.0, 0.0))
        self.assertEqual(third[0].path_type.kind, SplineType.BSpline)
        self.assertEqual(third[1].pos, Pos.new(0.0, 192.0))
        self.assertIsNone(third[1].path_type)
        self.assertEqual(third[2].pos, Pos.new(224.0, 192.0))
        self.assertIsNone(third[2].path_type)

        self.assertEqual(third[3].pos, Pos.new(224.0, 0.0))
        self.assertEqual(third[3].path_type.kind, SplineType.BSpline)
        self.assertEqual(third[4].pos, Pos.new(224.0, -192.0))
        self.assertIsNone(third[4].path_type)
        self.assertEqual(third[5].pos, Pos.new(480.0, -192.0))
        self.assertIsNone(third[5].path_type)
        self.assertEqual(third[6].pos, Pos.new(480.0, 0.0))
        self.assertIsNone(third[6].path_type)

        # Slider 3
        slider = hit_objects[3].kind
        self.assertIsInstance(slider, HitObjectSlider)
        fourth = slider.path.control_points

        self.assertEqual(fourth[0].pos, Pos.new(0.0, 0.0))
        self.assertEqual(fourth[0].path_type.kind, SplineType.BSpline)
        self.assertEqual(fourth[1].pos, Pos.new(1.0, 1.0))
        self.assertIsNone(fourth[1].path_type)
        self.assertEqual(fourth[2].pos, Pos.new(2.0, 2.0))
        self.assertIsNone(fourth[2].path_type)
        self.assertEqual(fourth[3].pos, Pos.new(3.0, 3.0))
        self.assertIsNone(fourth[3].path_type)
        self.assertEqual(fourth[4].pos, Pos.new(3.0, 3.0))
        self.assertIsNone(fourth[4].path_type)

        # Slider 4
        slider = hit_objects[4].kind
        self.assertIsInstance(slider, HitObjectSlider)
        fifth = slider.path.control_points

        self.assertEqual(fifth[0].pos, Pos.new(0.0, 0.0))
        self.assertEqual(fifth[0].path_type.kind, SplineType.BSpline)
        self.assertEqual(fifth[1].pos, Pos.new(1.0, 1.0))
        self.assertIsNone(fifth[1].path_type)
        self.assertEqual(fifth[2].pos, Pos.new(2.0, 2.0))
        self.assertIsNone(fifth[2].path_type)
        self.assertEqual(fifth[3].pos, Pos.new(3.0, 3.0))
        self.assertIsNone(fifth[3].path_type)
        self.assertEqual(fifth[4].pos, Pos.new(3.0, 3.0))
        self.assertIsNone(fifth[4].path_type)

        self.assertEqual(fifth[5].pos, Pos.new(4.0, 4.0))
        self.assertEqual(fifth[5].path_type.kind, SplineType.BSpline)
        self.assertEqual(fifth[6].pos, Pos.new(5.0, 5.0))
        self.assertIsNone(fifth[6].path_type)

        # Slider 5
        slider = hit_objects[5].kind
        self.assertIsInstance(slider, HitObjectSlider)
        sixth = slider.path.control_points

        self.assertEqual(sixth[0].pos, Pos.new(0.0, 0.0))
        self.assertEqual(sixth[0].path_type.kind, SplineType.BSpline)
        self.assertEqual(sixth[1].pos, Pos.new(75.0, 145.0))
        self.assertIsNone(sixth[1].path_type)

        self.assertEqual(sixth[2].pos, Pos.new(170.0, 75.0))
        self.assertEqual(sixth[2].path_type.kind, SplineType.BSpline)
        self.assertEqual(sixth[3].pos, Pos.new(300.0, 145.0))
        self.assertIsNone(sixth[3].path_type)
        self.assertEqual(sixth[4].pos, Pos.new(410.0, 20.0))
        self.assertIsNone(sixth[4].path_type)

        # Slider 6
        slider = hit_objects[6].kind
        self.assertIsInstance(slider, HitObjectSlider)
        seventh = slider.path.control_points

        self.assertEqual(seventh[0].pos, Pos.new(0.0, 0.0))
        self.assertEqual(seventh[0].path_type.kind, SplineType.PerfectCurve)
        self.assertEqual(seventh[1].pos, Pos.new(75.0, 145.0))
        self.assertIsNone(seventh[1].path_type)

        self.assertEqual(seventh[2].pos, Pos.new(170.0, 75.0))
        self.assertEqual(seventh[2].path_type.kind, SplineType.PerfectCurve)
        self.assertEqual(seventh[3].pos, Pos.new(300.0, 145.0))
        self.assertIsNone(seventh[3].path_type)
        self.assertEqual(seventh[4].pos, Pos.new(410.0, 20.0))
        self.assertIsNone(seventh[4].path_type)

    def test_slider_len_extension_edge_case(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "duplicate-last-position-slider.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        hit_objects = map_obj.hit_objects
        slider = hit_objects[0].kind
        self.assertIsInstance(slider, HitObjectSlider)

        # No seu código SliderPath.expected_dist é Optional[float]
        self.assertEqual(slider.path.expected_dist, 2.0)

        bufs = CurveBuffers()
        curve = slider.path.borrowed_curve(bufs)
        self.assertEqual(curve.dist(), 1.0)

    def test_undefined_ar_inherits_od(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "undefined-approach-rate.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        self.assertEqual(map_obj.approach_rate, 1.0)
        self.assertEqual(map_obj.overall_difficulty, 1.0)

    def test_ar_before_od(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "approach-rate-before-overall-difficulty.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        self.assertEqual(map_obj.approach_rate, 9.0)
        self.assertEqual(map_obj.overall_difficulty, 1.0)

    def test_ar_after_od(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "approach-rate-after-overall-difficulty.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        self.assertEqual(map_obj.approach_rate, 9.0)
        self.assertEqual(map_obj.overall_difficulty, 1.0)

    def test_adjacent_implicit_catmull_segments_merged(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "adjacent-catmull-segments.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        hit_objects = map_obj.hit_objects

        slider = hit_objects[0].kind
        self.assertIsInstance(slider, HitObjectSlider)

        # Em Python, control_points é uma lista mutável
        control_points = slider.path.control_points

        self.assertEqual(len(control_points), 6)

        # Filtrar os pontos que têm path_type definido
        # Criamos uma nova lista com os pontos filtrados
        filtered_control_points = [
            point for point in control_points if point.path_type is not None
        ]

        self.assertEqual(len(filtered_control_points), 1)
        self.assertEqual(filtered_control_points[0].path_type.kind, SplineType.Catmull)

    def test_duplicate_initial_catmull_point_merged(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "catmull-duplicate-initial-controlpoint.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        hit_objects = map_obj.hit_objects

        slider = hit_objects[0].kind
        self.assertIsInstance(slider, HitObjectSlider)

        control_points = slider.path.control_points

        self.assertEqual(len(control_points), 4)
        self.assertEqual(control_points[0].path_type.kind, SplineType.Catmull)
        self.assertEqual(control_points[0].pos, Pos.new(0.0, 0.0))
        self.assertIsNone(control_points[1].path_type)
        self.assertNotEqual(control_points[1].pos, Pos.new(0.0, 0.0))

    def test_nan_control_points(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "nan-control-points.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        control_points = map_obj.control_points

        self.assertEqual(len(control_points.timing_points), 1)
        self.assertEqual(len(control_points.difficulty_points), 2)

        def beat_len_at(time):
            p = control_points.timing_point_at(time)
            return p.beat_len if p else TimingPoint.DEFAULT_BEAT_LEN

        def slider_velocity_at(time):
            p = control_points.difficulty_point_at(time)
            return p.slider_velocity if p else DifficultyPoint.DEFAULT_SLIDER_VELOCITY

        def generate_ticks_at(time):
            p = control_points.difficulty_point_at(time)
            return p.generate_ticks if p else DifficultyPoint.DEFAULT_GENERATE_TICKS

        self.assertEqual(beat_len_at(1000.0), 500.0)

        self.assertEqual(slider_velocity_at(2000.0), 1.0)
        self.assertEqual(slider_velocity_at(3000.0), 1.0)

        self.assertEqual(generate_ticks_at(2000.0), False)
        self.assertEqual(generate_ticks_at(3000.0), True)

    def test_sample_point_leniency(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "sample-point-leniency.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        hit_objects = map_obj.hit_objects

        self.assertEqual(len(hit_objects), 1)
        hit_object = hit_objects[0]

        for sample in hit_object.samples:
            self.assertEqual(sample.volume, 70)

    def test_new_combo_after_break(self):
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources"
        path = resources_dir / "break-between-objects.osu"
        if not path.exists():
            self.skipTest(f"File {path} not found")

        map_obj = Beatmap.from_path(path)
        hit_objects = map_obj.hit_objects

        self.assertTrue(hit_objects[0].new_combo)
        self.assertTrue(hit_objects[1].new_combo)
        self.assertFalse(hit_objects[2].new_combo)


if __name__ == "__main__":
    unittest.main()
