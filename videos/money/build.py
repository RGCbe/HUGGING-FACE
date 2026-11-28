"""Money Tea Talks: one finance Short in flat vector style, built from WORK/spec.json and the Tamil voice.

    python3 videos/money/build.py WORK      # WORK/out/video.mp4, WORK/out/subs_ta.srt (+ subs_en.srt if spec "en")

WORK holds spec.json, voice_ta/sec_NN.wav (one per spoken line, videos/kural/eleven.py), words.json (each line's word
timings from faster-whisper, videos/money/check_voice.py) and pics/NAME.png (the flat story pictures). English is
YouTube's automatic dub (the owner, 27 Nov 2026: "KEEP AUTODUB"), so only Tamil is voiced.

Safe area: every word on screen stays inside the band YouTube Shorts leaves clear of its buttons, title and channel
name (SAFE below: y 288-1248, x 48-888, from YouTube's Shorts ad specs as HyperFrames' checker uses them; on 27 Nov 2026
it found our first Short's rate note and colour key under them). The build checks every text box and stops if one
falls outside.

spec.json:
  {"slug": "start-early",
   "lines": ["Tamil line as captioned, with digits", ...],      one per voice line, for the subtitles
   "en": ["English line", ...],                                   optional, English subtitles
   "scenes": [{"kind": ..., "line": N, ...}, ...]}                line N (1-based) is said over the scene; a scene
                                                                  without a line takes "seconds"
Scene kinds:
  host     {"pose": "think" | "comment", "captions": [[WHEN, "line 1", "line 2"], ...]}   the owner's flat host,
           lips moving with the voice (mouth.py)
  picture  {"pic": "priya", "move": 0-3, "caption": ["line 1", "line 2"]}   a story picture moving in 3D (depthmove)
  bars     {"title": [l1, l2], "monthly": 2000, "rate": 0.12, "ages": [25, 60], "run": [WHEN, WHEN],
            "people": [{"name": "ப்ரியா", "start": 25, "pic": "priya", "face": [cx, cy, r], "land": WHEN}, ...]}
           two people saving the same amount each month from different ages (monthly compounding); the ages run
           over "run", each person's final amount lands at its "land"
  cards    {"cards": [{"label": "...", "value": 240000, "colour": "blue" | "coral", "at": WHEN, "count_to": WHEN}]}
  rule     {"title": [l1, l2], "items": [[WHEN, "text"], ...]}                a rule card that builds up line by line
  Any scene may add "note": the small line at the bottom of the safe band (bars and cards default to the rate note).
WHEN is seconds into the scene, or "word:XYZ": when the scene's line says its first word starting with XYZ.
"""
import json
import math
import os
import random
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "videos", "doodle"))
from mouth import levels  # noqa: E402

FONT = os.path.join(REPO, "videos", "movies-explained", "fonts", "MuktaMalar-ExtraBold.ttf")
W, H, FPS = 1080, 1920, 30
SAFE = (48, 288, 888, 1248)              # x0, y0, x1, y1: YouTube Shorts' clear band
CX = (SAFE[0] + SAFE[2]) // 2           # the band's centre (the right side has YouTube's buttons)
LEAD, TAIL = 0.2, 0.35
SKY, NAVY, ORANGE, CORAL, BLUE, WHITE = (161, 215, 244), (31, 42, 68), (245, 162, 59), (232, 87, 79), (64, 110, 190), (255, 255, 255)
RATE_NOTE = "*12% ஒரு உதாரணம், உத்தரவாதம் இல்லை. கல்வி மட்டும்."
_fonts, BOXES = {}, []


def font(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM)
    return _fonts[size]


def text(d, xy, s, size, fill=NAVY, anchor="mm"):
    BOXES.append((d.textbbox(xy, s, font=font(size), anchor=anchor), s))
    d.text(xy, s, font=font(size), fill=fill, anchor=anchor)


def fit(d, lines, size, width):
    while size > 30 and max(d.textlength(s, font=font(size)) for s in lines if s) > width:
        size -= 2
    return size


def check_safe(where):
    bad = [(b, s) for b, s in BOXES if b[0] < SAFE[0] or b[1] < SAFE[1] or b[2] > SAFE[2] or b[3] > SAFE[3]]
    BOXES.clear()
    if bad:
        raise SystemExit(f"{where}: text outside the Shorts safe band {SAFE}: " +
                         "; ".join(f"{s!r} at {tuple(int(v) for v in b)}" for b, s in bad))


def card(im, box, radius=40, fill=WHITE):
    x0, y0, x1, y1 = [int(v) for v in box]
    sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 12, x1, y1 + 12), radius, fill=60)
    im.paste(Image.new("RGB", im.size, NAVY), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(im).rounded_rectangle((x0, y0, x1, y1), radius, fill=fill)


def two_lines(im, l1, l2, top):
    """Two caption lines on a white card whose top is at `top`: line 1 navy, line 2 coral."""
    d = ImageDraw.Draw(im)
    size = fit(d, [l1, l2], 56, SAFE[2] - SAFE[0] - 90)
    widest = max(d.textlength(s, font=font(size)) for s in (l1, l2) if s)
    h = 200 if l2 else 120
    card(im, (CX - widest / 2 - 40, top, CX + widest / 2 + 40, top + h))
    d = ImageDraw.Draw(im)
    text(d, (CX, top + 62), l1, size)
    if l2:
        text(d, (CX, top + 142), l2, size, fill=CORAL)


def bottom_caption(im, l1, l2):
    two_lines(im, l1, l2, SAFE[3] - 12 - (200 if l2 else 120))


def note(im, s):
    if s:
        d = ImageDraw.Draw(im)
        size = fit(d, [s], 30, SAFE[2] - SAFE[0] - 40)
        w = d.textlength(s, font=font(size))
        lay = Image.new("L", im.size, 0)
        ImageDraw.Draw(lay).rounded_rectangle((CX - w / 2 - 20, 1192, CX + w / 2 + 20, 1240), 22, fill=225)
        im.paste(Image.new("RGB", im.size, WHITE), (0, 0), lay)
        text(ImageDraw.Draw(im), (CX, 1215), s, size)


def money_words(x):
    if x >= 1e7:
        return f"₹{x / 1e7:.2f} கோடி"
    if x >= 1e5:
        return f"₹{x / 1e5:.1f}".replace(".0", "") + " லட்சம்"
    return "₹" + inr(x)


def inr(x):
    s = str(int(round(x)))
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    return ",".join(([head] if head else []) + parts + [tail]) if len(s) > 3 else s


def compound(monthly, rate, months):
    m = rate / 12
    return monthly * ((1 + m) ** months - 1) / m * (1 + m) if months > 0 else 0.0


class Build:
    def __init__(self, work):
        self.work = work
        self.spec = json.load(open(os.path.join(work, "spec.json"), encoding="utf-8"))
        self.words = json.load(open(os.path.join(work, "words.json"), encoding="utf-8"))
        self.out = os.path.join(work, "out")
        os.makedirs(self.out, exist_ok=True)
        self.voice = {}

    def line_voice(self, n):
        if n not in self.voice:
            with wave.open(os.path.join(self.work, "voice_ta", f"sec_{n:02d}.wav")) as f:
                self.voice[n] = (np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32) / 32768,
                                 f.getframerate())
        return self.voice[n]

    def when(self, scene, w):
        if isinstance(w, (int, float)):
            return float(w)
        if isinstance(w, str) and w.startswith("word:"):
            key = f"ta{scene['line']}"
            for word, t0, _ in self.words[key]["words"]:
                if word.startswith(w[5:]):
                    return LEAD + t0
            raise SystemExit(f"scene {scene['kind']} line {scene['line']}: no word starting with {w[5:]!r}")
        raise SystemExit(f"bad time {w!r}")

    def duration(self, scene):
        if scene.get("line"):
            v, sr = self.line_voice(scene["line"])
            return LEAD + len(v) / sr + TAIL
        return float(scene["seconds"])

    # the scene kinds: each returns draw(t, dur) -> PIL image
    def host(self, s, dur):
        pose = s["pose"]
        hs = {"comment": [0, 9, 18, 30], "think": [0, 7, 14, 22]}[pose]
        pics = [Image.open(os.path.join(HERE, "host", f"host_{pose}.png" if h == 0 else f"host_{pose}_m{h}.png"))
                .convert("RGB") for h in hs]
        n = int(round(dur * FPS))
        v, sr = self.line_voice(s["line"])
        mouth = levels(v, sr, FPS, n, int(round(LEAD * FPS)))
        caps = [(self.when(s, c[0]), c[1], c[2] if len(c) > 2 else "") for c in s["captions"]]

        def draw(t, d):
            im = pics[mouth[min(n - 1, int(round(t * FPS)))]]
            z = 1.0 + 0.04 * t / d                    # a slow push in, smooth (the camera moves at full rate)
            w = int(1040 * z)
            h = int(im.height * w / im.width)
            canvas = Image.new("RGB", (W, H), SKY)
            canvas.paste(im.resize((w, h), Image.LANCZOS), ((W - w) // 2, 60 - int(20 * (z - 1) * 25)))
            l1, l2 = [c[1:] for c in caps if t >= c[0]][-1]
            bottom_caption(canvas, l1, l2)
            note(canvas, s.get("note"))
            return canvas
        return draw

    def picture(self, s, dur):
        import depthmove
        path = os.path.join(self.out, f"{s['pic']}_{dur:.2f}.mp4")
        if not os.path.exists(path):
            depthmove.shot(os.path.join(self.work, "pics", f"{s['pic']}.png"), path, dur, s.get("move", 0),
                           size=(W, H), fps=FPS, punch=True)
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True, check=True).stdout
        frames = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
        l1, l2 = (s["caption"] + [""])[:2]

        def draw(t, d):
            im = Image.fromarray(frames[min(len(frames) - 1, int(t * FPS))]).copy()
            bottom_caption(im, l1, l2)
            note(im, s.get("note"))
            return im
        return draw

    def bars(self, s, dur):
        monthly, rate = s.get("monthly", 2000), s.get("rate", 0.12)
        a0, a1 = s.get("ages", [25, 60])
        r0, r1 = (self.when(s, x) for x in s["run"])
        people = []
        for p in s["people"]:
            im = Image.open(os.path.join(self.work, "pics", f"{p['pic']}.png")).convert("RGB")
            cx, cy, r = p["face"]
            face = im.crop((cx - r, cy - r, cx + r, cy + r)).resize((84, 84), Image.LANCZOS)
            people.append(dict(p, face=face, land_t=self.when(s, p["land"])))
        final = max(compound(monthly, rate, (a1 - p["start"]) * 12) for p in people)
        mask = Image.new("L", (84, 84), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 83, 83), fill=255)
        base, top_min, bw = 1040, 735, 230
        centres = [CX - 220, CX + 220]
        rate_tag = f"{rate * 100:g}% / வருஷம்*"

        def draw(t, d):
            im = Image.new("RGB", (W, H), SKY)
            two_lines(im, s["title"][0], s["title"][1], 300)
            age = a0 + (a1 - a0) * min(1, max(0, (t - r0) / max(0.01, r1 - r0)))
            dr = ImageDraw.Draw(im)
            pulse = 1 + 0.15 * max(0, 1 - abs(t - r1 - 0.1) / 0.15)
            dr.rounded_rectangle((CX - 250 - 10 * pulse, 512, CX + 10 - 0 + 10 * pulse - 10, 582), 35, fill=NAVY)
            text(dr, (CX - 120, 546), f"வயசு {int(age)}", int(46 * pulse), fill=WHITE)
            dr.rounded_rectangle((CX + 40, 518, CX + 300, 576), 28, fill=WHITE)
            text(dr, (CX + 170, 547), rate_tag, 30, fill=BLUE)
            card(im, (SAFE[0] + 10, 600, SAFE[2] - 10, 1240), radius=40)
            dr = ImageDraw.Draw(im)
            for p, mid in zip(people, centres):
                months = max(0.0, (age - p["start"]) * 12)
                v, put = compound(monthly, rate, months), monthly * months
                x0, x1 = mid - bw // 2, mid + bw // 2
                if months <= 0:
                    dr.rounded_rectangle((x0, base - 20, x1, base), 10, fill=(225, 232, 242))
                    text(dr, (mid, base - 60), "இன்னும் ஆரம்பிக்கல", 32, fill=CORAL)
                else:
                    hv = max(20, v / final * (base - top_min))
                    hp = max(8, put / final * (base - top_min))
                    dr.rounded_rectangle((x0, base - hv, x1, base), 18, fill=ORANGE)
                    dr.rounded_rectangle((x0, base - hp, x1, base), 10, fill=BLUE)
                    landed = t >= p["land_t"]
                    pop = 1 + 0.22 * max(0, 1 - abs(t - p["land_t"] - 0.12) / 0.12) if landed else 1
                    text(dr, (mid, base - hv - 42), money_words(v) if landed else "₹" + inr(v), int(52 * pop))
                    if landed:
                        text(dr, (mid, base - hv - 98), f"போட்டது {money_words(put)}", 30, fill=BLUE)
                        if hv - hp > 120:
                            text(dr, (mid, base - (hv + hp) / 2), "வட்டி மேல வட்டி", 30, fill=WHITE)
                im.paste(p["face"], (mid - 42, base + 14), mask)
                dr.ellipse((mid - 42, base + 14, mid + 42, base + 98), outline=NAVY, width=5)
                text(dr, (mid, base + 128), f"{p['name']}, {p['start']}-ல ஆரம்பம்", 32)
            dr.line((SAFE[0] + 50, base, SAFE[2] - 50, base), fill=NAVY, width=6)
            note(im, s.get("note", RATE_NOTE))
            return im
        return draw

    def cards(self, s, dur):
        items = [dict(c, at_t=self.when(s, c["at"]), to_t=self.when(s, c.get("count_to", c["at"]))) for c in s["cards"]]
        colours = {"blue": BLUE, "coral": CORAL, "navy": NAVY}

        def draw(t, d):
            im = Image.new("RGB", (W, H), SKY)
            for i, c in enumerate(items):
                k = min(1, max(0, (t - c["at_t"]) / 0.45))
                if k <= 0:
                    continue
                slide = int((1 - (1 - (1 - k) ** 3)) * 900)
                top = 330 + i * 400
                card(im, (SAFE[0] + 10 + slide, top, SAFE[2] - 10 + slide, top + 300), radius=44)
                dr = ImageDraw.Draw(im)
                if slide == 0:
                    text(dr, (CX, top + 80), c["label"], fit(dr, [c["label"]], 44, 760))
                    span = max(0.01, c["to_t"] - c["at_t"] - 0.25)
                    p = min(1, max(0, (t - c["at_t"] - 0.25) / span)) if c["to_t"] > c["at_t"] else 1
                    shown = c["value"] * (1 - (1 - p) ** 3)
                    text(dr, (CX, top + 200), "+" + money_words(shown), 100, fill=colours[c.get("colour", "blue")])
                if i > 0 and slide == 0:
                    dr.polygon([(CX - 30, top - 80), (CX + 30, top - 80), (CX, top - 40)], fill=NAVY)
            note(im, s.get("note", RATE_NOTE))
            return im
        return draw

    def rule(self, s, dur):
        items = [(self.when(s, w), txt) for w, txt in s["items"]]

        def draw(t, d):
            im = Image.new("RGB", (W, H), SKY)
            two_lines(im, s["title"][0], s["title"][1] if len(s["title"]) > 1 else "", 300)
            for i, (w, txt) in enumerate(items):
                if t < w:
                    continue
                top = 540 + i * 125
                card(im, (SAFE[0] + 10, top, SAFE[2] - 10, top + 105), radius=30)
                dr = ImageDraw.Draw(im)
                text(dr, (CX, top + 52), txt, fit(dr, [txt], 42, 760))
            note(im, s.get("note"))
            return im
        return draw

    def run(self):
        scenes = self.spec["scenes"]
        durs = [self.duration(s) for s in scenes]
        frames = [int(round(d * FPS)) for d in durs]
        draws = [getattr(self, s["kind"])(s, d) for s, d in zip(scenes, durs)]
        silent = os.path.join(self.out, "silent.mp4")
        p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s",
                              f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                              "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
        for k, (draw, n) in enumerate(zip(draws, frames)):
            for i in range(n):
                BOXES.clear()
                p.stdin.write(draw(i / FPS, durs[k]).convert("RGB").tobytes())
                check_safe(f"scene {k + 1} ({scenes[k]['kind']}) at {i / FPS:.2f} s")
            print(f"scene {k + 1} {scenes[k]['kind']}: {durs[k]:.2f} s", flush=True)
        p.stdin.close()
        p.wait()
        total = sum(frames) / FPS
        # the voice: each line at its scene's start + LEAD
        sr = self.line_voice(scenes[0].get("line") or 1)[1]
        track = np.zeros(int(total * sr) + sr, np.float32)
        at, cues = 0, {"ta": [], "en": []}
        for s, n in zip(scenes, frames):
            if s.get("line"):
                v, _ = self.line_voice(s["line"])
                i = int((at / FPS + LEAD) * sr)
                track[i: i + len(v)] += v
                start, length = at / FPS + LEAD, len(v) / sr
                for lang in cues:
                    lines = self.spec.get("lines" if lang == "ta" else "en")
                    if lines:
                        cues[lang].append((start, length, lines[s["line"] - 1]))
            at += n
        voice = os.path.join(self.out, "voice.wav")
        with wave.open(voice, "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(sr)
            f.writeframes((np.clip(track[: int(total * sr)], -1, 1) * 32767).astype(np.int16).tobytes())
        music = os.path.join(self.out, "music.wav")
        subprocess.run([sys.executable, os.path.join(REPO, "videos", "doodle", "music.py"), music, f"{total + 1:.2f}",
                        "--bpm", "96", "--seed", str(self.spec.get("music_seed", 3))], check=True)
        mix = os.path.join(self.out, "mix.m4a")  # mix.py writes AAC
        subprocess.run([sys.executable, os.path.join(REPO, "videos", "doodle", "mix.py"), voice, music, mix,
                        "--music-gain", "0.28"], check=True)
        video = os.path.join(self.out, "video.mp4")
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", silent, "-i", mix, "-c:v", "copy", "-c:a", "copy",
                        "-shortest", "-movflags", "+faststart", video], check=True)
        for lang, cs in cues.items():
            if cs:
                write_srt(os.path.join(self.out, f"subs_{lang}.srt"), cs)
        print(f"{video}: {total:.1f} s, every text inside the Shorts safe band")


def write_srt(path, cues):
    """One cue per sentence, each sentence timed by its share of the line's letters."""
    import re

    def ts(t):
        ms = int(round(t * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    out = []
    for start, length, line in cues:
        parts = [x.strip() for x in re.split(r"(?<=[.?!])\s+", line) if x.strip()]
        total = sum(len(x) for x in parts)
        t = start
        for x in parts:
            d = length * len(x) / total
            out.append((t, t + d, x))
            t += d
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, x) in enumerate(out, 1):
            f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{x}\n\n")


if __name__ == "__main__":
    Build(sys.argv[1]).run()
