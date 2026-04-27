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
                decoded_original = Beatmap.from_path(filepath)
                encoded_str_1 = decoded_original.encode_to_string()

                decoded_after_encode = Beatmap.from_bytes(encoded_str_1.encode("utf-8"))
                encoded_str_2 = decoded_after_encode.encode_to_string()

                self.assertEqual(encoded_str_1, encoded_str_2)


if __name__ == "__main__":
    unittest.main()
