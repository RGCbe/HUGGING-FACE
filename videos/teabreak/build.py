"""Build a Tea Break with Manoj video from the files written for it, one step at a time.

    python3 build.py STEP VIDEO_DIR

VIDEO_DIR holds what the writer (the tea-break-weekly skill) prepares:
  voiceover_en.txt  the script, one section per line, spelled as it is said (numbers in words)
  hooks.txt         two hook lines, one per Short
  names.txt         optional: names in the script, one per line, for the listening test
  images.json       picture prompts (doodle/imagegen.py format); "characters" describes how this story's
                    people, animals and things look, and is added to config.json's style. img/end.png
                    is the channel's end card (config.json end_card)
  scenes.js         the boards: pictures, handwriting, stamps, punchlines (see ../01-emu-war/scenes.js)
  thumbnail.js      the thumbnail (see ../01-emu-war/thumbnail.js)
  shorts.json       [{"title", "subtitle", "hook": 1, "segments": [{"from", "to"}]}, ...] on the long timeline
  meta.json         {"title", "description", "tags", "long_at", "shorts_at": [..], "shorts": [{"title", "description"}],
                     "tiktok": {"title", "subtitle", "caption"}}
  caption_replace.json  optional: [["eighteen fifty-nine", "1859"], ...] so captions show numbers as digits

Steps, in order (each can be run again; finished voice lines and pictures are kept):
  voice    voices every line and both hooks a sentence or two at a time, listens to each piece without
           the script (kural/check.py) and tries other seeds until every word is clear, then joins
           and times the voiceover
  images   makes the pictures (Cloudflare FLUX.2 klein, in the style of config.json's style_ref)
  stills   renders one finished frame per board into stills/, plus contact sheets, for review
  video    renders the video, adds music, sound effects, captions; makes the thumbnail
  sound    only the sound again (events, music, mix, captions) on the rendered pictures, after
           changing moods, stings or punchlines in scenes.js
  shorts   cuts both vertical Shorts
  tiktok   the whole story as one vertical video, for the owner to post on TikTok
  upload   writes upload.json for doodle/upload.py: long video and Shorts, private until their times

Needs the voice setup: KURAL_HOME=~/.cache/tea-break VOICE_ENGINE=<config voice_engine> FIXED_CLIPS=0
bash ../kural/setup.sh, then source ~/.cache/tea-break/env.sh.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEOS = os.path.dirname(HERE)
DOODLE = os.path.join(VIDEOS, "doodle")
KURAL = os.path.join(VIDEOS, "kural")
cfg = json.load(open(os.path.join(HERE, "config.json")))
SEEDS = [7, 11, 23, 42, 77, 101]
GAP = 0.5  # silence between lines
BREATH = 0.2  # silence between the pieces of a line
TAIL = 3.0  # the end card: render.mjs runs this long past the voiceover (scenes.js sets D.tail to match)


def run(*cmd, **kw):
    return subprocess.run([str(c) for c in cmd], check=True, **kw)


def env(name):
    if not os.environ.get(name):
        sys.exit(f"{name} is not set: run ../kural/setup.sh for the tea-break voice and source its env.sh")
    return os.environ[name]


def duration(path):
    return float(run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path,
                     capture_output=True, text=True).stdout)


def pieces(line):
    """A line cut into sentences, short ones joined to the next (at least 8 words a piece). The voice
    model slips more in long stretches, and a slip then costs one piece, not the whole line."""
    out, cur = [], ""
    for sentence in re.split(r"(?<=[.?!])\s+", line.strip()):
        cur = f"{cur} {sentence}".strip()
        if len(cur.split()) >= 8:
            out.append(cur)
            cur = ""
    if cur and out and len(cur.split()) < 4:
        out[-1] += " " + cur
    elif cur:
        out.append(cur)
    return out


def say(text_file, out_dir, names):
    """Voice each line of text_file into out_dir/line_NN.wav, a piece at a time (sec_NN.wav, the
    pieces listed in pieces.txt), trying other seeds until Whisper hears every word of every piece."""
    lines = [l.strip() for l in open(text_file, encoding="utf-8") if l.strip()]
    split = [pieces(l) for l in lines]
    flat = [p for ps in split for p in ps]
    os.makedirs(out_dir, exist_ok=True)
    pieces_file = os.path.join(out_dir, "pieces.txt")
    open(pieces_file, "w", encoding="utf-8").write("\n".join(flat) + "\n")
    wav = lambda n: os.path.join(out_dir, f"sec_{n:02d}.wav")
    cache_file = os.path.join(out_dir, "cache.json")
    cache = json.load(open(cache_file)) if os.path.exists(cache_file) else {}  # piece number: the text it passed with
    passed = lambda n: cache.get(str(n)) == flat[n - 1] and os.path.exists(wav(n))
    engine = os.environ.get("TTS_ENGINE", cfg["voice_engine"])
    voice = ["--engine", engine] + (["--ref-text", env("VOICE_REF_TEXT")] if engine == "qwen" else ["--temperature", 0.5])
    problems = {}

    def listen(todo):
        report = os.path.join(out_dir, "check.json")
        run(env("WHISPER_PY"), "-I", os.path.join(KURAL, "check.py"), pieces_file, os.path.join(out_dir, "sec_{n:02d}.wav"),
            report, "--names", names, "--sections", ",".join(map(str, todo)))
        for r in json.load(open(report))["sections"]:
            if r["ok"]:
                cache[str(r["n"])] = flat[r["n"] - 1]
            else:
                problems[r["n"]] = r["problems"]
        json.dump(cache, open(cache_file, "w"), indent=1)

    # pieces voiced by an earlier run that stopped before listening to them
    unheard = [n for n in range(1, len(flat) + 1) if not passed(n) and os.path.exists(wav(n))]
    if unheard:
        listen(unheard)
    todo = [n for n in range(1, len(flat) + 1) if not passed(n)]
    for seed in SEEDS:
        if not todo:
            break
        run(env("TTS_PY"), "-I", os.path.join(KURAL, "tts.py"), env("VOICE_REF"), pieces_file, out_dir, *voice,
            "--sections", ",".join(map(str, todo)), "--seed", seed)
        listen(todo)
        todo = [n for n in todo if not passed(n)]
    if todo:
        sys.exit("NOT CLEAR after every seed. Reword these sentences with simpler words and run `voice` again:\n" +
                 "\n".join(f'  "{flat[n - 1]}": ' + "; ".join(problems[n]) for n in todo))
    breath = os.path.join(out_dir, "breath.wav")
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "lavfi", "-t", BREATH, "-i", "anullsrc=r=24000:cl=mono", breath)
    out, n = [], 0
    for i, ps in enumerate(split, 1):
        parts = [wav(n + k) for k in range(1, len(ps) + 1)]
        n += len(ps)
        out.append(os.path.join(out_dir, f"line_{i:02d}.wav"))
        concat([p for k, part in enumerate(parts) for p in ([breath, part] if k else [part])], out[-1])
    return out


def concat(wavs, out):
    lst = out + ".txt"
    open(lst, "w").write("".join(f"file '{w}'\n" for w in wavs))
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c:a", "pcm_s16le", out)
    os.remove(lst)


def step_voice(d):
    names_file = os.path.join(d, "names.txt")
    names = ",".join(l.strip() for l in open(names_file) if l.strip()) if os.path.exists(names_file) else ""
    names = ",".join(n for n in (names, "Manoj") if n)
    lines = say(os.path.join(d, "voiceover_en.txt"), os.path.join(d, "tts"), names)
    say(os.path.join(d, "hooks.txt"), os.path.join(d, "hooks"), names)
    gap = os.path.join(d, "tts", "gap.wav")
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "lavfi", "-t", GAP, "-i", "anullsrc=r=24000:cl=mono", gap)
    voice = os.path.join(d, "voice.wav")
    concat([p for k, line in enumerate(lines) for p in ([gap, line] if k else [line])], voice)
    # a Tea Break video is 2 to 5 minutes, end card included: a story you finish in a tea break
    shortest, longest = cfg["length_seconds"]
    seconds = duration(voice) + TAIL
    words = len(open(os.path.join(d, "voiceover_en.txt"), encoding="utf-8").read().split())
    per_second = words / duration(voice)
    if not shortest <= seconds <= longest:
        change = (f"cut about {round((seconds - longest) * per_second) + 10} words" if seconds > longest
                  else f"add about {round((shortest - seconds) * per_second) + 10} words")
        sys.exit(f"the video would be {seconds:.0f}s, outside Tea Break's {shortest}-{longest}s: {change} "
                 "and run voice again (unchanged sentences are kept)")
    whisper = env("WHISPER_PY")
    run(whisper, "-I", os.path.join(DOODLE, "timing.py"), os.path.join(d, "voiceover_en.txt"),
        os.path.join(d, "tts", "line_{n:02d}.wav"), GAP, os.path.join(d, "timing.json"))
    run(whisper, "-I", os.path.join(DOODLE, "timing.py"), os.path.join(d, "hooks.txt"),
        os.path.join(d, "hooks", "line_{n:02d}.wav"), 0, os.path.join(d, "hooks_timing.json"))
    print(f"voice: {duration(voice):.1f}s, every word clear")


def step_images(d):
    img = os.path.join(d, "img")
    os.makedirs(img, exist_ok=True)
    spec = json.load(open(os.path.join(d, "images.json")))
    spec["style"] = (cfg["style"] + " " + spec.pop("characters", "")).strip()
    spec.setdefault("aspect", "16:9")
    spec["style_ref"] = "ref"
    for name, src in (("ref", cfg["style_ref"]), ("end", cfg["end_card"])):
        if not os.path.exists(os.path.join(img, f"{name}.png")):
            shutil.copy(os.path.normpath(os.path.join(HERE, src)), os.path.join(img, f"{name}.png"))
    full = os.path.join(d, "images_full.json")
    json.dump(spec, open(full, "w"), indent=1)
    run("python3", "-I", os.path.join(DOODLE, "imagegen.py"), full, img, "--engine", os.environ.get("IMAGE_ENGINE", "cloudflare"))


def render(d, *args):
    data = os.path.join(d, "data.json")
    json.dump({"img": os.path.join(os.path.abspath(d), "img")}, open(data, "w"))
    run("node", os.path.join(DOODLE, "render.mjs"), "--timing", os.path.join(d, "timing.json"), "--data", data, *args)


def step_stills(d):
    st = os.path.join(d, "stills")
    shutil.rmtree(st, ignore_errors=True)
    render(d, "--scenes", os.path.join(d, "scenes.js"), "--out", os.path.join(st, "s.mp4"), "--stills", "auto")
    pngs = sorted((f for f in os.listdir(st) if f.endswith(".png")), key=lambda f: float(f[2:-4]))
    for k in range(0, len(pngs), 8):
        group = pngs[k:k + 8] + [None] * (8 - len(pngs[k:k + 8]))
        args, chain = [], ""
        for i, f in enumerate(group):
            args += ["-i", os.path.join(st, f)] if f else ["-f", "lavfi", "-i", "color=c=white:s=800x450:d=1"]
            chain += f"[{i}]scale=800:450[v{i}];"
        chain += "".join(f"[v{2 * r}][v{2 * r + 1}]hstack[r{r}];" for r in range(4)) + "[r0][r1][r2][r3]vstack=4"
        run("ffmpeg", "-nostdin", "-v", "error", "-y", *args, "-filter_complex", chain, "-frames:v", "1",
            os.path.join(st, f"sheet_{k // 8 + 1}.png"))
    print(f"stills: {len(pngs)} boards in {st} (sheet_*.png shows 8 per sheet, in order)")


def step_video(d):
    slug = os.path.basename(os.path.normpath(d))
    out = os.path.join(d, "out")
    os.makedirs(out, exist_ok=True)
    render(d, "--scenes", os.path.join(d, "scenes.js"), "--out", os.path.join(d, "silent.mp4"))
    video = step_sound(d)
    thumb = os.path.join(d, "thumb")
    render(d, "--scenes", os.path.join(d, "thumbnail.js"), "--out", os.path.join(thumb, "t.mp4"), "--stills", "3")
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", os.path.join(thumb, "t_3.00.png"), "-vf", "scale=1280:720:flags=lanczos",
        "-q:v", "3", os.path.join(out, f"{slug}_thumbnail.jpg"))
    print(f"video: {video} ({duration(video):.1f}s), thumbnail: {slug}_thumbnail.jpg")


def step_sound(d):
    """The sound again on the rendered pictures: events, the mood score (or the one-mood loop when
    scenes.js sets no moods), the mix, captions."""
    slug = os.path.basename(os.path.normpath(d))
    out = os.path.join(d, "out")
    os.makedirs(out, exist_ok=True)
    total = json.load(open(os.path.join(d, "timing.json")))["total"] + TAIL
    silent = os.path.join(d, "silent.mp4")
    events = os.path.join(d, "events.json")
    render(d, "--scenes", os.path.join(d, "scenes.js"), "--out", os.devnull, "--events", events)
    music = os.path.join(d, "music.wav")
    stings = os.path.join(d, "music_stings.wav")
    if os.path.exists(stings):
        os.remove(stings)
    seed = int(hashlib.sha1(slug.encode()).hexdigest(), 16) % 1000
    if any(e["kind"] == "mood" for e in json.load(open(events))):
        if not shutil.which("fluidsynth"):
            sys.exit("scenes.js sets moods, but fluidsynth is missing: run ../kural/setup.sh (it installs it)")
        run(env("TTS_PY"), "-I", os.path.join(DOODLE, "score.py"), music, total + 1, "--events", events, "--seed", seed)
    else:
        run(env("TTS_PY"), "-I", os.path.join(DOODLE, "music.py"), music, total + 1, "--seed", seed)
    voice_pad = os.path.join(d, "voice_pad.wav")
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", os.path.join(d, "voice.wav"), "-af", f"apad=pad_dur={TAIL}", voice_pad)
    mix = os.path.join(d, "mix.m4a")
    run("python3", os.path.join(DOODLE, "mix.py"), voice_pad, music, mix, "--music-gain", cfg["music_gain"], "--events", events,
        *(["--stings", stings] if os.path.exists(stings) else []))
    ass = os.path.join(d, "captions.ass")
    run("python3", os.path.join(DOODLE, "captions.py"), os.path.join(d, "timing.json"), ass, *replace(d))
    video = os.path.join(out, f"{slug}.mp4")
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", silent, "-i", mix, "-vf",
        f"ass={ass}:fontsdir={os.path.join(DOODLE, 'fonts')}", "-af", f"afade=t=out:st={total - 1.5}:d=1.5", "-shortest",
        "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart", video)
    return video


def replace(d):
    path = os.path.join(d, "caption_replace.json")
    return ["--replace", path] if os.path.exists(path) else []


def step_shorts(d):
    slug = os.path.basename(os.path.normpath(d))
    out = os.path.join(d, "out")
    for k, s in enumerate(json.load(open(os.path.join(d, "shorts.json"))), 1):
        spec = {
            "name": f"short{k}", "out": os.path.join(out, f"{slug}_short{k}.mp4"), "work_dir": os.path.join(d, "shorts_work"),
            "scenes": os.path.join(d, "scenes.js"), "timing": os.path.join(d, "timing.json"),
            "voiceover": os.path.join(d, "voice.wav"), "title": s["title"], "subtitle": s["subtitle"],
            "hook": {"wav": os.path.join(d, "hooks", f"line_{s['hook']:02d}.wav"), "timing": os.path.join(d, "hooks_timing.json"),
                     "section": s["hook"], "visual_from": s.get("hook_visual_from", 0.3), "visual_to": s.get("hook_visual_to", 6.0)},
            "music": os.path.join(d, "music.wav"), "music_gain": cfg["music_gain"], "music_follows": True,
            "segments": s["segments"], "data": {"img": os.path.join(d, "img")}, "background": "0xfff8e7",
        }
        if replace(d):
            spec["replace"] = replace(d)[1]
        if os.path.exists(os.path.join(d, "music_stings.wav")):
            spec["stings"] = os.path.join(d, "music_stings.wav")
        path = os.path.join(d, f"short{k}.json")
        json.dump(spec, open(path, "w"), indent=1)
        run("python3", os.path.join(DOODLE, "short.py"), path, cwd=VIDEOS)


def step_tiktok(d):
    """The whole story as one vertical video (TikTok pays only for videos over a minute): the board
    in the middle of a cream page, the title above it and big captions under it, the long video's sound."""
    slug = os.path.basename(os.path.normpath(d))
    meta = json.load(open(os.path.join(d, "meta.json")))["tiktok"]
    work = os.path.join(d, "tiktok_work")
    os.makedirs(work, exist_ok=True)
    silent = os.path.join(work, "silent.mp4")
    render(d, "--scenes", os.path.join(d, "scenes.js"), "--out", silent, "--layout", "vertical")
    ass = os.path.join(work, "captions.ass")
    run("python3", os.path.join(DOODLE, "captions.py"), os.path.join(d, "timing.json"), ass, "--layout", "vertical", *replace(d))
    for name in ("title", "subtitle"):
        open(os.path.join(work, f"{name}.txt"), "w").write(meta[name])
    font = os.path.join(DOODLE, "fonts", "PatrickHand-Regular.ttf")
    total = json.load(open(os.path.join(d, "timing.json")))["total"] + TAIL
    # the vertical layout draws the 1920x1080 board 1080x608 at y=660
    graph = (f"[1:v]crop=1080:608:0:660[board];[0:v][board]overlay=0:660:shortest=1,"
             f"drawtext=fontfile={font}:textfile={os.path.join(work, 'title.txt')}:fontsize=118:fontcolor=0xe8590c:"
             f"x=(w-text_w)/2:y=250,"
             f"drawtext=fontfile={font}:textfile={os.path.join(work, 'subtitle.txt')}:fontsize=72:fontcolor=0x1d1d1f:"
             f"x=(w-text_w)/2:y=420,ass={ass}:fontsdir={os.path.join(DOODLE, 'fonts')}[v]")
    video = os.path.join(d, "out", f"{slug}_tiktok.mp4")
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0xfff8e7:s=1080x1920:r=30", "-i", silent,
        "-i", os.path.join(d, "mix.m4a"), "-filter_complex", graph, "-map", "[v]", "-map", "2:a",
        "-af", f"afade=t=out:st={total - 1.5}:d=1.5", "-shortest", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", video)
    print(f"tiktok: {video} ({duration(video):.1f}s)\ncaption: {meta['caption']}")


def step_upload(d):
    slug = os.path.basename(os.path.normpath(d))
    meta = json.load(open(os.path.join(d, "meta.json")))
    out = os.path.abspath(os.path.join(d, "out"))
    note = ("\n\nThe voice is an AI copy of my own voice; the pictures are made with an AI image model "
            "(FLUX.2 klein), and the music is original.")
    # the long video goes in "long" and in its topic's playlists (topics.json), each Short in "shorts"
    topic = next((t for t in json.load(open(os.path.join(HERE, "topics.json"))) if t["slug"] == slug), {})
    playlist = lambda key: cfg.get("playlists", {}).get(key, {}).get("id")
    long_lists = [playlist(k) for k in ["long"] + topic.get("playlists", []) if playlist(k)]
    videos = [{"file": os.path.join(out, f"{slug}.mp4"), "thumbnail": os.path.join(out, f"{slug}_thumbnail.jpg"),
               "title": meta["title"], "description": meta["description"] + note, "tags": meta["tags"],
               "publish_at": meta["long_at"], "playlists": long_lists}]
    for k, (s, when) in enumerate(zip(meta["shorts"], meta["shorts_at"]), 1):
        videos.append({"file": os.path.join(out, f"{slug}_short{k}.mp4"), "title": s["title"],
                       "description": s["description"] + note, "tags": meta["tags"][:5] + ["shorts"], "publish_at": when,
                       "playlists": [p for p in [playlist("shorts")] if p]})
    upload = {"defaults": {"privacy": "private", "made_for_kids": False, "ai_content": True, "category_id": 27,
                           "language": "en", "refresh_token_env": cfg["channel"]["refresh_token_env"]}, "videos": videos}
    path = os.path.join(d, "upload.json")
    json.dump(upload, open(path, "w"), indent=2, ensure_ascii=False)
    print(f"wrote {path}: upload with python3 {os.path.join(DOODLE, 'upload.py')} {path}")


STEPS = {"voice": step_voice, "images": step_images, "stills": step_stills, "video": step_video, "sound": step_sound,
         "shorts": step_shorts, "tiktok": step_tiktok, "upload": step_upload}
if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in STEPS:
        sys.exit(__doc__)
    STEPS[sys.argv[1]](os.path.abspath(sys.argv[2]))
