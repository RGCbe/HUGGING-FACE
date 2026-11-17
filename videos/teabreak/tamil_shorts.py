"""Tamil Shorts of a Tea Break video, made from its Tamil version (tamil.py) and its English Shorts.

    python3 tamil_shorts.py STEP WORK_DIR        STEP: hooks | shorts | upload

WORK_DIR is the video's folder, after tamil.py's video step. tamil/shorts_ta.json is written by a person:
  {"title": "சின்ன போர் (1896)",                  the line above the picture
   "shorts": [{"hook": "[excited] ...",           the Tamil hook line, spoken before the clip
               "subtitle": "...",                  the smaller line under the title
               "yt_title": "... #shorts",          the YouTube title
               "yt_text": "...",                   one or two lines for the description
               "publish_at": "2026-11-19T12:30:00Z"}, ...],
   "english": ["short1.json", "short2.json"]}      the English Short specs whose moments to use (optional;
                                                   default WORK_DIR/short1.json, short2.json)

  hooks   each hook line in the owner's ElevenLabs voice, checked to be heard as Tamil, and its word times
  shorts  each Short: the English Short's moments, widened to whole sections (the Tamil sentences do not end
          where the English ones do), with the Tamil voice, the Tamil boards and captions, the English Short's
          music: out/SLUG_ta_shortN.mp4
  upload  private, scheduled at publish_at, Tamil as the language
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tamil  # noqa: E402  (word_times, speech_spans, shown, load, cfg)

DOODLE = os.path.join(HERE, "..", "doodle")
KURAL = os.path.join(HERE, "..", "kural")


def run(*cmd):
    print("+", " ".join(str(c) for c in cmd)[:160], flush=True)
    subprocess.run([str(c) for c in cmd], check=True)


def setup(d):
    t = os.path.join(d, "tamil")
    conf = json.load(open(os.path.join(t, "shorts_ta.json"), encoding="utf-8"))
    english = [os.path.join(d, f) for f in conf.get("english", ["short1.json", "short2.json"])]
    return t, conf, [json.load(open(os.path.expandvars(e))) for e in english]


def step_hooks(d):
    t, conf, _ = setup(d)
    hooks_dir = os.path.join(t, "hooks")
    lines = os.path.join(t, "hooks_ta.txt")
    open(lines, "w", encoding="utf-8").write("\n".join(s["hook"] for s in conf["shorts"]) + "\n")
    todo = [k for k in range(1, len(conf["shorts"]) + 1) if not os.path.exists(os.path.join(hooks_dir, f"sec_{k:02d}.wav"))]
    e = tamil.cfg["eleven"]
    if todo:
        run("python3", "-I", os.path.join(KURAL, "eleven.py"), lines, hooks_dir, "--sections", ",".join(map(str, todo)),
            "--voice", e["voice"], "--model", e["model"], "--stability", e["stability"], "--similarity", e["similarity"])
    rp = os.path.join(t, "caption_replace_ta.json")
    table = json.load(open(rp, encoding="utf-8")) if os.path.exists(rp) else []
    sections = []
    for k, s in enumerate(conf["shorts"], 1):
        wav = os.path.join(hooks_dir, f"sec_{k:02d}.wav")
        a = tamil.load(wav)
        text = re.sub(r"^\[[a-z]+\]\s*", "", s["hook"])
        sections.append({"n": k, "offset": 0.0, "duration": len(a) / tamil.SR,
                         "words": tamil.shown(tamil.word_times(text.split(), tamil.speech_spans(a)), table)})
    json.dump({"total": 0, "sections": sections}, open(os.path.join(t, "hooks_ta_timing.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
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
        *[os.path.join(hooks_dir, f"sec_{k:02d}.wav") for k in range(1, len(conf["shorts"]) + 1)])


def tamil_segments(d, english_segments):
    """The English Short's moments as whole sections of the Tamil voice: every section an English segment touches,
    from its start to the end of its Tamil speech."""
    en = json.load(open(os.path.join(d, "timing.json")))["sections"]
    ta = {s["n"]: s for s in json.load(open(os.path.join(d, "tamil", "timing_ta.json")))["sections"]}
    touched = []
    for g in english_segments:
        for s in en:
            end = s["offset"] + s["duration"]
            if s["offset"] < g["to"] - 0.3 and end > g["from"] + 0.3 and s["n"] not in touched:
                touched.append(s["n"])
    out = []
    for n in sorted(touched):
        s = ta[n]
        out.append({"from": round(max(0.0, s["offset"] - 0.05), 2), "to": round(s["offset"] + s["duration"] + 0.25, 2)})
    return out


def step_shorts(d):
    slug = os.path.basename(os.path.normpath(d))
    t, conf, english = setup(d)
    for k, (s, en) in enumerate(zip(conf["shorts"], english), 1):
        out = os.path.join(d, "out", f"{slug}_ta_short{k}.mp4")
        if os.path.exists(out):
            print(f"{out} already made")
            continue
        segs = tamil_segments(d, en["segments"])
        print(f"short {k}: {sum(g['to'] - g['from'] for g in segs):.1f}s of story from sections "
              f"{[round(g['from']) for g in segs]}")
        spec = {k2: v for k2, v in en.items() if k2 in ("music", "music_gain", "music_follows", "stings", "data", "background")}
        spec.update({
            "name": f"ta_short{k}", "out": out, "work_dir": os.path.join(t, "shorts_work"),
            "scenes": os.path.join(t, "scenes_ta.js"), "timing": os.path.join(d, "timing.json"),
            "caption_timing": os.path.join(t, "timing_ta.json"), "caption_font": "Kavivanar",
            "title_font": "Kavivanar-Regular.ttf", "voiceover": os.path.join(t, "voice_pad_ta.wav"),
            "title": conf["title"], "subtitle": s["subtitle"],
            "hook": {"wav": os.path.join(t, "hooks", f"sec_{k:02d}.wav"), "timing": os.path.join(t, "hooks_ta_timing.json"),
                     "section": k, "visual_from": en["hook"].get("visual_from", 0.0), "visual_to": en["hook"]["visual_to"]},
            "segments": segs,
        })
        path = os.path.join(t, f"short{k}_ta.json")
        json.dump(spec, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        run("python3", os.path.join(DOODLE, "short.py"), path)


def step_upload(d):
    slug = os.path.basename(os.path.normpath(d))
    t, conf, _ = setup(d)
    meta = json.load(open(os.path.join(t, "meta_ta.json"), encoding="utf-8"))
    long_ta = json.load(open(os.path.join(t, "upload_ta.results.json")))[0]["url"]
    note = "\n\nகுரல்: என் சொந்தக் குரலின் AI நகல். படங்கள் AI மூலம் வரையப்பட்டவை, இசை எங்களுடையது."
    shorts_list = tamil.cfg.get("playlists", {}).get("shorts_ta", {}).get("id")  # the Tamil Shorts playlist
    for k, s in enumerate(conf["shorts"], 1):
        done = os.path.join(t, f"upload_ta_short{k}.results.json")
        if os.path.exists(done):
            continue
        spec = {"defaults": {"privacy": "private", "made_for_kids": False, "ai_content": True, "category_id": 27, "language": "ta",
                             "refresh_token_env": tamil.cfg["channel"]["refresh_token_env"]},
                "videos": [{"file": os.path.join(d, "out", f"{slug}_ta_short{k}.mp4"), "title": s["yt_title"],
                            "description": s["yt_text"] + f"\nமுழு வீடியோ: {long_ta}" + note,
                            "tags": meta["tags"][:5] + ["shorts", "tamil shorts"], "publish_at": s.get("publish_at"),
                            "playlists": [shorts_list] if shorts_list else []}]}
        path = os.path.join(t, f"upload_ta_short{k}.json")
        json.dump(spec, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        run("python3", os.path.join(DOODLE, "upload.py"), path)


if __name__ == "__main__":
    {"hooks": step_hooks, "shorts": step_shorts, "upload": step_upload}[sys.argv[1]](os.path.abspath(sys.argv[2]))
