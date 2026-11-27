import json
SEG = {"s1": 3, "s2": 5, "s3": 5, "s4": 2, "s5": 3, "s6": 10, "s7": 8, "s8": 5, "s9": 5, "s10": 2}
OUT = "timing.json"
data = {"fps": 24, "placeholder": True, "segments": {}}
for k, n in SEG.items():
    sents = []
    for i in range(n):
        sents.append({"i": i + 1, "start": round(i * 4.0, 3), "end": round((i + 1) * 4.0, 3)})
    data["segments"][k] = {"seconds": round(n * 4.0, 3), "sentences": sents}
open(OUT, "w").write(json.dumps(data, ensure_ascii=False, indent=2))
print("ok")
