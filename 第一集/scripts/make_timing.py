"""由实测字幕时间生成每段 Manim 场景的时间表与帧数。

段边界以「下一段首句起点」为界，保证拼接后句界不漂移。
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FPS = 24
TAIL_FRAMES = 40
LEAD_SILENCE = 0.0  # 片头静默由 build_caption_track 的 initialSilenceSec 提供

SCRIPT = json.loads((ROOT / "script.json").read_text(encoding="utf-8"))
CAPS = json.loads((ROOT / "audio" / "voice-v3" / "captions.json").read_text(encoding="utf-8"))
caps = CAPS
assert len(caps) == len(SCRIPT["sentences"]), (len(caps), len(SCRIPT["sentences"]))

# 句号 -> 绝对秒（加片头静默）
starts = {i + 1: LEAD_SILENCE + c["startSec"] for i, c in enumerate(caps)}
ends = {i + 1: LEAD_SILENCE + c["endSec"] for i, c in enumerate(caps)}
audio_total = LEAD_SILENCE + caps[-1]["endSec"]

segs = SCRIPT["segments"]
bounds = []
for k, seg in enumerate(segs):
    start = starts[seg["sentences"][0]]
    if k + 1 < len(segs):
        stop = starts[segs[k + 1]["sentences"][0]]
        tail = 0
    else:
        stop = audio_total
        tail = TAIL_FRAMES
    frames = int(math.ceil((stop - start) * FPS)) + tail
    bounds.append((start, stop, frames))

total_frames = sum(b[2] for b in bounds)
timing = {"fps": FPS, "placeholder": False, "totalFrames": total_frames, "segments": {}}
for k, seg in enumerate(segs):
    start, stop, frames = bounds[k]
    rel = []
    for idx, sid in enumerate(seg["sentences"], start=1):
        rel.append({"i": idx, "id": sid,
                    "start": round(starts[sid] - start, 4),
                    "end": round(ends[sid] - start, 4)})
    timing["segments"][seg["id"]] = {
        "scene": seg["scene"],
        "seconds": round(frames / FPS, 4),
        "frames": frames,
        "sentences": rel,
    }

out = ROOT / "scenes" / "math" / "timing.json"
out.write_text(json.dumps(timing, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"totalFrames": total_frames, "seconds": round(total_frames / FPS, 2),
                  "segments": {b: f for b, (_, _, f) in zip([s["id"] for s in segs], bounds)}},
                 ensure_ascii=False))
