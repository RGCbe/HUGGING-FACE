"""Make one Super Kural Short from a story spec, from voice to finished video (and upload).

    python3 make.py STORY_JSON [--publish-at 2026-10-22T12:00:00Z | --public] [--upload]

STORY_JSON (see stories/0003.json and the kural-daily skill) holds the kural number, a title,
the story lines with what to draw, the spoken meaning and the lesson. Steps:

  1. check the spec (known drawings and places, cue words that are really in the line, length)
  2. voice each new line in the AI voice and listen to it with check.py; any line that is not
     crystal clear is voiced again with another seed, up to SEEDS times, then the run stops
     and names the words to reword
  3. word timings, scenes (story.js), portrait render, captions, the Super Kural music ducked
     under the voice, title on top; then the finished mix is listened to once more
  4. write upload.json next to the video, and upload it with doodle/upload.py if --upload

Environment: KURAL_WORK (work folder), KURAL_OUT (finished videos), TTS_ENGINE (qwen or
chatterbox), VOICE_REF and, for qwen, VOICE_REF_TEXT (the speaker's sample, trimmed to whole words
by ref_prep.py, and its words), FIXED_DIR (the pre-approved intro/says/goodbye clips), TTS_PY and
WHISPER_PY (Pythons with the voice engine and faster-whisper), PLAYWRIGHT_MODULE if Playwright is
global. setup.sh writes all of these.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOODLE = os.path.join(HERE, "..", "doodle")
SEEDS = [7, 11, 23, 42, 77, 101]
GAP = 0.5
MUSIC_GAINS = [0.22, 0.15, 0.10]  # music level under the voice, loudest first; the music matters here
ENGINE = os.environ.get("TTS_ENGINE", "qwen")
FIXED = {  # pre-approved clips (FIXED_DIR/NAME.wav, NAME_qwen.wav for Qwen3-TTS) and the words they say
    "intro": "Hello little friends! It's Super Kural time!",
    "says": "Now listen to what the great poet Thiruvalluvar says.",
    # "Kural" at the very end of a sentence kept coming out as "coral" in the Qwen voice
    "outro": "See you tomorrow for the next Super Kural, friends!" if ENGINE == "qwen" else
             "See you tomorrow for the next Super Kural!",
}
FIXED_SUFFIX = "_qwen" if ENGINE == "qwen" else ""
PEOPLE = ["kid", "boy", "girl", "grandma", "grandpa", "mom", "dad", "teacher", "man", "woman", "sage"]
THINGS = ["tree", "mango", "flower", "lotus", "sun", "moon", "star", "cloud", "river", "hill", "bird", "dog", "cat",
          "cow", "fish", "elephant", "peacock", "house", "school", "temple", "shop", "well", "book", "palmleaf",
          "lamp", "ball", "kite", "bag", "pencil", "plate", "leaf", "pot", "gift", "heart", "clock", "phone",
          "bicycle", "boat", "bench", "money", "bulb", "coin", "trophy", "medal", "check", "cross", "burst", "face"]
SLOTS = ["left", "center", "right", "top-left", "top", "top-right", "middle-left", "middle", "middle-right", "bottom"]
MOODS = ["happy", "sad", "angry", "surprised", "laugh", "calm", "worried"]
ARMS = ["down", "up", "wave", "point", "give", "hips", "pray"]
COLORS = ["red", "blue", "green", "orange", "yellow", "brown", "grey", "pink", "purple", "black"]
NOT_SPOKEN = ["kural", "thiruvalluvar", "valluvar", "paati", "thatha", "amma", "appa"]  # say these in the fixed clips only, or in English


def env(name, default=None):
    v = os.environ.get(name, default)
    if v is None:
        sys.exit(f"set {name}")
    return v


def run(*cmd, **kw):
    print("+", " ".join(str(c) for c in cmd)[:200], flush=True)
    return subprocess.run([str(c) for c in cmd], check=True, **kw)


def words(text):
    return re.findall(r"[A-Za-z0-9']+", text)


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def validate(spec):
    errors = []
    lines = spec["lines"]
    if not 3 <= len(lines) <= 7:
        errors.append(f"use 3 to 7 story lines, not {len(lines)}")
    spoken = [l["say"] for l in lines] + [spec["meaning"], spec["lesson"]]
    total = sum(len(words(s)) for s in spoken)
    if not 80 <= total <= 150:
        errors.append(f"the story, meaning and lesson should be 80-150 words together, not {total}")
    for s in spoken:
        for w in words(s):
            if norm(w) in NOT_SPOKEN:
                errors.append(f'"{w}" in "{s[:40]}...": the voice cannot say it clearly; use English words (Grandma, Grandpa)')
        if len(words(s)) > 40:
            errors.append(f'line too long for one board (max 40 words): "{s[:40]}..."')
    if len(spec["title"]) > 45:
        errors.append(f'title is {len(spec["title"])} characters; keep it under 45')
    if len(spec["lesson_short"]) > 44:
        errors.append("lesson_short must fit on screen: 44 characters at most")
    for i, l in enumerate(lines, 1):
        said = [norm(w) for w in words(l["say"])]
        if not 1 <= len(l["board"]) <= 5:
            errors.append(f"line {i}: draw 1 to 5 things per board")
        used = []
        for it in l["board"]:
            kind = [k for k in ("draw", "text", "bubble", "stamp", "arrow") if k in it]
            if len(kind) != 1:
                errors.append(f"line {i}: each item needs one of draw/text/bubble/stamp/arrow: {it}")
                continue
            if "draw" in it and it["draw"] not in PEOPLE + THINGS:
                errors.append(f'line {i}: unknown drawing "{it["draw"]}"')
            if it.get("at", "center") not in SLOTS:
                errors.append(f'line {i}: unknown place "{it.get("at")}"')
            if "draw" in it:
                if it.get("at", "center") in used:
                    errors.append(f'line {i}: two drawings in "{it.get("at", "center")}"')
                used.append(it.get("at", "center"))
            if it.get("mood") and it["mood"] not in MOODS:
                errors.append(f'line {i}: mood must be one of {MOODS}')
            if it.get("arms") and it["arms"] not in ARMS:
                errors.append(f'line {i}: arms must be one of {ARMS}')
            if it.get("color") and it["color"] not in COLORS:
                errors.append(f'line {i}: color must be one of {COLORS}')
            for s in it.get("arrow", []):
                if s not in SLOTS:
                    errors.append(f'line {i}: unknown arrow place "{s}"')
            if it.get("cue"):
                cue = [norm(w) for w in words(it["cue"])]
                if not any(said[k:k + len(cue)] == cue for k in range(len(said))):
                    errors.append(f'line {i}: cue "{it["cue"]}" is not in the line')
    for k in ("lesson_draw", "kid"):
        if spec.get(k) and spec[k] not in PEOPLE + THINGS:
            errors.append(f'{k}: unknown drawing "{spec[k]}"')
    if errors:
        sys.exit("story spec problems:\n  " + "\n  ".join(errors))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("story")
    ap.add_argument("--publish-at")
    ap.add_argument("--public", action="store_true", help="go public as soon as it is uploaded")
    ap.add_argument("--upload", action="store_true")
    a = ap.parse_args()

    spec = json.load(open(a.story))
    validate(spec)
    n = spec["kural"]
    kural = json.load(open(os.path.join(HERE, "kurals.json")))["kurals"][n - 1]
    assert kural["n"] == n
    work = os.path.join(env("KURAL_WORK"), f"{n:04d}")
    out_dir = env("KURAL_OUT")
    fixed = env("FIXED_DIR")
    os.makedirs(work, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    tts_py, whisper_py = env("TTS_PY"), env("WHISPER_PY")

    # Sections: hook, intro, story, says, meaning, lesson, goodbye.
    story = [l["say"] for l in spec["lines"]]
    sections = [("story", story[0]), ("fixed:intro", FIXED["intro"])] + [("story", s) for s in story[1:]]
    sections += [("fixed:says", FIXED["says"]), ("story", spec["meaning"]), ("story", spec["lesson"]),
                 ("fixed:outro", FIXED["outro"])]
    text = os.path.join(work, "voiceover.txt")
    open(text, "w").write("".join(s + "\n" for _, s in sections))
    wav = lambda i: os.path.join(work, f"sec_{i:02d}.wav")
    new = [i for i, (kind, _) in enumerate(sections, 1) if kind == "story"]
    for i, (kind, _) in enumerate(sections, 1):
        if kind.startswith("fixed:"):
            shutil.copy(os.path.join(fixed, kind[6:] + FIXED_SUFFIX + ".wav"), wav(i))

    # 2. Voice, listen, and voice again until every line is clear. Lines that passed on an earlier
    # run with the same words are kept, so a rerun after a reword only voices what changed.
    names = ",".join(spec.get("names", []))
    cache_file = os.path.join(work, "voice_cache.json")
    cache = json.load(open(cache_file)) if os.path.exists(cache_file) else {}
    todo = [i for i in new if not (cache.get(str(i)) == sections[i - 1][1] and os.path.exists(wav(i)))]
    problems = {}
    for seed in SEEDS:
        if not todo:
            break
        voice = ["--engine", ENGINE] + (["--ref-text", env("VOICE_REF_TEXT")] if ENGINE == "qwen" else [])
        run(tts_py, "-I", os.path.join(HERE, "tts.py"), env("VOICE_REF"), text, work, *voice,
            "--sections", ",".join(map(str, todo)), "--seed", seed)
        report = os.path.join(work, "check.json")
        run(whisper_py, "-I", os.path.join(HERE, "check.py"), text, os.path.join(work, "sec_{n:02d}.wav"), report,
            "--names", names, "--sections", ",".join(map(str, todo)))
        result = {r["n"]: r for r in json.load(open(report))["sections"]}
        for i in todo:
            if result[i]["ok"]:
                shutil.copy(wav(i), wav(i).replace(".wav", "_ok.wav"))
            else:
                problems[i] = result[i]["problems"]
        todo = [i for i in todo if not result[i]["ok"]]
    if todo:
        lines = [f'  line "{sections[i - 1][1]}": ' + "; ".join(problems[i]) for i in todo]
        sys.exit("NOT CLEAR after every seed. Reword these lines with simpler words and run again:\n" + "\n".join(lines))
    for i in new:
        if os.path.exists(wav(i).replace(".wav", "_ok.wav")):
            shutil.move(wav(i).replace(".wav", "_ok.wav"), wav(i))
        cache[str(i)] = sections[i - 1][1]
    json.dump(cache, open(cache_file, "w"), indent=1)

    # 3. Join, time, draw, caption, score, mix, title.
    voice = os.path.join(work, "voice.wav")
    silence = os.path.join(work, "gap.wav")
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", GAP, silence)
    lst = os.path.join(work, "voice.txt")
    open(lst, "w").write("".join(f"file '{wav(i)}'\n" + (f"file '{silence}'\n" if i < len(sections) else "")
                                 for i in range(1, len(sections) + 1)))
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-ar", "24000", "-ac", "1", voice)
    timing = os.path.join(work, "timing.json")
    run(whisper_py, "-I", os.path.join(DOODLE, "timing.py"), text, os.path.join(work, "sec_{n:02d}.wav"), GAP, timing)

    k = {n: i for i, n in enumerate([kind for kind, _ in sections], 1)}
    data = {
        "n": n, "next": n + 1, "kid": spec.get("kid", "girl"),
        "kural": {key: kural[key] for key in ("line1", "line2", "translit", "chapter_en", "chapter_ta")},
        "lines": [{"section": s, "board": l["board"]} for s, l in
                  zip([1] + list(range(3, 3 + len(story) - 1)), spec["lines"])],
        "intro_section": 2, "says_section": k["fixed:says"], "meaning_section": k["fixed:says"] + 1,
        "lesson_section": k["fixed:says"] + 2, "outro_section": k["fixed:outro"],
        "lesson_short": spec["lesson_short"], "lesson_draw": spec.get("lesson_draw", "star"),
    }
    data_json = os.path.join(work, "data.json")
    json.dump(data, open(data_json, "w"), ensure_ascii=False)
    render = ["node", os.path.join(DOODLE, "render.mjs"), "--scenes", os.path.join(HERE, "story.js"), "--timing", timing,
              "--data", data_json, "--layout", "portrait"]
    run(*render, "--out", os.path.join(work, "still.mp4"), "--stills", "auto")
    silent = os.path.join(work, "silent.mp4")
    run(*render, "--out", silent)

    ass = os.path.join(work, "captions.ass")
    run("python3", os.path.join(DOODLE, "captions.py"), timing, ass, "--layout", "vertical", "--margin", "110")
    seconds = json.load(open(timing))["total"] + 1.2
    music = os.path.join(work, "music.wav")
    run(whisper_py, "-I", os.path.join(HERE, "music.py"), music, seconds, "--seed", n)  # needs numpy

    # The finished mix, cut back into sections, must still pass the listening test; if the music
    # hides a word anywhere, it is turned down and mixed again.
    audio = os.path.join(work, "audio.m4a")
    mixed = os.path.join(work, "mixed_{n:02d}.wav")
    final_check = os.path.join(work, "check_mix.json")
    for gain in MUSIC_GAINS:
        run("python3", os.path.join(DOODLE, "mix.py"), voice, music, audio, "--music-gain", gain)
        for s in json.load(open(timing))["sections"]:
            # a little of the silent gap on each side, so no word is clipped at the cut
            run("ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", max(0, s["offset"] - 0.2), "-t", s["duration"] + 0.4, "-i", audio,
                "-ac", "1", "-ar", "16000", mixed.format(n=s["n"]))
        run(whisper_py, "-I", os.path.join(HERE, "check.py"), text, mixed, final_check, "--names", names,
            "--sections", ",".join(map(str, new)))
        if json.load(open(final_check))["ok"]:
            break
    else:
        sys.exit("even with the music turned down, some words are not clear in the finished mix; see " + final_check)

    font = os.path.join(DOODLE, "fonts", "PatrickHand-Regular.ttf")
    title_file, sub_file = os.path.join(work, "title.txt"), os.path.join(work, "subtitle.txt")
    open(title_file, "w").write(f"SUPER KURAL #{n}")
    open(sub_file, "w").write(spec["title"])
    out = os.path.join(out_dir, f"super_kural_{n:04d}.mp4")
    vf = (f"drawtext=fontfile={font}:textfile={title_file}:fontsize=110:fontcolor=0xe8590c:x=(w-text_w)/2:y=95,"
          f"drawtext=fontfile={font}:textfile={sub_file}:fontsize=62:fontcolor=0x1d1d1f:x=(w-text_w)/2:y=245,"
          f"ass={ass}:fontsdir={os.path.join(DOODLE, 'fonts')}")
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", silent, "-i", audio, "-vf", vf, "-af", "apad", "-shortest",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart", out)

    # 4. Upload details.
    title = f"Super Kural #{n}: {spec['title']}"
    description = (
        f"{spec['title']} - a short story for children about Thirukkural {n}.\n\n"
        f"{kural['line1']}\n{kural['line2']}\n({kural['translit']})\n\n"
        f"Meaning: {spec['meaning']}\n\nToday's lesson: {spec['lesson']}\n\n"
        f"Chapter {kural['chapter']}: {kural['chapter_en']} ({kural['chapter_ta']})\n"
        f"G. U. Pope's translation (1886): \"{kural['pope']}\"\n\n"
        "A new Super Kural every day. The voice is an AI copy of my own voice; the music is original.\n"
        "#thirukkural #tamil #kidsstories #shorts"
    )
    video = {"file": out, "title": title, "description": description,
             "tags": ["thirukkural", f"thirukkural {n}", "kural", "super kural", "thirukkural for kids",
                      "tamil moral stories", "kids stories", "moral stories for kids", kural["chapter_en"].lower()]
             + spec.get("tags", [])}
    if a.publish_at:
        video["publish_at"] = a.publish_at
    upload = {"defaults": {"privacy": "public" if a.public and not a.publish_at else "private", "made_for_kids": True, "ai_content": True, "category_id": 27,
                           "language": "en"}, "videos": [video]}
    upload_json = os.path.join(out_dir, f"super_kural_{n:04d}.upload.json")
    json.dump(upload, open(upload_json, "w"), ensure_ascii=False, indent=1)
    print(f"\nwrote {out}\nstills: {work}/still_*.png\nupload details: {upload_json}")
    if a.upload:
        run("python3", os.path.join(DOODLE, "upload.py"), upload_json)


if __name__ == "__main__":
    main()
