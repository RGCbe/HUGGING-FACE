"""A YouTube recap of a lettered episode, in Manoj's voice, plus a vertical Short.

    python3 recap.py STEP EPISODE_DIR        (STEP: voice, video, short, upload)

EPISODE_DIR/recap/recap.json holds the narration: "lines" [{"panel", "text", "mood"?, "sting"?, "punch"?}]
where panel is a panel name from the lettered strip (letter.py's panels.json; "end" is the closing card),
mood a score.py mood that starts with the line, sting {"name", "at": "start" | "end"} a score.py hit, and
punch stops the music just before the line's last word. "short" lists the Short's lines: {"from": N} reuses
line N of the recap, {"new": {...}} is a line voiced only for the Short. "meta" has the titles, descriptions,
tags and publish times.

  voice   voices the lines with ../teabreak/build.py's say() (every word checked) and times them
  video   the 1920x1080 recap: the strip in the middle over a blurred copy of itself, the camera moving
          to each line's panel and down tall ones; mood music, stings, whooshes, captions; a thumbnail
  short   the 1080x1920 Short, the strip full width
  upload  writes upload.json for ../doodle/upload.py, both videos private until their times

Needs the Tea Break voice setup (source ~/.cache/tea-break/env.sh) and letter.py's out/webtoon/strip.png.
"""
import json
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEOS = os.path.dirname(HERE)
DOODLE = os.path.join(VIDEOS, "doodle")
sys.path.insert(0, os.path.join(VIDEOS, "teabreak"))
import build as tb  # noqa: E402  (say, concat, emotion_refs, run, env, duration, cfg)

FPS, MOVE, TAIL = 30, 0.8, 3.0


def load(ep):
    r = os.path.join(ep, "recap")
    return r, json.load(open(os.path.join(r, "recap.json")))


def write_lines(path, lines):
    open(path, "w", encoding="utf-8").write("\n".join(l["text"] for l in lines) + "\n")


def short_lines(spec):
    return [s["new"] if "new" in s else dict(spec["lines"][s["from"] - 1], **{k: v for k, v in s.items() if k != "from"})
            for s in spec["short"]["lines"]]


def step_voice(ep):
    r, spec = load(ep)
    refs, moods = tb.emotion_refs(r)
    print(f"emotion samples: {', '.join(moods) or 'none yet (every line in the usual voice)'}")
    names = ",".join(n for n in (spec.get("names", ""), "Manoj") if n)
    text = os.path.join(r, "voiceover_en.txt")
    write_lines(text, spec["lines"])
    lines = tb.say(text, os.path.join(r, "tts"), names, refs)
    new = [s["new"] for s in spec["short"]["lines"] if "new" in s]
    short_text = os.path.join(r, "short_new.txt")
    write_lines(short_text, new)
    new_wavs = tb.say(short_text, os.path.join(r, "short_tts"), names, refs)
    gap = os.path.join(r, "gap.wav")
    tb.run("ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "lavfi", "-t", tb.GAP, "-i", "anullsrc=r=24000:cl=mono", gap)
    voice = os.path.join(r, "voice.wav")
    tb.concat([p for k, w in enumerate(lines) for p in ([gap, w] if k else [w])], voice)
    seconds = tb.duration(voice) + TAIL
    shortest, longest = tb.cfg["length_seconds"]
    if not shortest <= seconds <= longest:
        sys.exit(f"the recap would be {seconds:.0f}s, outside {shortest}-{longest}s: shorten or lengthen the narration")
    whisper = tb.env("WHISPER_PY")
    tb.run(whisper, "-I", os.path.join(DOODLE, "timing.py"), text, os.path.join(r, "tts", "line_{n:02d}.wav"), tb.GAP,
           os.path.join(r, "timing.json"))
    # the Short: its lines in order, recap lines reused as they were voiced
    sdir = os.path.join(r, "short")
    os.makedirs(sdir, exist_ok=True)
    k_new = iter(new_wavs)
    wavs = [next(k_new) if "new" in s else lines[s["from"] - 1] for s in spec["short"]["lines"]]
    for n, w in enumerate(wavs, 1):
        shutil.copy(w, os.path.join(sdir, f"line_{n:02d}.wav"))
    stext = os.path.join(sdir, "voiceover_en.txt")
    write_lines(stext, short_lines(spec))
    tb.concat([p for k, w in enumerate(wavs) for p in ([gap, w] if k else [w])], os.path.join(sdir, "voice.wav"))
    tb.run(whisper, "-I", os.path.join(DOODLE, "timing.py"), stext, os.path.join(sdir, "line_{n:02d}.wav"), tb.GAP,
           os.path.join(sdir, "timing.json"))
    print(f"voice: recap {tb.duration(voice):.1f}s, Short {tb.duration(os.path.join(sdir, 'voice.wav')):.1f}s, every word clear")


def ease(a):
    a = min(1.0, max(0.0, a))
    return a * a * (3 - 2 * a)


def camera_path(lines, timing, panels, k, view_h, total):
    """Camera top (in scaled strip pixels) as a function of time: each line's panel centred, a panel taller
    than the view scrolled top to bottom while the line is said, and an eased move between panels."""
    secs = timing["sections"]
    shots = []
    for l, s in zip(lines, secs):
        p = panels[l["panel"]]
        top, h = p["top"] * k, p["height"] * k
        if h <= view_h - 80:
            y0 = y1 = top + h / 2 - view_h / 2
        else:
            y0, y1 = top - 40, top + h - view_h + 40
        shots.append((s["offset"], s["offset"] + s["duration"], y0, y1))
    end_t = shots[-1][1]
    shots[-1] = (shots[-1][0], total, shots[-1][2], shots[-1][3])

    def along(i, t):
        s, e, y0, y1 = shots[i]
        return y0 + (y1 - y0) * ease((t - s - MOVE) / max(0.1, e - s - MOVE))

    starts = [along(i - 1, shots[i][0]) if i else shots[0][2] for i in range(len(shots))]

    def cam(t):
        i = max([j for j, sh in enumerate(shots) if sh[0] <= t] or [0])
        y = starts[i] + (along(i, t) - starts[i]) * ease((t - shots[i][0]) / MOVE)
        return y
    return cam, end_t


def events_for(lines, timing):
    ev = []
    for i, (l, s) in enumerate(zip(lines, timing["sections"])):
        start, end = s["offset"], s["offset"] + s["duration"]
        if l.get("mood"):
            ev.append({"t": round(start, 3), "kind": "mood", "mood": l["mood"]})
        if i and l["panel"] != lines[i - 1]["panel"]:
            ev.append({"t": round(max(0, start - 0.15), 3), "kind": "whoosh"})
        if l.get("sting"):
            ev.append({"t": round(start if l["sting"]["at"] == "start" else end + 0.1, 3), "kind": "sting", "name": l["sting"]["name"]})
        if l.get("punch"):
            ev.append({"t": round(s["words"][-1]["t0"], 3), "kind": "punch"})  # word times are absolute
    return sorted(ev, key=lambda e: e["t"])


def sound(work, lines, timing, voice, total, seed):
    events = os.path.join(work, "events.json")
    json.dump(events_for(lines, timing), open(events, "w"), indent=1)
    music = os.path.join(work, "music.wav")
    stings = os.path.join(work, "music_stings.wav")
    if os.path.exists(stings):
        os.remove(stings)
    tb.run(tb.env("TTS_PY"), "-I", os.path.join(DOODLE, "score.py"), music, total + 1, "--events", events, "--seed", seed)
    pad = os.path.join(work, "voice_pad.wav")
    tb.run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", voice, "-af", f"apad=whole_dur={total}", pad)
    mix = os.path.join(work, "mix.m4a")
    tb.run("python3", os.path.join(DOODLE, "mix.py"), pad, music, mix, "--music-gain", tb.cfg["music_gain"], "--events", events,
           *(["--stings", stings] if os.path.exists(stings) else []))
    return mix


def render(ep, work, lines, timing, layout):
    strip = Image.open(os.path.join(ep, "out", "webtoon", "strip.png")).convert("RGB")
    panels = {p["img"]: p for p in json.load(open(os.path.join(ep, "out", "webtoon", "panels.json")))}
    vw, vh, sw = (1920, 1080, 1000) if layout == "landscape" else (1080, 1920, 1080)
    k = sw / strip.width
    fg = strip.resize((sw, round(strip.height * k)), Image.LANCZOS)
    bg_k = 480 / strip.width  # a small blurred copy, scaled up per frame, behind the strip
    bg = ImageEnhance.Brightness(strip.resize((480, round(strip.height * bg_k))).filter(ImageFilter.GaussianBlur(6))).enhance(0.45)
    total = timing["total"] + TAIL
    cam, _ = camera_path(lines, timing, panels, k, vh, total)
    silent = os.path.join(work, "silent.mp4")
    ff = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{vw}x{vh}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                           silent], stdin=subprocess.PIPE)
    for f in range(int(total * FPS)):
        y = min(max(0, cam(f / FPS)), fg.height - vh)
        frame = fg.crop((0, int(y), sw, int(y) + vh))
        if sw < vw:  # the same rows of the small copy, around the frame's centre, stretched to fill it
            half = 480 * vh / vw / 2
            c = min(max((y + vh / 2) / k * bg_k, half), bg.height - half)
            back = bg.crop((0, int(c - half), 480, int(c + half))).resize((vw, vh), Image.BILINEAR)
            back.paste(frame, ((vw - sw) // 2, 0))
            frame = back
        ff.stdin.write(frame.tobytes())
    ff.stdin.close()
    ff.wait()
    return silent, total


def finish(work, silent, mix, timing_path, total, layout, out):
    ass = os.path.join(work, "captions.ass")
    tb.run("python3", os.path.join(DOODLE, "captions.py"), timing_path, ass, "--layout", layout)
    tb.run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", silent, "-i", mix, "-vf",
           f"ass={ass}:fontsdir={os.path.join(DOODLE, 'fonts')}", "-af", f"afade=t=out:st={total - 1.5}:d=1.5", "-shortest",
           "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
           "-movflags", "+faststart", out)


def step_video(ep):
    r, spec = load(ep)
    timing = json.load(open(os.path.join(r, "timing.json")))
    silent, total = render(ep, r, spec["lines"], timing, "landscape")
    mix = sound(r, spec["lines"], timing, os.path.join(r, "voice.wav"), total, 17)
    os.makedirs(os.path.join(r, "out"), exist_ok=True)
    out = os.path.join(r, "out", "recap.mp4")
    finish(r, silent, mix, os.path.join(r, "timing.json"), total, "landscape", out)
    thumbnail(ep, os.path.join(r, "out", "recap_thumbnail.jpg"))
    print(f"recap: {out} ({tb.duration(out):.1f}s)")


def step_short(ep):
    r, spec = load(ep)
    sdir = os.path.join(r, "short")
    timing = json.load(open(os.path.join(sdir, "timing.json")))
    lines = short_lines(spec)
    silent, total = render(ep, sdir, lines, timing, "vertical")
    mix = sound(sdir, lines, timing, os.path.join(sdir, "voice.wav"), total, 29)
    out = os.path.join(r, "out", "short.mp4")
    finish(sdir, silent, mix, os.path.join(sdir, "timing.json"), total, "vertical", out)
    print(f"short: {out} ({tb.duration(out):.1f}s)")


def thumbnail(ep, out):
    """1280x720: glowing Viktor on the left, deadpan Arjun on the right, the hook in big letters."""
    img = os.path.join(ep, "out", "img")
    t = Image.new("RGB", (1280, 720), "#111")
    v = Image.open(os.path.join(img, "p19.png")).convert("RGB")
    v = v.crop((0, 0, 832, 1170)).resize((512, 720), Image.LANCZOS)
    a = Image.open(os.path.join(img, "p30.png")).convert("RGB").resize((720, 720), Image.LANCZOS)
    t.paste(a, (560, 0))
    t.paste(v, (0, 0))
    band = Image.new("RGBA", t.size, (0, 0, 0, 0))
    ImageDraw.Draw(band).rectangle([0, 575, 1280, 720], fill=(0, 0, 0, 170))
    t = Image.alpha_composite(t.convert("RGBA"), band).convert("RGB")
    d = ImageDraw.Draw(t)
    big = ImageFont.truetype(os.path.join(HERE, "fonts", "Bangers-Regular.ttf"), 112)
    parts = [("HIS TEA = ", "white"), ("1 HOUR OF POWER", "#ffd43b")]
    x = (1280 - sum(big.getlength(p) for p, _ in parts)) / 2
    for text, fill in parts:  # one line along the bottom, clear of both faces
        d.text((x, 588), text, font=big, fill=fill, stroke_width=8, stroke_fill="black")
        x += big.getlength(text)
    t.save(out, quality=90)


def step_upload(ep):
    r, spec = load(ep)
    m = spec["meta"]
    out = os.path.abspath(os.path.join(r, "out"))
    note = "\n\nThe voice is an AI copy of my own voice, the pictures are made with an AI image model, and the music is original."
    playlist = lambda key: tb.cfg.get("playlists", {}).get(key, {}).get("id")
    videos = [{"file": os.path.join(out, "recap.mp4"), "thumbnail": os.path.join(out, "recap_thumbnail.jpg"),
               "title": m["title"], "description": m["description"] + note, "tags": m["tags"], "publish_at": m["long_at"],
               "playlists": [p for p in [playlist("long")] if p]},
              {"file": os.path.join(out, "short.mp4"), "title": m["short"]["title"], "description": m["short"]["description"] + note,
               "tags": m["tags"][:5] + ["shorts"], "publish_at": m["short_at"], "playlists": [p for p in [playlist("shorts")] if p]}]
    upload = {"defaults": {"privacy": "private", "made_for_kids": False, "ai_content": True, "category_id": 24, "language": "en",
                           "refresh_token_env": tb.cfg["channel"]["refresh_token_env"]}, "videos": videos}
    path = os.path.join(r, "upload.json")
    json.dump(upload, open(path, "w"), indent=2, ensure_ascii=False)
    print(f"wrote {path}: upload with python3 {os.path.join(DOODLE, 'upload.py')} {path}")


STEPS = {"voice": step_voice, "video": step_video, "short": step_short, "upload": step_upload}
if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in STEPS:
        sys.exit(__doc__)
    STEPS[sys.argv[1]](os.path.abspath(sys.argv[2]))
