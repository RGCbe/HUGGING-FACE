"""The Tamil version of a finished Tea Break video: the same pictures and music, the owner's voice speaking
Tamil, Tamil captions and Tamil words on the boards. It is a separate video (the English one has English
captions burned in), uploaded to the same channel with Tamil as its language.

    python3 tamil.py STEP WORK_DIR        STEP: voice | video | upload

WORK_DIR is the English video's folder after build.py's video step. Its tamil/ folder holds what a person
writes (the owner checks the Tamil):
  voiceover_ta.txt   one line per section of voiceover_en.txt, with the same emotion tags
  onscreen_ta.json   {"English text on a board": "Tamil text", ...}; every write/big/stamp/calendar text in
                     scenes.js is looked up, and a text with no entry stays English (names, a sale's name)
  thumbnail_ta.js    the Tamil thumbnail (like thumbnail.js)
  meta_ta.json       {"title", "description", "tags", "publish_at"}
  caption_replace_ta.json (optional)  [["ஆயிரத்து தொள்ளாயிரத்து எழுபதுல", "1970-ல"], ...]: spoken words shown
                     another way in the captions (numbers as digits)

  voice   each section in the owner's ElevenLabs voice (kural/eleven.py, config.json "eleven"), and a check
          that Whisper hears Tamil in every section (Whisper's Tamil is too weak to check word by word: the
          owner listens)
  video   each Tamil section is placed where the English one starts, sped up (a little) if it is longer than
          the English one's slot, so every board still matches its words; then the music and sound effects
          of the English video, Tamil captions (word times spread over the speech, skipping pauses), the
          boards re-rendered with the Tamil words, and the Tamil thumbnail:
          out/SLUG_ta.mp4, out/SLUG_ta_thumbnail.jpg
  upload  writes tamil/upload_ta.json and uploads it (private, scheduled at publish_at, language Tamil)
"""
import json
import os
import re
import subprocess
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DOODLE = os.path.join(HERE, "..", "doodle")
KURAL = os.path.join(HERE, "..", "kural")
cfg = json.load(open(os.path.join(HERE, "config.json")))
SR = 24000
TAIL = 3.0  # build.py: seconds of picture after the voiceover
MAX_SPEED = 1.15  # a section faster than this is reworded instead


def run(*cmd, **kw):
    print("+", " ".join(str(c) for c in cmd)[:160], flush=True)
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def lines(path):
    return [l.strip() for l in open(path, encoding="utf-8") if l.strip()]


def load(path):
    with wave.open(path) as w:
        assert w.getframerate() == SR and w.getnchannels() == 1
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


def save(path, a):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())


def trim(a, thr=0.01):
    loud = np.where(np.abs(a) > thr)[0]
    return a[max(0, loud[0] - int(0.05 * SR)): loud[-1] + int(0.15 * SR)]


def speech_spans(a, frame=0.02, gap=0.25):
    """(start, end) seconds of speech in a, pauses shorter than gap joined."""
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
    """Spread words over the speech spans by their length, so a pause carries no word."""
    weight = [len(w) + (3 if re.search(r"[.,?!:]$", w) else 0) for w in words]
    total_w, speech = sum(weight), sum(e - s for s, e in spans)
    def at(x):  # x of the speech time (0..speech) to a real time
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
        out.append({"w": w, "t0": round(t0, 3), "t1": round(max(t1, t0 + 0.05), 3)})
    return out


def shown(words, table):
    """Caption words with each spoken phrase in table replaced by how it is shown ("1970-ல" for the year in words);
    the phrase's last word keeps its punctuation, and the shown word spans the phrase's time."""
    strip = lambda w: re.sub(r"[.,?!:;\"]+$", "", w)
    phrases = sorted((([strip(x) for x in p.split()], strip(v)) for p, v in table), key=lambda r: -len(r[0]))
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


def step_voice(d):
    t = os.path.join(d, "tamil")
    n = len(lines(os.path.join(t, "voiceover_ta.txt")))
    if n != len(lines(os.path.join(d, "voiceover_en.txt"))):
        sys.exit("voiceover_ta.txt needs one line for each section of voiceover_en.txt")
    e = cfg["eleven"]
    todo = [k for k in range(1, n + 1) if not os.path.exists(os.path.join(t, "tts", f"sec_{k:02d}.wav"))]
    if todo:
        run("python3", "-I", os.path.join(KURAL, "eleven.py"), os.path.join(t, "voiceover_ta.txt"), os.path.join(t, "tts"),
            "--sections", ",".join(map(str, todo)), "--voice", e["voice"], "--model", e["model"],
            "--stability", e["stability"], "--similarity", e["similarity"])
    # Whisper only has to hear Tamil: a section in another language or garbled is redone by hand
    check = r"""
import sys, subprocess, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("medium", device="cpu", compute_type="int8")
bad = []
for p in sys.argv[1:]:
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", p, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    _, info = m.transcribe(np.frombuffer(raw, np.int16).astype(np.float32) / 32768, beam_size=1)
    print(p.rsplit("/", 1)[-1], info.language, round(info.language_probability, 2), flush=True)
    if info.language != "ta" or info.language_probability < 0.8:
        bad.append(p)
sys.exit(f"not heard as Tamil: {bad}" if bad else 0)
"""
    run(os.environ.get("WHISPER_PY", "python3"), "-c", check,
        *[os.path.join(t, "tts", f"sec_{k:02d}.wav") for k in range(1, n + 1)])


def scenes_ta(d):
    """scenes.js with each board's text swapped for its Tamil (onscreen_ta.json)."""
    src = open(os.path.join(d, "scenes.js"), encoding="utf-8").read()
    table = json.load(open(os.path.join(d, "tamil", "onscreen_ta.json"), encoding="utf-8"))
    used = set()
    def swap(m):
        q, text = m.group(1), m.group(2)
        if re.search(r"\b(?:c|cue|cueEnd)\(\d+, *$", src[max(0, m.start() - 20):m.start()]):
            return m.group(0)  # a cue phrase: the English words it waits for, never shown
        plain = text.replace("\\'", "'").replace('\\"', '"')
        plain = re.sub(r"\\u([0-9a-fA-F]{4})", lambda u: chr(int(u.group(1), 16)), plain)  # 'COULDN\u2019T' is COULDN’T
        if plain in table:
            used.add(plain)
            return q + table[plain].replace("\\", "\\\\").replace(q, "\\" + q) + q
        return m.group(0)
    out = re.sub(r"(['\"])((?:\\.|(?!\1).)*)\1", swap, src)
    for k in set(table) - used:
        print(f"warning: onscreen_ta.json has {k!r}, which is not in scenes.js")
    # a centred line may not run off the board: shrink it to fit between its centre and the nearer edge
    out = out.replace("(function () {", "(function () {\n  const W0 = Doodle.write;\n  Doodle.write = (at, x, y, str, o = {}) => "
                      "W0(at, x, y, str, Object.assign({ maxWidth: Math.max(300, 2 * Math.min(x, 1920 - x) - 60) }, o));", 1)
    path = os.path.join(d, "tamil", "scenes_ta.js")
    open(path, "w", encoding="utf-8").write(out)
    return path


def step_video(d):
    slug = os.path.basename(os.path.normpath(d))
    t = os.path.join(d, "tamil")
    timing = json.load(open(os.path.join(d, "timing.json")))
    secs, total = timing["sections"], timing["total"] + TAIL
    text = [re.sub(r"^\[[a-z]+\]\s*", "", l) for l in lines(os.path.join(t, "voiceover_ta.txt"))]
    track = np.zeros(int(total * SR) + SR, dtype=np.float32)
    rp = os.path.join(t, "caption_replace_ta.json")
    table = json.load(open(rp, encoding="utf-8")) if os.path.exists(rp) else []
    ta_sections, slow = [], []
    for k, s in enumerate(secs):
        a = trim(load(os.path.join(t, "tts", f"sec_{s['n']:02d}.wav")))
        end = secs[k + 1]["offset"] - 0.15 if k + 1 < len(secs) else total - 0.8
        slot, dur = end - s["offset"], len(a) / SR
        if dur > slot:
            speed = dur / slot
            if speed > MAX_SPEED:
                slow.append(f"section {s['n']}: {dur:.1f}s of Tamil for a {slot:.1f}s slot (x{speed:.2f})")
            src, fit = os.path.join(t, "tts", f"trim_{s['n']:02d}.wav"), os.path.join(t, "tts", f"fit_{s['n']:02d}.wav")
            save(src, a)
            run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", src, "-af", f"atempo={speed:.4f}", "-ar", SR, fit)
            a = load(fit)
        i = int(s["offset"] * SR)
        track[i:i + len(a)] += a[: len(track) - i]
        spans = [[s["offset"] + x, s["offset"] + y] for x, y in speech_spans(a)]
        ta_sections.append({"n": s["n"], "offset": s["offset"], "duration": len(a) / SR,
                            "words": shown(word_times(text[k].split(), spans), table)})
    if slow:
        sys.exit("Tamil too long for its pictures; shorten these lines in voiceover_ta.txt and run voice again:\n  "
                 + "\n  ".join(slow))
    voice = os.path.join(t, "voice_pad_ta.wav")
    save(voice, track[: int(total * SR)])
    tj = os.path.join(t, "timing_ta.json")
    json.dump({"total": timing["total"], "sections": ta_sections}, open(tj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # sound: the English video's music, stings and effects under the Tamil voice
    mix = os.path.join(t, "mix_ta.m4a")
    stings = os.path.join(d, "music_stings.wav")
    run("python3", os.path.join(DOODLE, "mix.py"), voice, os.path.join(d, "music.wav"), mix, "--music-gain", cfg["music_gain"],
        "--events", os.path.join(d, "events.json"), *(["--stings", stings] if os.path.exists(stings) else []))
    ass = os.path.join(t, "captions_ta.ass")
    run("python3", os.path.join(DOODLE, "captions.py"), tj, ass, "--font", "Kavivanar")

    # pictures: the boards with Tamil words, on the English timeline (the cues are English words)
    data = os.path.join(d, "data.json")
    silent = os.path.join(t, "silent_ta.mp4")
    scenes = scenes_ta(d)
    inputs = [os.path.join(d, "scenes.js"), os.path.join(t, "onscreen_ta.json"), os.path.join(d, "timing.json")]
    if os.path.exists(silent) and os.path.getmtime(silent) > max(os.path.getmtime(p) for p in inputs):
        print(f"boards unchanged since {silent}: not rendered again")
    else:  # rendered under another name first, so a render cut short (a restart) is never taken for a finished one
        part = os.path.join(t, "silent_ta.part.mp4")
        run("node", os.path.join(DOODLE, "render.mjs"), "--timing", os.path.join(d, "timing.json"), "--data", data,
            "--scenes", scenes, "--out", part)
        os.replace(part, silent)
    out = os.path.join(d, "out")
    video = os.path.join(out, f"{slug}_ta.mp4")
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", silent, "-i", mix, "-vf",
        f"ass={ass}:fontsdir={os.path.join(DOODLE, 'fonts')}", "-af", f"afade=t=out:st={total - 1.5}:d=1.5", "-shortest",
        "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart", video)
    thumb = os.path.join(t, "thumb")
    run("node", os.path.join(DOODLE, "render.mjs"), "--timing", os.path.join(d, "timing.json"), "--data", data,
        "--scenes", os.path.join(t, "thumbnail_ta.js"), "--out", os.path.join(thumb, "t.mp4"), "--stills", "3")
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", os.path.join(thumb, "t_3.00.png"), "-vf",
        "scale=1280:720:flags=lanczos", "-q:v", "3", os.path.join(out, f"{slug}_ta_thumbnail.jpg"))
    print(f"tamil video: {video}, thumbnail: {slug}_ta_thumbnail.jpg")


def step_upload(d):
    slug = os.path.basename(os.path.normpath(d))
    t = os.path.join(d, "tamil")
    meta = json.load(open(os.path.join(t, "meta_ta.json"), encoding="utf-8"))
    note = ("\n\nகுரல்: என் சொந்தக் குரலின் AI நகல். படங்கள் AI மூலம் வரையப்பட்டவை (FLUX.2 klein), இசை எங்களுடையது."
            "\nEnglish version on the channel.")
    out = os.path.abspath(os.path.join(d, "out"))
    long_list = cfg.get("playlists", {}).get("tamil", {}).get("id")
    spec = {"defaults": {"privacy": "private", "made_for_kids": False, "ai_content": True, "category_id": 27,
                         "language": "ta", "refresh_token_env": cfg["channel"]["refresh_token_env"]},
            "videos": [{"file": os.path.join(out, f"{slug}_ta.mp4"), "thumbnail": os.path.join(out, f"{slug}_ta_thumbnail.jpg"),
                        "title": meta["title"], "description": meta["description"] + note, "tags": meta["tags"],
                        "publish_at": meta["publish_at"], "playlists": [long_list] if long_list else []}]}
    path = os.path.join(t, "upload_ta.json")
    json.dump(spec, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    run("python3", os.path.join(DOODLE, "upload.py"), path)


if __name__ == "__main__":
    {"voice": step_voice, "video": step_video, "upload": step_upload}[sys.argv[1]](os.path.abspath(sys.argv[2]))
