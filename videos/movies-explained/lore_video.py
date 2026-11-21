"""A vertical lore video (1080x1920, a 30-second Short up to 3 minutes) from a script's voice pieces, our own pictures and our own sound:
pictures that move (slow zooms and pans, a small punch-in on every cut), big captions a few words at a time,
"ONE / TWO / THREE" cards, name cards, original music (doodle/score.py), whooshes and booms made here, loudness
-14 LUFS. Nothing in it comes from a film, a comic or anyone else's video.

    python3 lore_video.py WORK_DIR LANG [--only-plan]

WORK_DIR holds:
  shots.json          {"sections": [{"mood": "curious", "items": [{"pic": "k_intro", "w": 1.3}, {"pic": "p01"}, ...],
                                     "cards": [{"text": "ONE", "f": 0.0}], "names": [{"text": "DOCTOR DOOM",
                                     "color": "2E7D32", "f": 0.1}]}, ...],
                       "caption_replace": {"ta": [["spoken words", "shown"], ...]}}
                      One section per script line. "w" is a picture's share of its section (default 1); "f" is where in
                      the section a card or name appears (0 = its start, 1 = its end). A card's "text" may be a dict
                      {"en": "...", "ta": "..."}.
  pics/NAME.png       the pictures (9:16)
  voice_LANG/sec_NN.wav   the voice pieces, one per script line (kural/eleven.py)
  script_LANG.txt     the script (one line per section, emotion tags in [brackets]): the captions' words
Writes WORK_DIR/out/LANG/video.mp4 (and its parts in the same folder).
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "doodle"))
from voicefx import VOICE_CLEAR, shorten_pauses  # noqa: E402  (the owner's pick of 21 Nov 2026: "B ok")

CFG = json.load(open(os.path.join(HERE, "config.json")))
# the music bed: "beat" (a steady beat with no tune under the whole Short, the owner's choice of 21 Nov 2026) or
# "score" (the story moods of doodle/score.py); with "beat", a warm or sad section gets the softer beat
BEAT_FOR = {"warm": "beat_warm", "sad": "beat_warm"}
MUSIC_UNDER_VOICE_DB = 9  # the bed 9 dB under the voice's average: about 20 dB under it in the gaps between words (theirs: 15)
W, H, FPS = 1080, 1920, 30
SR = 44100
GAP = 0.18  # silence between sections
LEAD, TAIL = 0.25, 1.2
FONTS = os.path.join(HERE, "fonts")
FONT = {"en": "Bangers", "ta": "Mukta Malar ExtraBold"}
CAP_SIZE = {"en": 118, "ta": 92}
YELLOW = "&H0035D7FF&"  # ASS colours are &HAABBGGRR


def run(*cmd):
    subprocess.run([str(c) for c in cmd], check=True)


def load(path):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le",
                          "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def save(path, a, channels=1):
    run_in = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "f32le", "-ac", str(channels), "-ar",
                             str(SR), "-i", "-", path], input=np.asarray(a, np.float32).tobytes(), check=True)
    return run_in


def speech_spans(a, frame=0.02, gap=0.25):
    """(start, end) seconds of speech in a; pauses shorter than gap are joined (as in teabreak/tamil.py)."""
    n = int(frame * SR)
    rms = np.array([np.sqrt(np.mean(a[i:i + n] ** 2)) for i in range(0, len(a) - n, n)])
    on = rms > max(0.01, rms.max() * 0.05)
    spans, start = [], None
    for k, v in enumerate(on):
        if v and start is None:
            start = k * frame
        if not v and start is not None:
            spans.append([start, k * frame])
            start = None
    if start is not None:
        spans.append([start, len(on) * frame])
    merged = [spans[0]]
    for s in spans[1:]:
        if s[0] - merged[-1][1] < gap:
            merged[-1][1] = s[1]
        else:
            merged.append(s)
    return merged


def word_times(words, spans):
    """Spread the words over the speech by their length, so a pause carries no word."""
    weight = [len(w) + (3 if re.search(r"[.,?!:]$", w) else 0) for w in words]
    total_w, speech = sum(weight), sum(e - s for s, e in spans)

    def at(x):
        for s, e in spans:
            if x <= e - s:
                return s + x
            x -= e - s
        return spans[-1][1]
    out, acc = [], 0.0
    for w, k in zip(words, weight):
        t0 = at(acc / total_w * speech)
        acc += k
        t1 = at(acc / total_w * speech - 0.02)
        out.append({"w": w, "t0": t0, "t1": max(t1, t0 + 0.05)})
    return out


def replace_phrases(words, table):
    """Spoken phrases shown another way in the captions (a year said in words shown as digits)."""
    strip = lambda w: re.sub(r"[.,?!:;\"]+$", "", w)
    phrases = sorted((([strip(x) for x in p.split()], v) for p, v in table), key=lambda r: -len(r[0]))
    out, i = [], 0
    while i < len(words):
        for p, v in phrases:
            if [strip(w["w"]) for w in words[i:i + len(p)]] == p:
                last = words[i + len(p) - 1]
                out.append({"w": v + last["w"][len(strip(last["w"])):], "t0": words[i]["t0"], "t1": last["t1"]})
                i += len(p)
                break
        else:
            out.append(words[i])
            i += 1
    return out


def chunks(words, lang):
    """Caption groups of 1-3 words (shorter for Tamil, whose words are long), split after punctuation."""
    out, cur = [], []
    limit = 14 if lang == "ta" else 16
    for w in words:
        cur.append(w)
        text = " ".join(x["w"] for x in cur)
        if re.search(r"[.,?!:]$", w["w"]) or len(cur) == 3 or len(text) >= limit:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def ass_time(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def pick(v, lang):
    return v.get(lang, v.get("en")) if isinstance(v, dict) else v


def is_key(word, lang, first):
    w = re.sub(r"[^\w\-]", "", word)
    if re.search(r"\d", w):
        return True
    return lang == "en" and not first and w[:1].isupper() and w.lower() not in {"i", "i'm", "iron"}


def subtitles(path, lang, caps, cards, names, total):
    font = FONT[lang]
    sp = 1 if lang == "en" else 0  # letter spacing breaks the shaping of Tamil letters in libass: none for Tamil
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},{CAP_SIZE[lang]},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,{sp},0,1,9,4,5,60,60,0,1
Style: Card,{FONT['en'] if lang == 'en' else font},{210 if lang == 'en' else 170},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,{sp * 2},0,1,12,6,5,40,40,0,1
Style: Name,{font},{88 if lang == 'en' else 72},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,{sp * 2},0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    for group, (t0, t1) in caps:
        parts = []
        for k, w in enumerate(group):
            txt = w["w"].replace("{", "").replace("}", "")
            parts.append(("{\\c" + YELLOW + "}" + txt + "{\\c&H00FFFFFF&}") if is_key(txt, lang, w.get("start")) else txt)
        ev.append(f"Dialogue: 1,{ass_time(t0)},{ass_time(t1)},Cap,,0,0,0,,{{\\pos({W // 2},1390)\\fscx118\\fscy118\\t(0,90,\\fscx100\\fscy100)}}" + " ".join(parts))
    for c in cards:
        t0 = c["t"]
        col = c.get("color", "35D7FF")
        bgr = col[4:6] + col[2:4] + col[0:2]
        ev.append(f"Dialogue: 2,{ass_time(t0)},{ass_time(t0 + c.get('dur', 1.3))},Card,,0,0,0,,{{\\pos({W // 2},820)\\fad(60,180)\\c&H00{bgr}&\\fscx150\\fscy150\\t(0,140,\\fscx100\\fscy100)}}{c['text']}")
    for n in names:
        t0, t1 = n["t"], n["t"] + n.get("dur", 2.6)
        col = n.get("color", "2E7D32")
        bgr = col[4:6] + col[2:4] + col[0:2]
        text = n["text"]
        width = int(len(text) * (44 if lang == "en" else 30)) + 80
        x0, y0 = 60, 240
        box = f"m 0 0 l {width} 0 {width} 130 0 130"
        ev.append(f"Dialogue: 3,{ass_time(t0)},{ass_time(t1)},Name,,0,0,0,,{{\\an7\\move({x0 - 400},{y0},{x0},{y0},0,180)\\fad(0,200)\\p1\\bord0\\shad0\\1c&H00{bgr}&\\1a&H10&}}{box}{{\\p0}}")
        ev.append(f"Dialogue: 3,{ass_time(t0)},{ass_time(t1)},Name,,0,0,0,,{{\\an7\\move({x0 - 400},{y0 + 8},{x0},{y0 + 8},0,180)\\fad(0,200)\\p1\\bord0\\shad0\\1c&H00FFFFFF&}}m 0 0 l 14 0 14 114 0 114{{\\p0}}")
        ev.append(f"Dialogue: 4,{ass_time(t0)},{ass_time(t1)},Name,,0,0,0,,{{\\an4\\move({x0 + 40 - 400},{y0 + 66},{x0 + 40},{y0 + 66},0,180)\\fad(0,200)}}{text}")
    open(path, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")


def still(img, out, dur, k):
    """One picture as a moving shot: zoom in, zoom out, drift up or drift down, with a punch-in at the start."""
    n = max(2, int(round(dur * FPS)))
    moves = [
        ("1.04+0.10*on/{n}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
        ("1.16-0.10*on/{n}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
        ("1.12", "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*(0.85-0.7*on/{n})"),
        ("1.12", "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*(0.15+0.7*on/{n})"),
    ]
    z, x, y = (s.format(n=n) for s in moves[k % 4])
    z = f"({z})*(1+0.05*max(0,1-on/5))"
    vf = (f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,crop={W * 2}:{H * 2},"
          f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={W}x{H}:fps={FPS},"
          f"eq=contrast=1.04:saturation=1.08,format=yuv420p")
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-loop", "1", "-i", img, "-vf", vf, "-frames:v", n, "-c:v", "libx264",
        "-preset", "veryfast", "-crf", "18", out)


def whoosh(seconds=0.35, seed=0):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    noise = rng.standard_normal(n).astype(np.float32)
    out = np.zeros(n, np.float32)
    lp = 0.0
    t = np.arange(n) / n
    alpha = 0.02 + 0.5 * np.sin(np.pi * t) ** 2  # the filter opens and closes: a swish
    for i in range(n):
        lp += alpha[i] * (noise[i] - lp)
        out[i] = lp
    env = np.sin(np.pi * t) ** 1.5
    out = out * env
    return out / (np.abs(out).max() + 1e-9)


def boom(seconds=1.2):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    f = 46 + 30 * np.exp(-t * 8)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    rng = np.random.default_rng(3)
    hit = rng.standard_normal(n) * np.exp(-t * 30) * 0.4
    out = (tone + hit).astype(np.float32)
    return out / (np.abs(out).max() + 1e-9)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work")
    ap.add_argument("lang")
    ap.add_argument("--only-plan", action="store_true")
    a = ap.parse_args()
    work, lang = os.path.abspath(a.work), a.lang
    spec = json.load(open(os.path.join(work, "shots.json")))
    lines = [l.strip() for l in open(os.path.join(work, f"script_{lang}.txt"), encoding="utf-8") if l.strip()]
    secs = spec["sections"]
    if len(secs) != len(lines):
        sys.exit(f"shots.json has {len(secs)} sections, the script {len(lines)} lines")
    out = os.path.join(work, "out", lang)
    os.makedirs(out, exist_ok=True)

    # 1) the voice on one timeline, and where every section and word falls
    voice, t, plan, words_all = [np.zeros(int(LEAD * SR), np.float32)], LEAD, [], []
    table = spec.get("caption_replace", {}).get(lang, [])
    for i, line in enumerate(lines):
        # long pauses inside a line shortened, so the voice keeps moving (the pictures follow this timing)
        piece = shorten_pauses(load(os.path.join(work, f"voice_{lang}", f"sec_{i + 1:02d}.wav")), SR)
        dur = len(piece) / SR
        text = re.sub(r"^\[[a-z]+\]\s*", "", line)
        ws = word_times(text.split(), speech_spans(piece))
        for k, w in enumerate(ws):  # a word that starts a sentence is capitalised anyway: not a name
            w["start"] = k == 0 or bool(re.search(r"[.?!:]$", ws[k - 1]["w"]))
            w["t0"] += t
            w["t1"] += t
        words_all += replace_phrases(ws, table)
        plan.append({"t0": t, "t1": t + dur + GAP})
        voice += [piece, np.zeros(int(GAP * SR), np.float32)]
        t += dur + GAP
    total = t + TAIL
    voice.append(np.zeros(int(TAIL * SR), np.float32))
    voice = np.concatenate(voice)

    # 2) the pictures: each section's span shared by its pictures' weights; cuts snap to whole frames
    shots = []
    for s, p in zip(secs, plan):
        span = p["t1"] - p["t0"] if p is not plan[-1] else total - p["t0"]
        wsum = sum(it.get("w", 1) for it in s["items"])
        at = p["t0"]
        for it in s["items"]:
            d = span * it.get("w", 1) / wsum
            shots.append({"pic": it["pic"], "t0": at, "t1": at + d})
            at += d
    shots[0]["t0"] = 0.0
    frames = [round(x["t0"] * FPS) for x in shots] + [round(total * FPS)]
    cards, names = [], []
    for s, p in zip(secs, plan):
        for c in s.get("cards", []):
            cards.append(dict(c, text=pick(c["text"], lang), t=p["t0"] + c.get("f", 0) * (p["t1"] - p["t0"])))
        for n in s.get("names", []):
            names.append(dict(n, text=pick(n["text"], lang), t=p["t0"] + n.get("f", 0) * (p["t1"] - p["t0"])))
    caps = []
    for g in chunks(words_all, lang):
        caps.append((g, (g[0]["t0"], g[-1]["t1"] + 0.08)))
    for k in range(len(caps) - 1):  # a caption stays up until the next one starts (no flicker)
        g, (t0, t1) = caps[k]
        nxt = caps[k + 1][1][0]
        caps[k] = (g, (t0, nxt if nxt - t1 < 0.6 else t1))
    json.dump({"total": total, "sections": plan, "shots": shots, "cards": cards, "names": names},
              open(os.path.join(out, "plan.json"), "w"), indent=1, ensure_ascii=False)
    print(f"{lang}: {total:.1f} s, {len(shots)} pictures, {len(caps)} captions, {len(cards)} cards, {len(names)} names")
    if a.only_plan:
        return

    # 3) picture shots, joined with hard cuts
    parts = []
    for k, s in enumerate(shots):
        part = os.path.join(out, f"shot_{k:02d}.mp4")
        img = os.path.join(work, "pics", s["pic"] + ".png")
        key = f"{img} {os.path.getmtime(img)} {frames[k + 1] - frames[k]} {k % 4}"
        stamp = part + ".src"
        if not (os.path.exists(part) and os.path.exists(stamp) and open(stamp).read() == key):  # unchanged shots are kept
            still(img, part, (frames[k + 1] - frames[k]) / FPS, k)
            open(stamp, "w").write(key)
        parts.append(part)
    lst = os.path.join(out, "shots.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    picture = os.path.join(out, "picture.mp4")
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", picture)

    # 4) sound: voice, our own music in the sections' moods, a whoosh on every cut, a boom on every card
    beat = CFG.get("music_style", "score") == "beat"
    mood = lambda s: (BEAT_FOR.get(s.get("mood"), "beat") if beat else s.get("mood", "suspense"))
    events = [{"kind": "mood", "t": round(p["t0"] if i else 0.0, 2), "mood": mood(s)}
              for i, (s, p) in enumerate(zip(secs, plan))]
    ev_path = os.path.join(out, "events.json")
    json.dump(events, open(ev_path, "w"))
    music_path = os.path.join(out, "music.wav")
    run("python3", os.path.join(HERE, "..", "doodle", "score.py"), music_path, f"{total:.2f}", "--events", ev_path,
        "--seed", "11")
    # the voice made clear for phone speakers (voicefx.py), then the music: an even bed under the whole Short,
    # MUSIC_UNDER_VOICE_DB below the voice, its sub-bass and its 1-4 kHz (where the words are) turned down, and only a
    # slow, gentle dip under speech, so it never jumps up in the pauses
    raw_voice, clear_voice = os.path.join(out, "voice_raw.wav"), os.path.join(out, "voice_clear.wav")
    save(raw_voice, voice)
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", raw_voice, "-af", VOICE_CLEAR, clear_voice)
    voice = load(clear_voice)[: len(voice)]
    bed = os.path.join(out, "music_bed.wav")
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", music_path, "-af",
        "highpass=f=60,equalizer=f=2000:t=q:w=1.5:g=-5", bed)
    music = load(bed)[: len(voice)]
    music = np.pad(music, (0, max(0, len(voice) - len(music))))
    talking = np.abs(voice) > 1e-3
    v_rms = np.sqrt(np.mean(voice[talking] ** 2)) if talking.any() else 0.1
    m_rms = np.sqrt(np.mean(music ** 2)) + 1e-9
    music *= v_rms * 10 ** (-MUSIC_UNDER_VOICE_DB / 20) / m_rms / 0.55
    env = np.convolve(np.abs(voice), np.ones(int(0.6 * SR)) / int(0.6 * SR), mode="same")
    duck = 1.0 - 0.2 * np.clip(env / (env.max() * 0.25 + 1e-9), 0, 1)
    fx = np.zeros_like(voice)
    sw = whoosh()
    for k, s in enumerate(shots[1:], 1):
        i = max(0, int(frames[k] / FPS * SR) - int(0.2 * SR))
        seg = sw[: len(fx) - i]
        fx[i:i + len(seg)] += 0.22 * seg
    bm = boom()
    for c in cards:
        i = int(c["t"] * SR)
        seg = bm[: len(fx) - i]
        fx[i:i + len(seg)] += 0.5 * seg
    mix = voice * 1.0 + music * duck * 0.55 + fx
    mix_path = os.path.join(out, "mix.wav")
    save(mix_path, mix)

    # 5) captions and cards on top, the sound, loudness -14 LUFS
    ass = os.path.join(out, "captions.ass")
    subtitles(ass, lang, caps, cards, names, total)
    video = os.path.join(out, "video.mp4")
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", picture, "-i", mix_path, "-vf",
        f"ass={ass}:fontsdir={FONTS}:shaping=complex", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "libx264", "-preset", "medium",
        "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", video)
    print(f"done: {video}")


if __name__ == "__main__":
    main()
