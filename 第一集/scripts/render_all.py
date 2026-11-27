"""按 timing.json 逐段渲染 Manim 场景，并核对实际帧数不少于目标帧数。"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJ = ROOT / "scenes" / "math"
OUT = ROOT / "renders"
MANIM = "/usr/local/bin/manim"

timing = json.loads((PROJ / "timing.json").read_text(encoding="utf-8"))
OUT.mkdir(exist_ok=True)
manifest = {}

only = sys.argv[1:] or [s["id"] for s in json.loads((ROOT / "script.json").read_text("utf-8"))["segments"]]

for seg_id in only:
    seg = timing["segments"][seg_id]
    scene = seg["scene"]
    need = int(seg["frames"])
    media = OUT / seg_id / "media"
    target = OUT / seg_id / f"{scene}.mp4"
    if target.exists():
        target.unlink()
    cmd = [MANIM, "--disable_caching", "--fps", str(timing["fps"]),
           "--resolution", "1920,1080", "--format", "mp4",
           "--media_dir", str(media), str(PROJ / "scene.py"), scene]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(f"FAILED {seg_id}\n{r.stderr[-2500:]}", file=sys.stderr)
        sys.exit(1)
    found = list(media.rglob(f"{scene}.mp4"))
    if len(found) != 1:
        print(f"OUTPUT_AMBIGUOUS {seg_id}: {found}", file=sys.stderr)
        sys.exit(1)
    src = found[0]
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", str(src), str(target)], check=True)
    probe = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                            "-show_entries", "stream=nb_read_frames,width,height,avg_frame_rate",
                            "-of", "json", str(target)], capture_output=True, text=True)
    info = json.loads(probe.stdout)["streams"][0]
    got = int(info["nb_read_frames"])
    ok = got >= need and info["width"] == 1920 and info["height"] == 1080
    manifest[seg_id] = {"scene": scene, "frames": got, "need": need, "ok": ok,
                        "width": info["width"], "height": info["height"],
                        "fps": info["avg_frame_rate"]}
    print(f"{seg_id} {scene}: {got} frames (need {need}) {'OK' if ok else 'SHORT'}")
    if not ok:
        sys.exit(1)

(OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
