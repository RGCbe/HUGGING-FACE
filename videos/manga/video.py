"""Capability test: the lettered strip as a 16:9 video, the camera moving panel to panel with the narration."""
import json
import os
import subprocess

from PIL import Image, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
FPS, VW, VH, SW, GAP_S, MOVE = 30, 1920, 1080, 1000, 0.6, 0.8
LINE_PANEL = [0, 0, 1, 2, 3, 4, 5]  # which panel each narration line is about
MOODS = {0: "curious", 2: "playful", 5: "dramatic", 6: "suspense"}

strip = Image.open(os.path.join(OUT, "strip.png")).convert("RGB")
panels = json.load(open(os.path.join(OUT, "panels.json")))
k = SW / strip.width
fg = strip.resize((SW, round(strip.height * k)), Image.LANCZOS)
kb = VW / strip.width
bg = ImageEnhance.Brightness(strip.resize((VW, round(strip.height * kb))).filter(ImageFilter.GaussianBlur(30))).enhance(0.45)

# the voice: lines joined with short gaps; each line's start time
wavs = [os.path.join(HERE, "voice", f"sec_{i:02d}.wav") for i in range(1, len(LINE_PANEL) + 1)]
dur = lambda p: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                     capture_output=True, text=True, check=True).stdout)
starts, t = [], 0.6
for w in wavs:
    starts.append(t)
    t += dur(w) + GAP_S
total = t + 1.5
silence = os.path.join(OUT, "gap.wav")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "lavfi", "-t", str(GAP_S), "-i", "anullsrc=r=24000:cl=mono", silence], check=True)
lead = os.path.join(OUT, "lead.wav")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "lavfi", "-t", "0.6", "-i", "anullsrc=r=24000:cl=mono", lead], check=True)
open(os.path.join(OUT, "voice.txt"), "w").write("".join(f"file '{p}'\n" for w in wavs for p in (w, silence)) .replace(f"file '{lead}'\n", "") )
open(os.path.join(OUT, "voice.txt"), "w").write(f"file '{lead}'\n" + "".join(f"file '{w}'\nfile '{silence}'\n" for w in wavs))
voice = os.path.join(OUT, "voice.wav")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(OUT, "voice.txt"),
                "-af", f"apad=whole_dur={total}", voice], check=True)


def target(i):
    """Camera top (in fg pixels) that centres panel i, its narration gap above included for wide panels."""
    p = panels[i]
    top, h = p["top"] * k, p["height"] * k
    centre = top + h / 2 - (60 if h < VH * 0.7 else 0)
    return max(0, min(fg.height - VH, centre - VH / 2))


def camera(time):
    y = target(LINE_PANEL[0])
    for s, pi in zip(starts, LINE_PANEL):
        if time >= s:
            a = min(1.0, (time - s) / MOVE)
            a = a * a * (3 - 2 * a)  # ease in and out
            y = y + (target(pi) - y) * a
    return y


events = [{"t": starts[i], "kind": "mood", "mood": m} for i, m in MOODS.items()]
events += [{"t": round(s, 3), "kind": "whoosh"} for i, s in enumerate(starts) if i and LINE_PANEL[i] != LINE_PANEL[i - 1]]
events += [{"t": round(starts[5] + 0.5, 3), "kind": "sting", "name": "hit"}]
json.dump(sorted(events, key=lambda e: e["t"]), open(os.path.join(OUT, "events.json"), "w"))

silent = os.path.join(OUT, "silent.mp4")
ff = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}",
                       "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", silent],
                      stdin=subprocess.PIPE)
for f in range(int(total * FPS)):
    y = camera(f / FPS)
    by = int(y / k * kb + VH / 2 * (kb / k) - VH / 2)
    frame = bg.crop((0, max(0, by), VW, max(0, by) + VH))
    frame.paste(fg.crop((0, int(y), SW, int(y) + VH)), ((VW - SW) // 2, 0))
    ff.stdin.write(frame.tobytes())
ff.stdin.close()
ff.wait()
print(f"video {total:.1f}s, lines start at {[round(s, 1) for s in starts]}")
