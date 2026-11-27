"""Native-resolution delivery contract; deliberately needs no imaging package."""
import json
from pathlib import Path
import struct


def read_render_profile(root):
    file = Path(root) / "render-profile.json"
    profile = json.loads(file.read_text(encoding="utf-8")) if file.exists() else {"mode": "final"}
    if (not isinstance(profile, dict) or set(profile) - {"mode", "reason"}
            or profile.get("mode") not in {"final", "preview", "custom"}
            or ("reason" in profile and (not isinstance(profile["reason"], str) or not profile["reason"].strip()))
            or (profile.get("mode") == "custom" and not profile.get("reason", "").strip())):
        raise ValueError("INVALID_RENDER_PROFILE: custom requires a nonempty reason recording the user's explicit size request")
    if "reason" in profile:
        profile["reason"] = profile["reason"].strip()
    return profile


def validate_render_quality(config, profile):
    if any(type(config.get(key)) is not int or config[key] <= 0 or config[key] % 2 for key in ("width", "height")):
        raise ValueError("INVALID_RENDER_DIMENSIONS: dimensions must be positive even integers")
    if profile["mode"] == "final" and min(config["width"], config["height"]) < 1080:
        raise ValueError("FINAL_RESOLUTION_TOO_LOW: render natively with a short edge of at least 1080; use a separate preview project, or custom with an explicit user size request")
    return {**profile, "width": config["width"], "height": config["height"],
            "minimumShortEdge": 1080 if profile["mode"] == "final" else None,
            "resolutionReady": profile["mode"] != "preview"}


def protect_final_from_preview(root, profile):
    root = Path(root)
    if profile["mode"] != "preview" or not (root / "out/video.mp4").exists():
        return
    try:
        previous = json.loads((root / "out/render-result.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        previous = {}
    if previous.get("renderProfile", {}).get("mode") != "preview":
        raise ValueError("PREVIEW_WOULD_REPLACE_FINAL: use a separate preview project directory")


def png_dimensions(file):
    with Path(file).open("rb") as source:
        header = source.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"INVALID_FRAME: {Path(file).name} is not a PNG")
    return struct.unpack(">II", header[16:24])


def verify_source_frames(files, expected):
    for file in files:
        actual = png_dimensions(file)
        if actual != (expected["width"], expected["height"]):
            raise ValueError(f"SOURCE_FRAME_SIZE_MISMATCH: {Path(file).name} is {actual}, expected native {expected['width']}x{expected['height']}; rerender source frames instead of upscaling")
