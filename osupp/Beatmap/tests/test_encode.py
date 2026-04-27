import os
import unittest

from beatmap import Beatmap

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
RESOURCES_DIR = os.path.join(root_dir, "resources")


class TestEncode(unittest.TestCase):
    def test_stability(self):
        for filename in os.listdir(RESOURCES_DIR):
            if not (filename.endswith(".osu") or filename.endswith(".osb")):
                continue

            filepath = os.path.join(RESOURCES_DIR, filename)

            with self.subTest(file=filename):
                try:
                    # 1. Decode the original map from the file
                    decoded_original = Beatmap.from_path(filepath)

                    # 2. Encode the map back into a string in memory
                    encoded_str = decoded_original.encode_to_string()

                    # 3. Decode the newly generated string
                    decoded_after_encode = Beatmap.from_bytes(
                        encoded_str.encode("utf-8")
                    )

                    # 4. The ultimate test: both objects must be identical
                    self.assertEqual(decoded_original, decoded_after_encode)

                except Exception as e:
                    self.fail(f"Failed processing {filename}: {e}")

    def test_multi_segment_slider_with_floating_point_error(self):
        filepath = os.path.join(RESOURCES_DIR, "multi-segment-slider.osu")

        decoded_original = Beatmap.from_path(filepath)
        encoded_str = decoded_original.encode_to_string()
        decoded_after_encode = Beatmap.from_bytes(encoded_str.encode("utf-8"))

        self.assertEqual(decoded_original, decoded_after_encode)

    def test_bspline_curve_type(self):
        filepath = os.path.join(RESOURCES_DIR, "bspline-curve-type.osu")

        decoded_original = Beatmap.from_path(filepath)
        encoded_str = decoded_original.encode_to_string()

        self.assertIn("B2|", encoded_str)

        decoded_after_encode = Beatmap.from_bytes(encoded_str.encode("utf-8"))
        self.assertEqual(decoded_original, decoded_after_encode)


if __name__ == "__main__":
    unittest.main()
