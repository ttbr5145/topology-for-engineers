"""把逐句配音 URL 下载为统一的 48kHz 单声道 PCM WAV，并生成 sentences.json。"""

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "audio"
SRC = AUDIO / "src"
OUT = AUDIO / "sentences"
URLS = json.loads((AUDIO / "voice-urls.json").read_text(encoding="utf-8"))
SCRIPT = json.loads((ROOT / "script.json").read_text(encoding="utf-8"))

SRC.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

missing = []
sentences = []
for s in SCRIPT["sentences"]:
    i = s["i"]
    url = next((u["url"] for u in URLS["sentences"] if u["id"] == i), "")
    if not url:
        missing.append(i)
        continue
    raw = SRC / f"raw-{i:02d}"
    if not raw.exists() or raw.stat().st_size == 0:
        subprocess.run(["curl", "-sL", "-o", str(raw), url], check=True)
    wav = OUT / f"sentence-{i:02d}.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-ac", "1", "-ar", "48000",
         "-c:a", "pcm_s16le", str(wav)],
        check=True,
    )
    sentences.append({"i": i, "text": s["text"], "file": f"sentence-{i:02d}.wav"})

(OUT / "sentences.json").write_text(
    json.dumps({"sentences": sentences}, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(json.dumps({"ok": len(sentences), "missing": missing}, ensure_ascii=False))
