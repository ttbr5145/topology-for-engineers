#!/usr/bin/env python3
"""Render through the selected Python's Manim CE, then verify actual media."""

import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction
from render_quality import read_render_profile, validate_render_quality, protect_final_from_preview


ROOT = Path(__file__).resolve().parents[1]


def load_config(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"width", "height", "fps", "frames"}:
        raise ValueError("video-config.json must contain exactly width, height, fps, frames")
    for key, value in data.items():
        if type(value) is not int or value <= 0:
            raise ValueError(f"{key} must be a positive integer")
    if data["width"] % 2 or data["height"] % 2:
        raise ValueError("H.264 yuv420p dimensions must be even")
    return data


def executable(value, label):
    result = shutil.which(value)
    if not result:
        raise RuntimeError(f"MISSING_DEPENDENCY: {label} executable not found: {value}")
    return result


def probe_video(file, expected, ffprobe):
    command = [ffprobe, "-v", "error", "-count_frames", "-show_entries",
               "stream=codec_type,width,height,avg_frame_rate,nb_read_frames:format=duration",
               "-of", "json", str(file)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise RuntimeError(f"FFPROBE_FAILED: {result.stderr.strip()}")
    data = json.loads(result.stdout)
    videos = [s for s in data.get("streams", []) if s.get("codec_type") == "video"]
    if len(videos) != 1:
        raise RuntimeError("MEDIA_VERIFICATION_FAILED: expected exactly one video stream")
    stream = videos[0]
    try:
        fps = Fraction(stream["avg_frame_rate"])
        frames = int(stream["nb_read_frames"])
        duration = float(data["format"]["duration"])
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        raise RuntimeError("MEDIA_VERIFICATION_FAILED: ffprobe did not return usable actual frame count/rate/duration") from error
    actual = {"width": stream["width"], "height": stream["height"], "fps": float(fps),
              "frames": frames, "durationSec": duration,
              "audioStreams": sum(s.get("codec_type") == "audio" for s in data.get("streams", []))}
    if (actual["width"] != expected["width"] or actual["height"] != expected["height"]
            or fps != expected["fps"] or frames != expected["frames"]
            or not math.isfinite(duration) or duration <= 0):
        raise RuntimeError(f"MEDIA_VERIFICATION_FAILED: expected {expected}; actual {actual}")
    return actual


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", default="SmokeScene", help="Scene class from scene.py")
    args = parser.parse_args()
    settings = load_config(ROOT / "video-config.json")
    profile = read_render_profile(ROOT)
    quality = validate_render_quality(settings, profile)
    protect_final_from_preview(ROOT, profile)
    python = executable(os.environ.get("PYTHON", sys.executable), "Python")
    ffprobe = executable(os.environ.get("FFPROBE_PATH", "ffprobe"), "ffprobe (install FFmpeg or set FFPROBE_PATH)")
    check = subprocess.run([python, "-c", "import manim; print(manim.__version__)"], capture_output=True, text=True)
    if check.returncode:
        raise RuntimeError("MANIM_UNAVAILABLE: selected Python cannot import Manim CE. Install this route's requirements.txt in that environment and its required Cairo/Pango system libraries. " + check.stderr.strip())
    if check.stdout.strip() != "0.19.0":
        raise RuntimeError(f"MANIM_VERSION_MISMATCH: expected CE 0.19.0, found {check.stdout.strip()!r}")
    out = ROOT / "out"
    out.mkdir(exist_ok=True)
    # Publish only the freshly rendered, verified file. Old final output cannot
    # accidentally stand in for a renderer that produced nothing.
    with tempfile.TemporaryDirectory(prefix=".manim-", dir=out) as temporary:
        command = [python, "-m", "manim", "--renderer=cairo", "--format=mp4",
                   "--disable_caching", "--fps", str(settings["fps"]),
                   "--resolution", f'{settings["width"]},{settings["height"]}',
                   "--media_dir", temporary, "--output_file", "video",
                   str(ROOT / "scene.py"), args.scene]
        result = subprocess.run(command, cwd=ROOT)
        if result.returncode:
            raise RuntimeError(f"MANIM_RENDER_FAILED: exit {result.returncode}")
        candidates = [p for p in Path(temporary).rglob("video.mp4") if "partial_movie_files" not in p.parts]
        if len(candidates) != 1 or candidates[0].stat().st_size == 0:
            raise RuntimeError("RENDER_OUTPUT_MISSING: expected one newly rendered nonempty video.mp4")
        actual = probe_video(candidates[0], settings, ffprobe)
        os.replace(candidates[0], out / "video.mp4")
    receipt = {"schemaVersion": 1, "backend": "manim", "status": "complete",
               "output": "out/video.mp4", "expected": settings, "actual": actual,
               "metadataVerified": True, "validationMethod": "ffprobe -count_frames",
               "audioMode": "silent" if actual["audioStreams"] == 0 else "present"}
    receipt.update(renderProfile=quality, resolutionReady=quality["resolutionReady"], deliveryReady=False,
                   artifactRole="visual-only", deliveryStage="intermediate", renderSucceeded=True,
                   nativeRenderSize={"width": settings["width"], "height": settings["height"]},
                   sourceFrameSizeVerified=True, outputResized=False)
    (out / "render-result.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    try:
        run()
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
