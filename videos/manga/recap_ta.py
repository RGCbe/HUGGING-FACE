"""The Tamil Short of a webtoon recap: the English Short's moments, with the speech bubbles and boxes in Tamil, the
owner's voice speaking Tamil and Tamil captions. A separate video on the same channel, Tamil as its language.

    python3 recap_ta.py STEP EPISODE_DIR        STEP: letter | voice | short | upload

EPISODE_DIR/recap/short_ta.json is written by a person (the owner checks the Tamil):
  "letter"   {"English text in episode.json": "Tamil text", ...}: bubbles, narration boxes, the status window and
             the cards. A text with no entry stays English; sound effects always do.
  "lines"    one Tamil line for each line of recap.json's "short", with its emotion tag; the panel, music, sting
             and punch come from the English line
  "caption_replace"  [["spoken words", "shown"], ...]: numbers as digits, the title in English
  "meta"     {"title", "description", "tags", "publish_at"}; "{FULL_RECAP}" in the description becomes the link
             of the English recap (recap/upload.results.json)

  letter  episode_ta.json and the Tamil strip in out_ta/webtoon (Mukta Malar; the English strip is untouched)
  voice   each line in the owner's ElevenLabs voice (teabreak config "eleven"), checked to be heard as Tamil
          (Whisper's Tamil is too weak to check word by word: the owner listens), joined with the recap's pauses;
          caption word times spread over the speech
  short   the 1080x1920 Short over the Tamil strip, the recap's music moods and stings: recap/out/short_ta.mp4
  upload  recap/upload_ta.json, private and scheduled at publish_at, uploaded with ../doodle/upload.py
"""
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEOS = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(VIDEOS, "teabreak"))
import recap  # noqa: E402
import tamil  # noqa: E402  (load, save, trim, speech_spans, word_times, shown, run, cfg)

TB = recap.tb
DOODLE, KURAL = recap.DOODLE, os.path.join(VIDEOS, "kural")
FONT = os.path.join(VIDEOS, "movies-explained", "fonts", "MuktaMalar-ExtraBold.ttf")
SR = tamil.SR
CHECK = r"""
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


def setup(ep):
    r, spec = recap.load(ep)
    conf = json.load(open(os.path.join(r, "short_ta.json"), encoding="utf-8"))
    english = recap.short_lines(spec)
    if len(conf["lines"]) != len(english):
        sys.exit(f"short_ta.json needs {len(english)} lines, one for each line of the English Short")
    lines = [dict(l, text=t) for l, t in zip(english, conf["lines"])]
    return r, spec, conf, lines, os.path.join(r, "short_ta")


def step_letter(ep):
    r, spec, conf, _, _ = setup(ep)
    table, missing = conf["letter"], []

    def tr(t):
        if t and t not in table:
            missing.append(t)
        return table.get(t, t)
    script = json.load(open(os.path.join(ep, "episode.json"), encoding="utf-8"))
    for p in script:
        if p.get("card"):
            p["card"] = tr(p["card"])
        for n in p.get("before", []) + p.get("after", []):
            n["text"] = tr(n["text"])
        for b in p.get("bubbles", []):
            b["text"] = tr(b["text"])
        for s in p.get("status", []):
            s["title"], s["lines"] = tr(s["title"]), [tr(x) for x in s["lines"]]
    if missing:
        print("left in English:\n  " + "\n  ".join(missing))
    path = os.path.join(ep, "episode_ta.json")
    json.dump(script, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    env = dict(os.environ, LETTER_FONT=FONT, LETTER_TITLE_FONT=FONT, LETTER_LINE="1.5")
    tamil.run("python3", os.path.join(HERE, "letter.py"), path, os.path.join(ep, "out", "img"),
              os.path.join(ep, "out_ta", "webtoon"), env=env)


def step_voice(ep):
    r, spec, conf, lines, work = setup(ep)
    tts = os.path.join(work, "tts")
    os.makedirs(tts, exist_ok=True)
    text = os.path.join(work, "voiceover_ta.txt")
    open(text, "w", encoding="utf-8").write("\n".join(l["text"] for l in lines) + "\n")
    e = tamil.cfg["eleven"]
    todo = [k for k in range(1, len(lines) + 1) if not os.path.exists(os.path.join(tts, f"sec_{k:02d}.wav"))]
    if todo:
        tamil.run("python3", "-I", os.path.join(KURAL, "eleven.py"), text, tts, "--sections", ",".join(map(str, todo)),
                  "--voice", e["voice"], "--model", e["model"], "--stability", e["stability"], "--similarity", e["similarity"])
    wavs = [os.path.join(tts, f"sec_{k:02d}.wav") for k in range(1, len(lines) + 1)]
    tamil.run(os.environ.get("WHISPER_PY", "python3"), "-c", CHECK, *wavs)
    table = conf.get("caption_replace", [])
    gap = np.zeros(int(TB.GAP * SR), np.float32)
    parts, sections, t = [], [], 0.0
    for k, (l, w) in enumerate(zip(lines, wavs), 1):
        a = tamil.trim(tamil.load(w))
        spans = [[t + x, t + y] for x, y in tamil.speech_spans(a)]
        words = re.sub(r"^\[[a-z]+\]\s*", "", l["text"]).split()
        sections.append({"n": k, "offset": round(t, 3), "duration": round(len(a) / SR, 3),
                         "words": tamil.shown(tamil.word_times(words, spans), table)})
        parts += [a, gap]
        t += len(a) / SR + TB.GAP
    voice = np.concatenate(parts[:-1])
    tamil.save(os.path.join(work, "voice.wav"), voice)
    total = round(len(voice) / SR, 3)
    json.dump({"total": total, "sections": sections}, open(os.path.join(work, "timing.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"Tamil Short voice: {total:.1f}s")


def step_short(ep):
    r, spec, conf, lines, work = setup(ep)
    timing = json.load(open(os.path.join(work, "timing.json"), encoding="utf-8"))
    silent, total = recap.render(ep, work, lines, timing, "vertical", webtoon=os.path.join("out_ta", "webtoon"))
    mix = recap.sound(work, lines, timing, os.path.join(work, "voice.wav"), total, 29)
    ass = os.path.join(work, "captions.ass")
    TB.run("python3", os.path.join(DOODLE, "captions.py"), os.path.join(work, "timing.json"), ass, "--layout", "vertical",
           "--font", "Kavivanar")
    out = os.path.join(r, "out", "short_ta.mp4")
    TB.run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", silent, "-i", mix, "-vf",
           f"ass={ass}:fontsdir={os.path.join(DOODLE, 'fonts')}:shaping=complex", "-af",
           f"afade=t=out:st={total - 1.5}:d=1.5", "-shortest", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out)
    print(f"Tamil Short: {out} ({TB.duration(out):.1f}s)")


def step_upload(ep):
    r, spec, conf, _, _ = setup(ep)
    m = dict(conf["meta"])
    if "{FULL_RECAP}" in m["description"]:
        done = os.path.join(r, "upload.results.json")
        if not os.path.exists(done):
            sys.exit("upload the English recap first (recap.py upload): its link goes in the description")
        m["description"] = m["description"].replace("{FULL_RECAP}", json.load(open(done))[0]["url"])
    defaults = {"privacy": "private", "made_for_kids": False, "ai_content": True, "category_id": 24, "language": "ta",
                "refresh_token_env": TB.cfg["channel"]["refresh_token_env"]}
    defaults.update(spec["meta"].get("upload_defaults", {}))
    defaults["language"] = "ta"
    upload = {"defaults": defaults,
              "videos": [{"file": os.path.join(r, "out", "short_ta.mp4"), "title": m["title"], "description": m["description"],
                          "tags": m["tags"], "publish_at": m["publish_at"], "playlists": spec["meta"].get("playlists", [])}]}
    path = os.path.join(r, "upload_ta.json")
    json.dump(upload, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    TB.run("python3", os.path.join(DOODLE, "upload.py"), path)


if __name__ == "__main__":
    steps = {"letter": step_letter, "voice": step_voice, "short": step_short, "upload": step_upload}
    if len(sys.argv) != 3 or sys.argv[1] not in steps:
        sys.exit(__doc__)
    steps[sys.argv[1]](sys.argv[2])
