"""Tamil Shorts of a Tea Break video, made from its Tamil version (tamil.py) and its English Shorts.

    python3 tamil_shorts.py STEP WORK_DIR        STEP: hooks | shorts | upload | parts | parts_upload

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

The whole story as Tamil Shorts in parts instead (the owner's choice, 21 Nov 2026: "full story, 3 parts", and
"we need to tell at end like stay tune for next part"): shorts_ta.json then has
   "parts": [{"yt_title": "... | பகுதி 1/3 #shorts", "yt_text": "...", "publish_at": "..."}, ...]   (usually 3)
and optionally "outro_next" / "outro_last" (the lines at the end of each part; defaults below).
  parts         voices the two end lines (checked as Tamil), splits the Tamil video's sections into len(parts)
                stretches of about equal length (never a sentence cut), and makes each part with the title above
                the picture, "பகுதி k/N" under it, Tamil captions, and the end line: "stay tuned" after every part
                but the last, "subscribe and comment" after the last: out/SLUG_ta_partK.mp4 (each under 3 minutes)
  parts_upload  uploads the parts in order, private and scheduled; each part's description links the full Tamil
                video and the parts before it, and once all are up the earlier parts get the link to the next one
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
    check = CHECK
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


OUTRO_NEXT = "[warm] அடுத்த பகுதி சீக்கிரமே வருது, காத்திருங்க!"
OUTRO_LAST = "[warm] கதை பிடிச்சிருந்தா சப்ஸ்கிரைப் பண்ணுங்க. உங்களுக்கு பிடிச்ச பகுதி எது? கமெண்ட்ல சொல்லுங்க!"
MAX_PART = 170.0  # seconds: a Short is at most 3 minutes, and the end line needs a few


def split_parts(sections, n):
    """Cut points so that n runs of whole sections are about equally long (each section counts its speech)."""
    lengths = [s["duration"] + 0.3 for s in sections]
    total, cuts, acc = sum(lengths), [], 0.0
    for i, x in enumerate(lengths[:-1]):
        acc += x
        k = len(cuts) + 1
        if k < n and abs(acc - total * k / n) <= abs(acc + lengths[i + 1] - total * k / n):
            cuts.append(i + 1)
    bounds = [0] + cuts + [len(sections)]
    return [sections[a:b] for a, b in zip(bounds, bounds[1:])]


def step_parts(d):
    slug = os.path.basename(os.path.normpath(d))
    t, conf, english = setup(d)
    parts = conf["parts"]
    # the two end lines, voiced once per story (a few seconds each) and checked as Tamil
    odir = os.path.join(t, "parts_outro")
    lines = os.path.join(t, "parts_outro_ta.txt")
    outros = [conf.get("outro_next", OUTRO_NEXT), conf.get("outro_last", OUTRO_LAST)]
    open(lines, "w", encoding="utf-8").write("\n".join(outros) + "\n")
    todo = [k for k in (1, 2) if not os.path.exists(os.path.join(odir, f"sec_{k:02d}.wav"))]
    e = tamil.cfg["eleven"]
    if todo:
        run("python3", "-I", os.path.join(KURAL, "eleven.py"), lines, odir, "--sections", ",".join(map(str, todo)),
            "--voice", e["voice"], "--model", e["model"], "--stability", e["stability"], "--similarity", e["similarity"])
    sections = []
    for k, line in enumerate(outros, 1):
        a = tamil.trim(tamil.load(os.path.join(odir, f"sec_{k:02d}.wav")))
        tamil.save(os.path.join(odir, f"trim_{k:02d}.wav"), a)
        text = re.sub(r"^\[[a-z]+\]\s*", "", line)
        sections.append({"n": k, "offset": 0.0, "duration": len(a) / tamil.SR,
                         "words": tamil.word_times(text.split(), tamil.speech_spans(a))})
    otiming = os.path.join(t, "parts_outro_timing.json")
    json.dump({"total": 0, "sections": sections}, open(otiming, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    run(os.environ.get("WHISPER_PY", "python3"), "-c", CHECK, *[os.path.join(odir, f"trim_{k:02d}.wav") for k in (1, 2)])

    ta = json.load(open(os.path.join(t, "timing_ta.json"), encoding="utf-8"))["sections"]
    groups = split_parts(ta, len(parts))
    en = english[0]
    for k, (p, group) in enumerate(zip(parts, groups), 1):
        out = os.path.join(d, "out", f"{slug}_ta_part{k}.mp4")
        segs = [{"from": round(max(0.0, s["offset"] - 0.05), 2), "to": round(s["offset"] + s["duration"] + 0.25, 2)}
                for s in group]
        length = sum(g["to"] - g["from"] for g in segs) + sections[0 if k < len(parts) else 1]["duration"] + 1.1
        print(f"part {k}/{len(parts)}: sections {group[0]['n']}-{group[-1]['n']}, {length:.1f}s")
        if length > MAX_PART:
            sys.exit(f"part {k} would be {length:.0f}s, over a Short's 3 minutes: use more parts")
        if os.path.exists(out):
            print(f"{out} already made")
            continue
        spec = {k2: v for k2, v in en.items() if k2 in ("music", "music_gain", "music_follows", "stings", "data", "background")}
        last = k == len(parts)
        spec.update({
            "name": f"ta_part{k}", "out": out, "work_dir": os.path.join(t, "shorts_work"),
            "scenes": os.path.join(t, "scenes_ta.js"), "timing": os.path.join(d, "timing.json"),
            "caption_timing": os.path.join(t, "timing_ta.json"), "caption_font": "Kavivanar",
            "title_font": "Kavivanar-Regular.ttf", "voiceover": os.path.join(t, "voice_pad_ta.wav"),
            "title": conf["title"], "subtitle": f"பகுதி {k}/{len(parts)}",
            "segments": segs,
            # under the end line, the part's last picture while it still stands (not the slide to the next board)
            "outro": {"wav": os.path.join(odir, f"trim_{2 if last else 1:02d}.wav"), "timing": otiming,
                      "section": 2 if last else 1, "visual_at": round(group[-1]["offset"] + group[-1]["duration"] - 0.4, 2)},
        })
        path = os.path.join(t, f"part{k}_ta.json")
        json.dump(spec, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        run("python3", os.path.join(DOODLE, "short.py"), path)


def step_parts_upload(d):
    slug = os.path.basename(os.path.normpath(d))
    t, conf, _ = setup(d)
    meta = json.load(open(os.path.join(t, "meta_ta.json"), encoding="utf-8"))
    long_ta = json.load(open(os.path.join(t, "upload_ta.results.json")))[0]["url"]
    note = "\n\nகுரல்: என் சொந்தக் குரலின் AI நகல். படங்கள் AI மூலம் வரையப்பட்டவை, இசை எங்களுடையது."
    shorts_list = tamil.cfg.get("playlists", {}).get("shorts_ta", {}).get("id")
    urls = []
    for k, p in enumerate(conf["parts"], 1):
        done = os.path.join(t, f"upload_ta_part{k}.results.json")
        if not os.path.exists(done):
            before = "".join(f"\nபகுதி {j}: {u}" for j, u in enumerate(urls, 1))
            spec = {"defaults": {"privacy": "private", "made_for_kids": False, "ai_content": True, "category_id": 27,
                                 "language": "ta", "refresh_token_env": tamil.cfg["channel"]["refresh_token_env"]},
                    "videos": [{"file": os.path.join(d, "out", f"{slug}_ta_part{k}.mp4"), "title": p["yt_title"],
                                "description": p["yt_text"] + before + f"\nமுழு வீடியோ: {long_ta}" + note,
                                "tags": meta["tags"][:5] + ["shorts", "tamil shorts"], "publish_at": p.get("publish_at"),
                                "playlists": [shorts_list] if shorts_list else []}]}
            path = os.path.join(t, f"upload_ta_part{k}.json")
            json.dump(spec, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
            run("python3", os.path.join(DOODLE, "upload.py"), path)
        urls.append(json.load(open(done))[0]["url"])
    # each earlier part now gets "அடுத்த பகுதி: <link>" at the top of its description
    sys.path.insert(0, DOODLE)
    import urllib.request
    from upload import access_token
    tok = access_token(tamil.cfg["channel"]["refresh_token_env"])
    api = "https://www.googleapis.com/youtube/v3/videos"
    for k, url in enumerate(urls[:-1], 1):
        vid = url.rsplit("/", 1)[-1]
        req = urllib.request.Request(f"{api}?part=snippet&id={vid}", headers={"Authorization": "Bearer " + tok})
        sn = json.load(urllib.request.urlopen(req, timeout=60))["items"][0]["snippet"]
        line = f"அடுத்த பகுதி: {urls[k]}"
        if line in sn["description"]:
            continue
        body = {"id": vid, "snippet": {x: sn[x] for x in ("title", "categoryId", "tags", "defaultLanguage",
                                                           "defaultAudioLanguage") if x in sn}}
        body["snippet"]["description"] = line + "\n\n" + sn["description"]
        req = urllib.request.Request(f"{api}?part=snippet", data=json.dumps(body).encode(), method="PUT",
                                     headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=60)
        print(f"part {k}: linked to part {k + 1}")
    print("parts: " + ", ".join(urls))


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
    {"hooks": step_hooks, "shorts": step_shorts, "upload": step_upload, "parts": step_parts,
     "parts_upload": step_parts_upload}[sys.argv[1]](os.path.abspath(sys.argv[2]))
