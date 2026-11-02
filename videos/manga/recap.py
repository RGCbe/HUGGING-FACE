"""A YouTube recap of a lettered episode, in Manoj's voice, plus a vertical Short.

    python3 recap.py STEP EPISODE_DIR        (STEP: voice, video, short, tiktok, upload)

EPISODE_DIR/recap/recap.json holds the narration: "lines" [{"panel", "text", "mood"?, "sting"?, "punch"?, "chapter"?}]
where panel is a panel name from the lettered strip (letter.py's panels.json; "end" is the closing card),
mood a score.py mood that starts with the line, sting {"name", "at": "start" | "end"} a score.py hit, punch
stops the music just before the line's last word, and chapter starts a YouTube chapter at the line. "short"
lists the Short's lines: {"from": N} reuses line N of the recap, {"new": {...}} is a line voiced only for the
Short. "meta" has the titles, descriptions, tags and publish times; "length_seconds" [min, max] overrides the
Tea Break limits for the recap; "tiktok_parts" N cuts the TikTok version into N about-equal parts (each at
least 61 s); "voice_engine" ("eleven": the owner's ElevenLabs clone) picks the voice over env.sh's TTS_ENGINE.

  voice   voices the lines with ../teabreak/build.py's say() (every word checked) and times them
  video   the 1920x1080 recap: the strip in the middle over a blurred copy of itself, the camera moving
          to each line's panel and down tall ones; mood music, stings, whooshes, captions; a thumbnail
  short   the 1080x1920 Short, the strip full width
  tiktok  the whole recap as vertical TikTok parts, each just over a minute, with end cards
  upload  writes upload.json for ../doodle/upload.py, both videos private until their times

Needs the Tea Break voice setup (source ~/.cache/tea-break/env.sh) and letter.py's out/webtoon/strip.png.
"""
import ast
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
ZOOM = 0.05  # how far a still panel zooms in over its shot


def music_names():
    """score.py's MOODS and STINGS, read without importing it (it needs the TTS environment)."""
    tree = ast.parse(open(os.path.join(DOODLE, "score.py")).read())
    return {t.id: ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
            for t in n.targets if isinstance(t, ast.Name) and t.id in ("MOODS", "STINGS")}


def load(ep):
    r = os.path.join(ep, "recap")
    spec = json.load(open(os.path.join(r, "recap.json")))
    # a line's "mood" is the music under it, not the voice tag: catch a wrong one before hours of voicing
    names = music_names()
    for l in spec["lines"] + short_lines(spec):
        bad = [x for x in [l.get("mood")] if x and x not in names["MOODS"]] + \
              [x for x in [(l.get("sting") or {}).get("name")] if x and x not in names["STINGS"]]
        if bad:
            sys.exit(f"{ep}: music {bad} in {l['text'][:50]!r}: moods are {names['MOODS']}, stings {names['STINGS']}")
    return r, spec


def write_lines(path, lines):
    open(path, "w", encoding="utf-8").write("\n".join(l["text"] for l in lines) + "\n")


def short_lines(spec):
    return [s["new"] if "new" in s else dict(spec["lines"][s["from"] - 1], **{k: v for k, v in s.items() if k != "from"})
            for s in spec["short"]["lines"]]


def step_voice(ep):
    r, spec = load(ep)
    if spec.get("voice_engine"):  # the review's own voice wins over the machine default (env.sh's TTS_ENGINE)
        os.environ["TTS_ENGINE"] = spec["voice_engine"]
    print(f"voice: {os.environ.get('TTS_ENGINE', tb.cfg['voice_engine'])}")
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
    shortest, longest = spec.get("length_seconds", tb.cfg["length_seconds"])
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
    """The camera as a function of time: (top in scaled strip pixels, zoom). Lines in a row on the same panel are
    one shot. A panel that fits the view is centred and slowly zoomed into (ZOOM by the end of the shot), so a long
    explanation never sits on a frozen picture; a taller panel is scrolled top to bottom; an eased move between."""
    shots = []
    for l, s in zip(lines, timing["sections"]):
        end = s["offset"] + s["duration"]
        if shots and shots[-1]["panel"] == l["panel"]:
            shots[-1]["end"] = end
            continue
        p = panels[l["panel"]]
        top, h = p["top"] * k, p["height"] * k
        still = h <= view_h - 80
        y0, y1 = (top + h / 2 - view_h / 2,) * 2 if still else (top - 40, top + h - view_h + 40)
        shots.append({"panel": l["panel"], "start": s["offset"], "end": end, "y0": y0, "y1": y1, "zoom": ZOOM if still else 0})
    end_t = shots[-1]["end"]
    shots[-1]["end"] = total

    def at(i, t):
        sh = shots[i]
        y = sh["y0"] + (sh["y1"] - sh["y0"]) * ease((t - sh["start"] - MOVE) / max(0.1, sh["end"] - sh["start"] - MOVE))
        z = 1 + sh["zoom"] * min(1.0, max(0.0, (t - sh["start"]) / max(0.1, sh["end"] - sh["start"])))
        return y, z

    starts = [at(i - 1, sh["start"]) if i else at(0, sh["start"]) for i, sh in enumerate(shots)]

    def cam(t):
        i = max([j for j, sh in enumerate(shots) if sh["start"] <= t] or [0])
        (by, bz), (y, z) = starts[i], at(i, t)
        a = ease((t - shots[i]["start"]) / MOVE)
        return by + (y - by) * a, bz + (z - bz) * a
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
        y, z = cam(f / FPS)
        y = min(max(0, y), fg.height - vh)
        if z > 1.0005:  # zoomed: the strip column grows wider where there is room (16:9), else its sides are cut
            src_w, src_h = min(sw, vw / z), vh / z
            out_w = min(vw, round(src_w * z))
            x0, y0 = (sw - src_w) / 2, y + (vh - src_h) / 2
            frame = fg.transform((out_w, vh), Image.EXTENT, (x0, y0, x0 + src_w, y0 + src_h), Image.BILINEAR)
        else:
            frame, out_w = fg.crop((0, int(y), sw, int(y) + vh)), sw
        if out_w < vw:  # the same rows of the small copy, around the frame's centre, stretched to fill it
            half = 480 * vh / vw / 2
            c = min(max((y + vh / 2) / k * bg_k, half), bg.height - half)
            back = bg.crop((0, int(c - half), 480, int(c + half))).resize((vw, vh), Image.BILINEAR)
            back.paste(frame, ((vw - out_w) // 2, 0))
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
    thumbnail(ep, os.path.join(r, "out", "recap_thumbnail.jpg"), spec)
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


def step_tiktok(ep):
    """The whole recap as vertical parts for TikTok, each just over a minute (TikTok rewards only longer
    videos): cut in the pauses between lines, "PART n/N" along the top, and a 2.5 s end card pointing to
    the next part, or to WEBTOON after the last."""
    r, spec = load(ep)
    work = os.path.join(r, "tiktok")
    os.makedirs(work, exist_ok=True)
    timing = json.load(open(os.path.join(r, "timing.json")))
    silent, total = os.path.join(work, "silent.mp4"), timing["total"] + TAIL
    if not os.path.exists(silent):  # the pictures only change with the strip or the voice: delete it to redraw
        silent, total = render(ep, work, spec["lines"], timing, "vertical")
    # TikTok covers the top ~150 px (tabs) and the bottom ~500 px (name, caption, sound): keep text between
    ass = os.path.join(work, "captions.ass")
    tb.run("python3", os.path.join(DOODLE, "captions.py"), os.path.join(r, "timing.json"), ass, "--layout", "vertical",
           "--margin", 560)
    full = os.path.join(work, "full.mp4")
    tb.run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", silent, "-i", os.path.join(r, "mix.m4a"), "-vf",
           f"ass={ass}:fontsdir={os.path.join(DOODLE, 'fonts')}", "-shortest", "-c:v", "libx264", "-preset", "medium",
           "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", full)
    secs = timing["sections"]
    pauses = [(secs[i]["offset"] + secs[i]["duration"] + secs[i + 1]["offset"]) / 2 for i in range(len(secs) - 1)]
    parts = spec.get("tiktok_parts")
    if parts:  # that many parts of about equal length: each cut in the pause nearest its share of the whole
        bounds = [0.0] + [min(pauses, key=lambda p: abs(p - total * k / parts)) for k in range(1, parts)] + [total]
        short = [round(b - a, 1) for a, b in zip(bounds, bounds[1:]) if b - a < 61]
        if short or bounds != sorted(set(bounds)):
            sys.exit(f"{parts} TikTok parts would leave parts under 61 s ({short}): ask for fewer")
    else:  # a cut in the pause after the first line that makes the part over 61.5 s
        bounds = [0.0]
        for mid in pauses:
            if mid - bounds[-1] >= 61.5 and total - mid >= 58:
                bounds.append(mid)
        bounds.append(total)
    n = len(bounds) - 1
    font = os.path.join(HERE, "fonts", "Bangers-Regular.ttf")
    out_dir = os.path.join(r, "out")
    for k in range(n):
        card = os.path.join(work, f"card{k + 1}.png")
        end_card(ep, card, [("PART " + str(k + 2) + " IS NEXT", "#ffd43b"), ("FOLLOW SO YOU", "white"), ("DON'T MISS IT!", "white")]
                 if k + 1 < n else [("READ IT FREE", "#ffd43b"), ("ON WEBTOON", "white"), ("THE F-RANK TEA SELLER", "white")])
        a, b = bounds[k], bounds[k + 1]
        label = os.path.join(work, f"label{k + 1}.txt")
        open(label, "w").write(f"PART {k + 1}/{n}  ·  THE F-RANK TEA SELLER")
        out = os.path.join(out_dir, f"tiktok_part{k + 1}.mp4")
        graph = (f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,drawtext=fontfile={font}:textfile={label}:fontsize=58:fontcolor=white:"
                 f"box=1:boxcolor=black@0.6:boxborderw=18:x=(w-text_w)/2:y=190[body];"
                 f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.3,afade=t=out:st={b - a - 0.4}:d=0.4[bodya];"
                 f"[1:v]scale=1080:1920,setsar=1,fps={FPS},format=yuv420p[cardv];"
                 f"[2:a]atrim={min(b, total - 2.5)}:{min(b, total - 2.5) + 2.5},asetpts=PTS-STARTPTS,volume=0.35,"
                 f"afade=t=in:d=0.3,afade=t=out:st=1.8:d=0.7,aformat=sample_rates=44100:channel_layouts=stereo[carda];"
                 f"[bodya]aformat=sample_rates=44100:channel_layouts=stereo[bodya2];"
                 f"[body][bodya2][cardv][carda]concat=n=2:v=1:a=1[v][aout]")
        tb.run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", full, "-loop", "1", "-t", "2.5", "-i", card,
               "-i", os.path.join(r, "music.wav"), "-filter_complex", graph, "-map", "[v]", "-map", "[aout]",
               "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
               "-movflags", "+faststart", out)
        print(f"tiktok part {k + 1}: {out} ({tb.duration(out):.1f}s)")
    k = n + 1  # parts left over from an earlier cut into more parts
    while os.path.exists(os.path.join(out_dir, f"tiktok_part{k}.mp4")):
        os.remove(os.path.join(out_dir, f"tiktok_part{k}.mp4"))
        k += 1


def series_cover(ep, name):
    """A series cover (thumb-square.jpg, thumb-vertical.jpg): the episode's own pack, else Episode 1's, where
    the series covers were made."""
    own = os.path.join(ep, "upload", name)
    return own if os.path.exists(own) else os.path.join(os.path.dirname(os.path.abspath(ep)), "ep01", "upload", name)


def end_card(ep, out, lines):
    """1080x1920: the series cover in the middle of a dark page, three lines of big text under it."""
    card = Image.new("RGB", (1080, 1920), "#0d0d0f")
    cover = Image.open(series_cover(ep, "thumb-square.jpg")).convert("RGB").resize((900, 900), Image.LANCZOS)
    card.paste(cover, (90, 260))
    d = ImageDraw.Draw(card)
    big = ImageFont.truetype(os.path.join(HERE, "fonts", "Bangers-Regular.ttf"), 110)
    y = 1240
    for text, fill in lines:
        size = big if big.getlength(text) < 1000 else ImageFont.truetype(big.path, 84)
        d.text(((1080 - size.getlength(text)) / 2, y), text, font=size, fill=fill, stroke_width=6, stroke_fill="black")
        y += 130
    card.save(out)


def thumbnail(ep, out, spec=None):
    """1280x720: one panel on the left, another on the right, the hook in big letters along the bottom
    (recap.json meta "thumbnail": {"left", "right", "text": [[words, colour], ...]}; Episode 1's by default:
    glowing Viktor, deadpan Arjun, HIS TEA = 1 HOUR OF POWER)."""
    th = (spec or {}).get("meta", {}).get("thumbnail", {})
    img = os.path.join(ep, "out", "img")
    t = Image.new("RGB", (1280, 720), "#111")
    v = Image.open(os.path.join(img, th.get("left", "p19") + ".png")).convert("RGB")
    v = v.crop((0, 0, v.width, min(v.height, round(v.width * 720 / 512)))).resize((512, 720), Image.LANCZOS)
    a = Image.open(os.path.join(img, th.get("right", "p30") + ".png")).convert("RGB")
    side = min(a.size)
    a = a.crop(((a.width - side) // 2, 0, (a.width + side) // 2, side)).resize((720, 720), Image.LANCZOS)
    t.paste(a, (560, 0))
    t.paste(v, (0, 0))
    band = Image.new("RGBA", t.size, (0, 0, 0, 0))
    ImageDraw.Draw(band).rectangle([0, 575, 1280, 720], fill=(0, 0, 0, 170))
    t = Image.alpha_composite(t.convert("RGBA"), band).convert("RGB")
    d = ImageDraw.Draw(t)
    big = ImageFont.truetype(os.path.join(HERE, "fonts", "Bangers-Regular.ttf"), 112)
    parts = th.get("text", [("HIS TEA = ", "white"), ("1 HOUR OF POWER", "#ffd43b")])
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
    timing = json.load(open(os.path.join(r, "timing.json")))
    marks = [(0 if not k else s["offset"], l["chapter"]) for k, (l, s) in
             enumerate((l, s) for l, s in zip(spec["lines"], timing["sections"]) if l.get("chapter"))]
    chapters = ("\n\nChapters\n" + "\n".join(f"{int(t // 60)}:{int(t % 60):02d} {name}" for t, name in marks)
                if len(marks) >= 3 else "")  # YouTube needs three or more, the first at 0:00
    # never the Tea Break playlists: they promise "every word is true", and this is fiction ("playlists" in
    # recap.json's meta may name the series' own playlist ids)
    videos = [{"file": os.path.join(out, "recap.mp4"), "thumbnail": os.path.join(out, "recap_thumbnail.jpg"),
               "title": m["title"], "description": m["description"] + chapters + note, "tags": m["tags"], "publish_at": m["long_at"],
               "playlists": m.get("playlists", [])},
              {"file": os.path.join(out, "short.mp4"), "title": m["short"]["title"], "description": m["short"]["description"] + note,
               "tags": m["tags"][:5] + ["shorts"], "publish_at": m["short_at"], "playlists": m.get("playlists", [])}]
    upload = {"defaults": {"privacy": "private", "made_for_kids": False, "ai_content": True, "category_id": 24, "language": "en",
                           "refresh_token_env": tb.cfg["channel"]["refresh_token_env"]}, "videos": videos}
    path = os.path.join(r, "upload.json")
    json.dump(upload, open(path, "w"), indent=2, ensure_ascii=False)
    print(f"wrote {path}: upload with python3 {os.path.join(DOODLE, 'upload.py')} {path}")


STEPS = {"voice": step_voice, "video": step_video, "short": step_short, "tiktok": step_tiktok, "upload": step_upload}
if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in STEPS:
        sys.exit(__doc__)
    STEPS[sys.argv[1]](os.path.abspath(sys.argv[2]))
