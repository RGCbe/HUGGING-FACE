"""Burned-in caption file (ASS) from word timings.

    python3 captions.py TIMING_JSON OUT_ASS [--layout landscape|vertical] [--replace REPLACE_JSON]
                        [--from SEC] [--to SEC] [--shift SEC]

Words are grouped into short captions that break at punctuation. REPLACE_JSON is a list of
[spoken phrase, shown text] pairs, so "nineteen thirty-two" can read "1932" on screen.
--from/--to keep only that stretch of the timeline and --shift moves it (for Shorts).
"""
import argparse
import json
import re

ap = argparse.ArgumentParser()
ap.add_argument("timing")
ap.add_argument("out")
ap.add_argument("--layout", default="landscape")
ap.add_argument("--replace")
ap.add_argument("--from", dest="t_from", type=float, default=0.0)
ap.add_argument("--to", dest="t_to", type=float, default=1e9)
ap.add_argument("--shift", type=float, default=0.0)
a = ap.parse_args()

norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())
replace = [(p.split(), s) for p, s in json.load(open(a.replace))] if a.replace else []
replace.sort(key=lambda r: -len(r[0]))  # longest phrases first

words = [w for s in json.load(open(a.timing))["sections"] for w in s["words"]]
merged, i = [], 0
while i < len(words):
    for phrase, shown in replace:
        n = len(phrase)
        if [norm(w["w"]) for w in words[i:i + n]] == [norm(p) for p in phrase]:
            tail = re.search(r"[^\w]*$", words[i + n - 1]["w"]).group(0)
            head = shown[:1].upper() + shown[1:] if words[i]["w"][:1].isupper() else shown
            merged.append({"w": head + tail, "t0": words[i]["t0"], "t1": words[i + n - 1]["t1"]})
            i += n
            break
    else:
        merged.append(words[i])
        i += 1
words = [w for w in merged if a.t_from <= w["t0"] < a.t_to]

max_words, max_chars = (7, 40) if a.layout == "landscape" else (4, 22)
caps, cur = [], []
for w in words:
    cur.append(w)
    text = " ".join(x["w"] for x in cur)
    if len(cur) >= max_words or len(text) >= max_chars or re.search(r"[.?!:,]$", w["w"]):
        caps.append(cur)
        cur = []
if cur:
    caps.append(cur)


def ts(t):
    t = max(0.0, t + a.shift)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


if a.layout == "landscape":
    play, size, margin = (1920, 1080), 64, 42
else:
    play, size, margin = (1080, 1920), 84, 330
header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {play[0]}
PlayResY: {play[1]}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Patrick Hand,{size},&H00111111,&H00111111,&H0080E6FF,&H00000000,0,0,0,0,100,100,0,0,3,10,0,2,60,60,{margin},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
lines = []
for k, cap in enumerate(caps):
    start = cap[0]["t0"]
    end = cap[-1]["t1"] + 0.35
    if k + 1 < len(caps):
        end = min(end, caps[k + 1][0]["t0"])
    lines.append(f"Dialogue: 0,{ts(start)},{ts(end)},Cap,,0,0,0,,{' '.join(w['w'] for w in cap)}")
open(a.out, "w", encoding="utf-8").write(header + "\n".join(lines) + "\n")
print(f"wrote {a.out}: {len(caps)} captions")
