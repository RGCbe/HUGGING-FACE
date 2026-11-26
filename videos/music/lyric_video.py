"""A lyric music video from a timed plan: each shot a picture moving in 3D (depthmove: the camera pushes in or slides,
near things moving more than far ones), cut on the song's lines, big Tamil captions, a credited real photo at the end.

    python3 lyric_video.py PLAN.json [--short]        # WORK/video.mp4 (16:9), or WORK/short.mp4 (9:16) with --short

PLAN.json (see vaibhav/video/plan.json): audio, pictures dir, work dir, size, fps, shots [{pic, start, end, move}],
optional clips dir (animated shots SNN_a.mp4 from manga/zerogpu_clips.py; a shot without one moves in 3D instead),
captions [{text, start, end}], optional photo {path, start, end, credit} and intro_note {text, start, end}.
Captions use Mukta Malar ExtraBold (OFL, videos/movies-explained/fonts). Nothing is sent anywhere: all local.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "doodle"))
FONTS = os.path.join(HERE, "..", "movies-explained", "fonts")


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *args], check=True)


def ass_time(t):
    h, rem = divmod(max(0.0, t), 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def captions_ass(plan, path, w, h, short):
    size = 92 if not short else 84
    margin_v = 90 if not short else 520
    lines = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {w}", f"PlayResY: {h}", "WrapStyle: 0", "",
             "[V4+ Styles]",
             "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
             "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
             "MarginR, MarginV, Encoding",
             f"Style: Lyric,Mukta Malar ExtraBold,{size},&H00FFFFFF,&H0000D7FF,&H00101010,&H96000000,0,0,0,0,100,100,0,0,1,6,3,2,60,60,{margin_v},1",
             f"Style: Note,Mukta Malar ExtraBold,{size // 2},&H00FFFFFF,&H00FFFFFF,&H00101010,&H96000000,0,0,0,0,100,100,0,0,1,3,2,8,60,60,60,1",
             f"Style: Credit,Mukta Malar ExtraBold,{size // 3},&H00FFFFFF,&H00FFFFFF,&H00101010,&H96000000,0,0,0,0,100,100,0,0,1,2,1,3,40,40,30,1",
             "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for c in plan["captions"]:
        text = c["text"]
        if short and len(text) > 22 and ", " in text:
            text = text.replace(", ", ",\\N", 1)
        # a quick pop in: a little bigger, then settling (on the beat of the line)
        anim = r"{\fad(120,160)\t(0,140,\fscx108\fscy108)\t(140,300,\fscx100\fscy100)}"
        lines.append(f"Dialogue: 0,{ass_time(c['start'])},{ass_time(c['end'])},Lyric,,0,0,0,,{anim}{text}")
    if plan.get("intro_note"):
        n = plan["intro_note"]
        lines.append(f"Dialogue: 0,{ass_time(n['start'])},{ass_time(n['end'])},Note,,0,0,0,,{{\\fad(300,400)}}{n['text']}")
    if plan.get("photo"):
        p = plan["photo"]
        lines.append(f"Dialogue: 0,{ass_time(p['start'])},{ass_time(p['end'])},Credit,,0,0,0,,{p['credit']}")
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--short", action="store_true", help="9:16 for Shorts / Reels")
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    import depthmove
    work = os.path.expanduser(plan["work"])
    pics = os.path.expanduser(plan["pictures"])
    os.makedirs(work, exist_ok=True)
    w, h = (1080, 1920) if a.short else tuple(plan["size"])
    fps = plan.get("fps", 30)
    tag = "short" if a.short else "video"
    clips = os.path.expanduser(plan["clips"]) if plan.get("clips") else None
    parts = []
    for i, s in enumerate(plan["shots"]):
        seconds = s["end"] - s["start"]
        clip = os.path.join(clips, f"S{i + 1:02d}_a.mp4") if clips else None
        animated = bool(clip and os.path.exists(clip))
        out = os.path.join(work, f"{tag}_{i:02d}_{s['pic']}{'_anim' if animated else ''}.mp4")
        if not os.path.exists(out):
            if animated:
                # the animated clip (Wan 2.1 on the owner's Space, 832x480): upscaled and cropped to the frame, at the
                # video's frame rate, cut or held to the shot's exact length so the cuts stay on the lines
                n = int(round(seconds * fps))
                ffmpeg("-i", clip, "-vf", f"fps={fps},scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,"
                       f"crop={w}:{h},unsharp=5:5:0.6,tpad=stop_mode=clone:stop_duration=3,format=yuv420p",
                       "-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", out)
            else:
                depthmove.shot(os.path.join(pics, s["pic"] + ".png"), out, seconds, s.get("move", 0),
                               size=(w, h), fps=fps, punch=i > 0)
        parts.append(out)
        print(f"shot {i + 1}/{len(plan['shots'])}: {s['pic']} {s['start']}-{s['end']}", flush=True)
    if plan.get("photo"):
        p = plan["photo"]
        out = os.path.join(work, f"{tag}_photo.mp4")
        if not os.path.exists(out):
            # the real photo, still and plain (a slow zoom, no depth warp): a photograph is shown as it is
            n = int(round((p["end"] - p["start"]) * fps))
            ffmpeg("-loop", "1", "-i", os.path.expanduser(p["path"]), "-vf",
                   f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=0x101018,"
                   f"zoompan=z='1+0.0006*on':d={n}:s={w}x{h}:fps={fps},format=yuv420p",
                   "-frames:v", str(n), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", out)
        parts.append(out)
    lst = os.path.join(work, f"{tag}_list.txt")
    open(lst, "w").write("".join(f"file '{x}'\n" for x in parts))
    silent = os.path.join(work, f"{tag}_silent.mp4")
    ffmpeg("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent)
    ass = os.path.join(work, f"{tag}.ass")
    captions_ass(plan, ass, w, h, a.short)
    final = os.path.join(work, f"{tag}.mp4")
    ffmpeg("-i", silent, "-i", os.path.expanduser(plan["audio"]), "-vf", f"ass={ass}:fontsdir={FONTS}",
           "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", final)
    print("video:", final)


if __name__ == "__main__":
    main()
