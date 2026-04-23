import unittest
from pathlib import Path

from osupp.Beatmap import Beatmap
from osupp.Beatmap.section.general import GameMode
from osupp.Beatmap.section.hit_objects import (
    HitObject,
    HitObjectSlider,
    PathControlPoint,
    PathType,
    SliderPath,
    SplineType,
)
from osupp.Beatmap.utils.pos import Pos


class TestEncode(unittest.TestCase):
    def test_stability(self):
        resources_dir = Path("./resources")
        if not resources_dir.exists():
            # If running from a different directory, try to find it
            resources_dir = Path(__file__).parent.parent.parent.parent / "resources"

        if not resources_dir.exists():
            self.skipTest("Resources directory not found")

        for entry in resources_dir.iterdir():
            if not entry.is_file():
                continue

            filename = entry.name
            if not (filename.endswith(".osu") or filename.endswith(".osb")):
                continue

            try:
                decoded = Beatmap.from_path(entry)
            except Exception as e:
                self.fail(f"Failed to decode beatmap {filename!r}: {e}")

            try:
                # Assuming encode() will be implemented in Beatmap class
                encoded_data = decoded.encode()
                if isinstance(encoded_data, str):
                    encoded_bytes = encoded_data.encode("utf-8")
                else:
                    encoded_bytes = encoded_data
            except Exception as e:
                self.fail(f"Failed to encode beatmap {filename!r}: {e}")

            try:
                decoded_after_encode = Beatmap.from_bytes(encoded_bytes)
            except Exception as e:
                self.fail(f"Failed to decode beatmap after encoding {filename!r}: {e}")

            self._assert_eq_list(
                decoded.control_points.timing_points,
                decoded_after_encode.control_points.timing_points,
                filename,
            )
            self._assert_eq_list(
                decoded.control_points.effect_points,
                decoded_after_encode.control_points.effect_points,
                filename,
            )
            self._assert_eq_list(
                decoded.hit_objects,
                decoded_after_encode.hit_objects,
                filename,
            )

            self.assertEqual(
                decoded.custom_colors,
                decoded_after_encode.custom_colors,
                f"{filename!r}",
            )
            self.assertEqual(
                decoded.custom_combo_colors,
                decoded_after_encode.custom_combo_colors,
                f"{filename!r}",
            )

    def test_bspline_curve_type(self):
        control_points = [
            PathControlPoint(
                pos=Pos.new(0.0, 0.0),
                path_type=PathType.new_b_spline(3),
            ),
            PathControlPoint(
                pos=Pos.new(50.0, 50.0),
                path_type=None,
            ),
            PathControlPoint(
                pos=Pos.new(100.0, 100.0),
                path_type=PathType.new_b_spline(3),
            ),
            PathControlPoint(
                pos=Pos.new(150.0, 150.0),
                path_type=None,
            ),
        ]

        path = SliderPath.new(GameMode.Taiko, control_points, None)

        slider = HitObjectSlider(
            pos=Pos.new(0.0, 0.0),
            new_combo=False,
            combo_offset=0,
            path=path,
            node_samples=[],
            repeat_count=0,
            velocity=0.0,
        )

        hit_object = HitObject(
            start_time=0.0,
            kind=slider,
            samples=[],
        )

        map_obj = Beatmap.default()
        map_obj.hit_objects = [hit_object]

        encoded_data = map_obj.encode()
        if isinstance(encoded_data, str):
            encoded_bytes = encoded_data.encode("utf-8")
        else:
            encoded_bytes = encoded_data

        decoded_after_encode = Beatmap.from_bytes(encoded_bytes)

        expected = map_obj.hit_objects[0].kind
        actual = decoded_after_encode.hit_objects[0].kind

        self.assertEqual(len(actual.path.control_points), 4)
        self.assertEqual(expected.path.control_points, actual.path.control_points)

    def test_multi_segment_slider_with_floating_point_error(self):
        control_points = [
            PathControlPoint(
                pos=Pos.new(0.0, 0.0),
                path_type=PathType(SplineType.BSpline),
            ),
            PathControlPoint(
                pos=Pos.new(0.5, 0.5),
                path_type=None,
            ),
            PathControlPoint(
                pos=Pos.new(0.51, 0.51),
                path_type=None,
            ),
            PathControlPoint(
                pos=Pos.new(1.0, 1.0),
                path_type=PathType(SplineType.BSpline),
            ),
            PathControlPoint(
                pos=Pos.new(2.0, 2.0),
                path_type=None,
            ),
        ]

        path = SliderPath.new(GameMode.Taiko, control_points, None)

        slider = HitObjectSlider(
            pos=Pos.new(0.6, 0.6),
            new_combo=False,
            combo_offset=0,
            path=path,
            node_samples=[],
            repeat_count=0,
            velocity=0.0,
        )

        hit_object = HitObject(
            start_time=0.0,
            kind=slider,
            samples=[],
        )

        map_obj = Beatmap.default()
        map_obj.hit_objects = [hit_object]

        encoded_data = map_obj.encode()
        if isinstance(encoded_data, str):
            encoded_bytes = encoded_data.encode("utf-8")
        else:
            encoded_bytes = encoded_data

        decoded_after_encode = Beatmap.from_bytes(encoded_bytes)

        decoded_slider = decoded_after_encode.hit_objects[0].kind
        self.assertEqual(len(decoded_slider.path.control_points), 5)

    def _assert_eq_list(self, expected, actual, filename):
        min_len = min(len(expected), len(actual))
        for idx in range(min_len):
            a, b = expected[idx], actual[idx]
            if a != b:
                self.fail(
                    f"[{idx}] filename: {filename!r}\nleft:\n{a!r}\nright:\n{b!r}"
                )

        if len(expected) != len(actual):
            self.fail(
                f"Length mismatch filename: {filename!r}\nleft len: {len(expected)}\nright len: {len(actual)}"
            )


if __name__ == "__main__":
    unittest.main()
