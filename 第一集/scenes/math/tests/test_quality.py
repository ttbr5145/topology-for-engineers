import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from render_quality import read_render_profile, validate_render_quality
from render import probe_video


class ManimQualityTests(unittest.TestCase):
    def test_modes_require_native_delivery_size(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(read_render_profile(directory), {"mode": "final"})
        with self.assertRaisesRegex(ValueError, "FINAL_RESOLUTION_TOO_LOW"):
            validate_render_quality({"width": 854, "height": 480}, {"mode": "final"})
        self.assertFalse(validate_render_quality({"width": 854, "height": 480}, {"mode": "preview"})["resolutionReady"])
        self.assertTrue(validate_render_quality({"width": 1920, "height": 1080}, {"mode": "final"})["resolutionReady"])

    def test_actual_movie_not_configured_label_determines_dimensions(self):
        expected = {"width": 1920, "height": 1080, "fps": 30, "frames": 2}
        class Result:
            returncode = 0
            stderr = ""
            stdout = json.dumps({"streams": [{"codec_type": "video", "width": 640, "height": 360,
                                   "avg_frame_rate": "30/1", "nb_read_frames": "2"}],
                                 "format": {"duration": "0.066667"}})
        with patch("render.subprocess.run", return_value=Result()):
            with self.assertRaisesRegex(RuntimeError, "MEDIA_VERIFICATION_FAILED"):
                probe_video(Path("video.mp4"), expected, "ffprobe")


if __name__ == "__main__":
    unittest.main()
