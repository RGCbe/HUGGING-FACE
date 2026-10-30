"""Cut a vertical Short (1080x1920) out of a doodle video.

    python3 short.py SPEC_JSON

The Short opens on a new hook line (its own audio, over the long video's first frames) and then
plays stretches of the long voiceover with the matching doodle frames, re-rendered in the vertical
layout. A title sits above the drawing and big captions below it. SPEC_JSON keys:

  name, out, work_dir, scenes, timing, voiceover (WAV of the whole long voiceover),
  replace (caption replacements JSON), title, subtitle,
  hook: {wav, timing, section, visual_from?, visual_to}   timing is timing.py output for the hook
                                               line; the picture under it is the long video's
                                               visual_from..visual_to
  music (optional): background music WAV, mixed under the voice with doodle/mix.py
  music_gain (optional): music level before ducking (default 0.30; Shorts on phone speakers need less)
  music_follows (optional): true when music is the long video's own track (a score.py mood score):
                   the Short then takes the music from the same moments as its pictures, so each
                   stretch keeps its mood; stings (optional) is the score's stings track, cut the same way
  segments: [{from, to, visual_to?}, ...]      seconds on the long timeline; visual_to freezes
                                               the picture early (to skip a camera pan)
  data (optional): passed to render.mjs --data, e.g. {"img": "01-emu-war/img"} for illustrated scenes
                   ("img" may be relative to the current folder)
  background (optional): colour around the board instead of white, e.g. "0xfff8e7"
Needs ffmpeg and node with Playwright; run from the folder that holds the doodle/ engine.
"""
import json
import os
import subprocess
import sys

def expand(v):
    """Paths in the spec may use environment variables, e.g. "$TTS_DIR/full_en.wav"."""
    if isinstance(v, str):
        return os.path.expandvars(v)
    if isinstance(v, list):
        return [expand(x) for x in v]
    if isinstance(v, dict):
        return {k: expand(x) for k, x in v.items()}
    return v


spec = expand(json.load(open(sys.argv[1])))
here = os.path.dirname(os.path.abspath(__file__))
work = os.path.join(spec["work_dir"], spec["name"])
os.makedirs(work, exist_ok=True)
PAUSE = 0.25
FPS = 30


def run(*cmd):
    subprocess.run(cmd, check=True)


data_args = []
if spec.get("data"):
    data = dict(spec["data"])
    if data.get("img"):
        data["img"] = os.path.abspath(data["img"])
    data_json = os.path.join(work, "data.json")
    json.dump(data, open(data_json, "w"))
    data_args = ["--data", data_json]


def render(t0, t1, out):
    run("node", os.path.join(here, "render.mjs"), "--scenes", spec["scenes"], "--timing", spec["timing"],
        "--layout", "vertical", "--from", f"{t0}", "--to", f"{t1}", "--out", out, *data_args)


def hold(src, dur, out):
    """Re-encode src padded with its last frame so it lasts exactly dur seconds."""
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", src, "-vf",
        f"tpad=stop_mode=clone:stop_duration={dur},trim=duration={dur},fps={FPS}",
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", out)


def probe(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                check=True, capture_output=True, text=True).stdout)


# 1. Audio: hook line, a short pause, then each stretch of the long voiceover.
hook = spec["hook"]
hook_dur = probe(hook["wav"]) + PAUSE
parts, words, clock = [], [], 0.0
hook_words = json.load(open(hook["timing"]))["sections"][hook["section"] - 1]
words += [{"w": w["w"], "t0": w["t0"] - hook_words["offset"], "t1": w["t1"] - hook_words["offset"]} for w in hook_words["words"]]
hook_audio = os.path.join(work, "a0.wav")
run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", hook["wav"], "-af", f"apad=pad_dur={PAUSE}",
    "-ar", "24000", "-ac", "1", hook_audio)
parts.append(hook_audio)
clock = hook_dur
long_words = [w for s in json.load(open(spec["timing"]))["sections"] for w in s["words"]]
for k, seg in enumerate(spec["segments"], 1):
    a = os.path.join(work, f"a{k}.wav")
    dur = seg["to"] - seg["from"]
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{seg['from']}", "-t", f"{dur}", "-i", spec["voiceover"],
        "-af", f"afade=t=in:d=0.03,afade=t=out:st={dur - 0.05}:d=0.05", "-ar", "24000", "-ac", "1", a)
    parts.append(a)
    words += [{"w": w["w"], "t0": w["t0"] - seg["from"] + clock, "t1": w["t1"] - seg["from"] + clock}
              for w in long_words if w["t0"] >= seg["from"] - 0.01 and w["t1"] <= seg["to"] + 0.05]
    clock += dur
total = clock
lst = os.path.join(work, "audio.txt")
open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
voice = os.path.join(work, "voice.wav")
run("ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, voice)
audio = os.path.join(work, "audio.m4a")


def follow(track, out):
    """track cut at the Short's moments of the long video: under the hook its pictures' stretch,
    then each segment, joined with short fades."""
    spans = [(hook.get("visual_from", 0.0), hook_dur)] + [(s["from"], s["to"] - s["from"]) for s in spec["segments"]]
    graph = "".join(f"[0:a]atrim=start={t0}:duration={dur},asetpts=PTS-STARTPTS,"
                    f"afade=t=in:d=0.15,afade=t=out:st={max(0, dur - 0.15)}:d=0.15[m{k}];" for k, (t0, dur) in enumerate(spans))
    graph += "".join(f"[m{k}]" for k in range(len(spans))) + f"concat=n={len(spans)}:v=0:a=1[out]"
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", track, "-filter_complex", graph, "-map", "[out]", out)
    return out


if spec.get("music"):
    music = follow(spec["music"], os.path.join(work, "music.wav")) if spec.get("music_follows") else spec["music"]
    stings = ["--stings", follow(spec["stings"], os.path.join(work, "stings.wav"))] if spec.get("stings") else []
    run("python3", os.path.join(here, "mix.py"), voice, music, audio,
        "--music-gain", str(spec.get("music_gain", 0.30)), *stings)
else:
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", voice, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
        "-ar", "44100", "-c:a", "aac", "-b:a", "160k", audio)

# 2. Captions on the Short's own clock.
timing = os.path.join(work, "timing.json")
json.dump({"total": total, "sections": [{"n": 1, "offset": 0, "duration": total, "words": words}]}, open(timing, "w"))
ass = os.path.join(work, "captions.ass")
cap_cmd = ["python3", os.path.join(here, "captions.py"), timing, ass, "--layout", "vertical"]
if spec.get("replace"):
    cap_cmd += ["--replace", spec["replace"]]
run(*cap_cmd)

# 3. Pictures: the long video's opening under the hook, then each stretch, frozen where asked.
clips = []
pieces = [(hook.get("visual_from", 0.0), hook["visual_to"], hook_dur)] + [
    (s["from"], s.get("visual_to", s["to"]), s["to"] - s["from"]) for s in spec["segments"]]
for k, (t0, t1, dur) in enumerate(pieces):
    raw = os.path.join(work, f"v{k}_raw.mp4")
    render(t0, min(t1, t0 + dur), raw)
    clip = os.path.join(work, f"v{k}.mp4")
    hold(raw, dur, clip)
    clips.append(clip)
vlst = os.path.join(work, "video.txt")
open(vlst, "w").write("".join(f"file '{c}'\n" for c in clips))
silent = os.path.join(work, "silent.mp4")
run("ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", vlst, "-c", "copy", silent)

# 4. Title, captions and sound.
font = os.path.join(here, "fonts", "PatrickHand-Regular.ttf")
title_file = os.path.join(work, "title.txt")
sub_file = os.path.join(work, "subtitle.txt")
open(title_file, "w").write(spec["title"])
open(sub_file, "w").write(spec["subtitle"])
text = (f"drawtext=fontfile={font}:textfile={title_file}:fontsize=118:fontcolor=0xe8590c:x=(w-text_w)/2:y=250,"
        f"drawtext=fontfile={font}:textfile={sub_file}:fontsize=72:fontcolor=0x1d1d1f:x=(w-text_w)/2:y=420,"
        f"ass={ass}:fontsdir={os.path.join(here, 'fonts')}")
if spec.get("background"):
    # the vertical layout draws the 1920x1080 board 1080x608 at y=660; lay it on a coloured page
    inputs = ["-f", "lavfi", "-i", f"color=c={spec['background']}:s=1080x1920:r={FPS}", "-i", silent, "-i", audio]
    graph = f"[1:v]crop=1080:608:0:660[board];[0:v][board]overlay=0:660:shortest=1,{text}[v]"
    maps = ["-filter_complex", graph, "-map", "[v]", "-map", "2:a"]
else:
    inputs, maps = ["-i", silent, "-i", audio], ["-vf", text]
run("ffmpeg", "-nostdin", "-v", "error", "-y", *inputs, *maps, "-af", "apad", "-shortest",
    "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
    "-movflags", "+faststart", spec["out"])
print(f"wrote {spec['out']}: {total:.1f}s")
