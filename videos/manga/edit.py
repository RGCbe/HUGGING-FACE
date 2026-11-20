"""Cut a movie-version episode together: every shot in order, timed to its voice line, with the cards made in the
edit, the voices, sound effects, an original score that ducks under the speech, and burned-in English subtitles.

    python3 edit.py SHOTS.json OUT.mp4 [--work DIR]

Per shot, the picture comes from (in this order): out/clips/SNN_a.mp4 (AI motion, 832x480, upscaled),
out/camera/SNN.mp4 (camera move), or a camera move made on the spot from out/keyframes_ok/SNN.jpg; cards
("kind": "edit") are made here. The voice lines are voice/SNN.wav, the effects out/sfx/SNN.mp3, all next to SHOTS.
A shot lasts its planned length, or longer if its line needs it (the line starts 0.3 s in, plus 0.5 s after it).
Music: videos/doodle/score.py with the moods below; mix: videos/doodle/mix.py (ducking, punchline silences).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DOODLE = os.path.join(HERE, "..", "doodle")
sys.path.insert(0, HERE)
import camera  # noqa: E402

FPS, W, H, SR = 24, 1920, 1080, 44100
LEAD, TAIL = 0.3, 0.5
FONT = "DejaVu Sans"
# the score: the mood from each shot on (videos/doodle/score.py moods), stings, and punchlines (music stops)
MOODS = {"S01": "suspense", "S03": "dramatic", "S05": "curious", "S08": "playful", "S13": "triumphant",
         "S15": "sneaky", "S24": "silence", "S25": "suspense", "S27": "dramatic", "S31": "suspense",
         "S33": "triumphant", "S39": "dramatic", "S42": "silence", "S45": "playful", "S47": "sad",
         "S49": "silence", "S51": "playful", "S53": "warm", "S55": "suspense", "S56": "dramatic"}
STINGS = {"S02": "hit", "S33": "hit", "S44": "wahwah", "S52": "rimshot"}
PUNCHES = ["S44", "S50", "S52"]


def run(*cmd):
    subprocess.run([str(c) for c in cmd], check=True)


def wav_seconds(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def ass_time(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def plan(shots, base):
    """Each shot's start and length, from its planned length and its voice line."""
    t, out = 0.0, []
    for s in shots:
        dur = float(s["seconds"])
        v = os.path.join(base, "voice", f"{s['id']}.wav")
        if s.get("line") and os.path.exists(v):
            dur = max(dur, LEAD + wav_seconds(v) + TAIL)
        out.append(dict(s, start=round(t, 3), dur=round(dur, 3)))
        t += dur
    return out, t


GRADES = {  # per-shot colour corrections ("grade" in the shot list)
    "evening": "eq=brightness=-0.07:contrast=1.03:saturation=0.92,colorbalance=rs=-0.05:gs=-0.02:bs=0.08:rm=-0.03:bm=0.05",
    "tame": "eq=saturation=0.8,colorbalance=rs=0.04:bs=-0.06:rm=0.03:bm=-0.05",  # pulls back an over-cyan drift
}


def clip_seconds(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)


def norm_video(src, out, dur, upscale=False, freeze_from_end=False, fit=False, cut_end=0.0, grade=None):
    """Any clip -> 1920x1080, 24 fps, exactly dur seconds (the last frame is held if the clip is shorter).
    fit: a longer clip is sped up to fit the shot instead of losing its ending (where the action often is);
    cut_end: seconds dropped from the clip's end first (a bad last moment); grade: a GRADES colour correction."""
    n = int(round(dur * FPS))
    pre = ""
    if fit:
        usable = max(0.5, clip_seconds(src) - cut_end)
        pre = f"trim=end={usable:.3f}," + (f"setpts=(PTS-STARTPTS)*{dur / usable:.4f}," if usable > dur else "")
    vf = (pre + f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}"
          + (",unsharp=5:5:0.6" if upscale else "") + (f",{GRADES[grade]}" if grade else "")
          + f",fps={FPS},tpad=stop_mode=clone:stop_duration={dur},format=yuv420p")
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", src, "-vf", vf, "-frames:v", n, "-an", "-c:v", "libx264",
        "-crf", "17", "-preset", "medium", out)


def still_video(img, out, dur, darken=0.0):
    n = int(round(dur * FPS))
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},"
          f"zoompan=z='1+0.04*on/{max(n - 1, 1)}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={n}:s={W}x{H}:fps={FPS}"
          + (f",eq=brightness=-{darken}" if darken else "") + ",format=yuv420p")
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", img, "-vf", vf, "-frames:v", n, "-c:v", "libx264", "-crf", "17", out)


def black_video(out, dur):
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}:d={dur}",
        "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", out)


def last_frame(video, out_png):
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-sseof", "-0.1", "-i", video, "-frames:v", "1", out_png)


def picture(s, base, work, segs):
    """The shot's picture as a normalized segment; returns its path."""
    out = os.path.join(work, f"seg_{s['id']}.mp4")
    sid, dur = s["id"], s["dur"]
    ai = os.path.join(base, "out", "clips", f"{sid}_{s.get('take', 'a')}.mp4")  # "take": the chosen take, once it exists
    if not os.path.exists(ai):
        ai = os.path.join(base, "out", "clips", f"{sid}_a.mp4")
    lip = os.path.join(base, "out", "clips", f"{sid}_lip.mp4")  # a talking shot made by lipsync_clips.py
    cam = os.path.join(base, "out", "camera", f"{sid}.mp4")
    kf = os.path.join(base, "out", "keyframes_ok", f"{sid}.jpg")
    if s["kind"] == "edit":
        if sid == "S03":
            still_video(os.path.join(base, "out", "keyframes_ok", "S05.jpg"), out, dur, darken=0.25)
        elif sid in ("S14", "S20", "S42"):  # a freeze of the shot before, with a card or the clock on it
            png = os.path.join(work, f"freeze_{sid}.png")
            last_frame(segs[-1], png)
            still_video(png, out, dur)
        elif sid == "S32":  # the cold-open shot again: S02's clip
            src = segs[1] if len(segs) > 1 else None
            norm_video(src, out, dur) if src else black_video(out, dur)
        elif sid == "S38":  # the clock montage over the wolf fight
            prev = os.path.join(work, "seg_S36.mp4")
            norm_video(prev, out, dur) if os.path.exists(prev) else black_video(out, dur)
        else:
            black_video(out, dur)
        return out
    grade, cut_end = s.get("grade"), float(s.get("clip_cut_end", 0))
    def fresh(src):  # reuse a segment already made from the same source at the same length
        stamp = out + ".src"
        key = f"{os.path.abspath(src)} {os.path.getmtime(src)} {dur} {grade} {cut_end} fit2"
        ok = os.path.exists(out) and os.path.exists(stamp) and open(stamp).read() == key
        open(stamp, "w").write(key)
        return ok
    if os.path.exists(lip):  # the lips follow the voice line from the shot's start: no speed change, only a trim
        if not fresh(lip):
            norm_video(lip, out, dur, upscale=True, grade=grade)
    elif os.path.exists(ai):
        if not fresh(ai):
            norm_video(ai, out, dur, upscale=True, fit=True, cut_end=cut_end, grade=grade)
    elif os.path.exists(cam):
        if not fresh(cam):
            norm_video(cam, out, dur, grade=grade)
    elif os.path.exists(kf):  # a stand-in until the AI clip or camera move exists
        tmp = os.path.join(work, f"cam_{sid}.mp4")
        camera.render(kf, tmp, dur, camera.MOVES.get(sid, camera.DEFAULT))
        norm_video(tmp, out, dur, grade=grade)
    else:
        black_video(out, dur)
        print(f"   {sid}: no picture yet (black)")
    return out


def ass_file(timeline, path):
    """Subtitles for every line, plus the cards made in the edit."""
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{FONT},46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,3,1,2,120,120,60,1
Style: Title,DejaVu Serif,110,&H00FFFFFF,&H00FFFFFF,&H00301000,&H00000000,1,0,0,0,100,100,6,0,1,4,2,5,60,60,60,1
Style: Small,{FONT},52,&H00F0E6C8,&H00F0E6C8,&H00000000,&H00000000,0,0,0,0,100,100,4,0,1,2,1,5,60,60,60,1
Style: Card,{FONT},58,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0101820,1,0,0,0,100,100,2,0,3,18,0,1,90,90,140,1
Style: Clock,DejaVu Sans Mono,120,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,5,2,9,80,80,60,1
Style: Skill,{FONT},44,&H00FFF2C8,&H00FFF2C8,&H00402000,&HB0200A00,1,0,0,0,100,100,1,0,3,22,0,6,140,140,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    by = {s["id"]: s for s in timeline}

    def add(style, t0, t1, text, layer=0):
        ev.append(f"Dialogue: {layer},{ass_time(t0)},{ass_time(t1)},{style},,0,0,0,,{text}")
    for s in timeline:
        if s.get("line"):
            text = re.sub(r"^\((\w+)\)\s*", "", s["line"][1])
            who = s["line"][0]
            if s["line"][1].startswith("(thinking)"):
                text = "{\\i1}" + text + "{\\i0}"
            elif who != "narrator":
                text = text
            v = wav_seconds(os.path.join(BASE, "voice", f"{s['id']}.wav"))
            add("Sub", s["start"] + LEAD, s["start"] + LEAD + v + 0.15, text)
    t = by["S03"]
    add("Title", t["start"] + 0.3, t["start"] + t["dur"] - 0.2, "{\\fad(600,400)}THE F-RANK TEA SELLER", 1)
    add("Small", t["start"] + 1.0, t["start"] + t["dur"] - 0.2, "{\\fad(500,400)\\pos(960,660)}EPISODE 1  ·  HUNTER'S CHAI", 1)
    t = by["S04"]
    add("Small", t["start"] + 0.1, t["start"] + t["dur"] - 0.1, "{\\fad(300,300)\\fs64}ONE HOUR EARLIER", 1)
    t = by["S12"]
    add("Card", t["start"] + t["dur"] * 0.4, t["start"] + t["dur"], "{\\fad(250,200)}ARJUN\\N{\\fs40}AGE 18   ·   HUNTER RANK: F", 1)
    t = by["S14"]
    add("Card", t["start"], t["start"] + t["dur"], "{\\fad(200,200)}VIKTOR HALE\\N{\\fs40}B-RANK   ·   2M FOLLOWERS", 1)
    t = by["S20"]
    add("Card", t["start"], t["start"] + t["dur"], "{\\fad(200,200)}MEERA\\N{\\fs40}HEALER", 1)
    t = by["S38"]
    steps = 12
    for k in range(steps):
        mm = 2 + round(56 * k / (steps - 1))
        a = t["start"] + t["dur"] * k / steps
        add("Clock", a, a + t["dur"] / steps, f"{mm:02d}:00", 1)
    t = by["S42"]
    for k, (txt, col) in enumerate([("59:58", "&H00FFFFFF&"), ("59:59", "&H00FFFFFF&"), ("60:00", "&H003030FF&")]):
        a = t["start"] + t["dur"] * k / 3
        add("Clock", a, t["start"] + t["dur"] if k == 2 else a + t["dur"] / 3, f"{{\\c{col}}}{txt}", 1)
    t = by["S54"]
    a, b = t["start"] + 0.6, t["start"] + t["dur"]
    # the window: a dark-blue panel with a cyan frame (an ASS drawing), the text inside it, left-aligned
    add("Skill", a, b, "{\\an7\\pos(1150,250)\\fad(400,300)\\p1\\bord4\\shad0\\1c&H401808&\\1a&H30&\\3c&HFFE84C&}"
        "m 0 0 l 660 0 660 330 0 330{\\p0}", 0)
    add("Skill", a, b, "{\\an7\\pos(1185,275)\\fad(400,300)\\bord0\\shad0\\fs40\\c&HFFE84C&}[ HIDDEN SKILL ]"
        "{\\fs34\\c&HFFF2E6&}\\N\\NName: Hunter's Chai\\NRank: ???\\NEffect: Anyone who drinks it\\N"
        "             borrows great strength.\\NDuration: exactly 1 hour.", 1)
    t = by["S56"]
    add("Title", t["start"] + 0.3, t["start"] + t["dur"], "{\\fad(500,0)\\fs90}TO BE CONTINUED", 1)
    add("Small", t["start"] + 1.4, t["start"] + t["dur"], "{\\fad(400,0)\\pos(960,690)}Subscribe so you don't miss Episode 2", 1)
    open(path, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")


def load_audio(path, channels=1):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-f", "f32le", "-ac", str(channels), "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, channels)


def write_wav(path, a):
    a = np.clip(a, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(a.shape[1]); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((a * 32767).astype("<i2").tobytes())


BASE = ""


def main():
    global BASE
    ap = argparse.ArgumentParser()
    ap.add_argument("shots")
    ap.add_argument("out")
    ap.add_argument("--work")
    a = ap.parse_args()
    BASE = os.path.dirname(os.path.abspath(a.shots))
    work = a.work or os.path.join(BASE, "out", "edit")
    os.makedirs(work, exist_ok=True)
    timeline, total = plan(json.load(open(a.shots))["shots"], BASE)
    print(f"{len(timeline)} shots, {total:.1f} s")
    # pictures
    segs = []
    for s in timeline:
        segs.append(picture(s, BASE, work, segs))
    lst = os.path.join(work, "segments.txt")
    open(lst, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in segs))
    silent = os.path.join(work, "picture.mp4")
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent)
    # voices on one track, effects on another
    n = int(total * SR) + SR
    voice, fx = np.zeros((n, 1), np.float32), np.zeros((n, 2), np.float32)
    for s in timeline:
        v = os.path.join(BASE, "voice", f"{s['id']}.wav")
        if s.get("line") and os.path.exists(v):
            x = load_audio(v)
            i = int((s["start"] + LEAD) * SR)
            voice[i:i + len(x)] += x[: n - i]
        f = os.path.join(BASE, "out", "sfx", f"{s['id']}.mp3")
        if os.path.exists(f):
            x = load_audio(f, 2)[: int(s["dur"] * SR)].copy()
            fade = min(len(x), int(0.35 * SR))
            x[len(x) - fade:] *= np.linspace(1, 0, fade)[:, None]
            i = int(s["start"] * SR)
            fx[i:i + len(x)] += 0.32 * x[: n - i]
    amb = os.path.join(BASE, "out", "score", "ambience.wav")  # film_score.py: one background bed per scene
    if os.path.exists(amb):
        x = load_audio(amb, 2)[:n]
        fx[: len(x)] += x
    write_wav(os.path.join(work, "voice.wav"), voice)
    write_wav(os.path.join(work, "sfx.wav"), fx)
    # the score and the mix (ducking under the voice, silence before the punchlines)
    by = {s["id"]: s for s in timeline}
    events = [{"t": by[k]["start"], "kind": "mood", "mood": m} for k, m in MOODS.items()]
    events += [{"t": by[k]["start"] + 0.2, "kind": "sting", "name": m} for k, m in STINGS.items()]
    events += [{"t": by[k]["start"] + LEAD, "kind": "punch"} for k in PUNCHES]
    ev = os.path.join(work, "events.json")
    json.dump(sorted(events, key=lambda e: e["t"]), open(ev, "w"))
    music = os.path.join(work, "music.wav")
    run(sys.executable, os.path.join(DOODLE, "score.py"), music, f"{total:.2f}", "--events", ev, "--seed", "3")
    film = os.path.join(BASE, "out", "score", "score.wav")  # film_score.py: the orchestral score replaces the synth
    if os.path.exists(film):
        run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", film, "-ar", str(SR), "-ac", "2", music)
    mixed = os.path.join(work, "mix.m4a")  # mix.py always writes AAC
    run(sys.executable, os.path.join(DOODLE, "mix.py"), os.path.join(work, "voice.wav"), music, mixed, "--events", ev,
        "--stings", os.path.splitext(music)[0] + "_stings.wav", "--plain-voice", "--music-gain", "0.34")
    audio = os.path.join(work, "audio.wav")
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", mixed, "-i", os.path.join(work, "sfx.wav"), "-filter_complex",
        "[0:a][1:a]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-2:LRA=11,alimiter=limit=0.79:level=false", "-ar", str(SR), audio)
    # subtitles and cards, a light film look, fade in and out
    subs = os.path.join(work, "subs.ass")
    ass_file(timeline, subs)
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", silent, "-i", audio, "-filter_complex",
        f"[0:v]eq=contrast=1.04:saturation=1.06,vignette=PI/6,ass={subs},fade=t=in:st=0:d=0.8,"
        f"fade=t=out:st={total - 1.0:.2f}:d=1.0[v]", "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-crf", "18",
        "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", a.out)
    print(f"done: {a.out} ({total:.1f} s)")


if __name__ == "__main__":
    main()
