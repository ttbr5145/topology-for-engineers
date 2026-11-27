"""生成公共合成的 composition.json：按段拼接画面轨，挂上旁白与逐句字幕。"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
timing = json.loads((ROOT / "scenes" / "math" / "timing.json").read_text(encoding="utf-8"))
caps = json.loads((ROOT / "audio" / "voice-v3" / "captions.json").read_text(encoding="utf-8"))
script = json.loads((ROOT / "script.json").read_text(encoding="utf-8"))

segments = []
for seg in script["segments"]:
    info = timing["segments"][seg["id"]]
    segments.append({
        "id": seg["id"],
        "frames": int(info["frames"]),
        "layers": [{
            "type": "video",
            "file": f"renders/{seg['id']}/{info['scene']}.mp4",
            "sourceStartFrame": 0,
            "x": 0, "y": 0,
            "width": 1920, "height": 1080,
            "opacity": 1,
        }],
    })

full_text = "".join(s["text"] for s in script["sentences"])

composition = {
    "schemaVersion": 1,
    "video": {"width": 1920, "height": 1080, "fps": int(timing["fps"])},
    "audioMode": "narration",
    "segments": segments,
    "audio": [{
        "id": "voice",
        "role": "narration",
        "file": "audio/voice-v3/narration.wav",
        "text": full_text,
        "startFrame": 0,
        "volume": 1,
        "captions": [{"text": c["text"], "startSec": c["startSec"], "endSec": c["endSec"],
                      "timingSource": "sentence-audio"} for c in caps],
    }],
    "subtitles": {
        "enabled": True,
        "fontFile": "fonts/NotoSansSC-Regular.otf",
        "fontFamily": "Noto Sans CJK SC",
    },
    "renderProfile": {"mode": "final"},
}

(ROOT / "composition.json").write_text(json.dumps(composition, ensure_ascii=False, indent=2),
                                       encoding="utf-8")
print(json.dumps({"segments": len(segments), "frames": sum(s["frames"] for s in segments),
                  "captions": len(caps)}, ensure_ascii=False))
