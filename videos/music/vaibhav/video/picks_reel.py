"""One silent review video of chosen SkyReels takes, each labelled with its shot and take, for the owner to watch on a
phone. Where a take is cut, the part after the cut turns grey under a red "CUT HERE" bar.

    python3 picks_reel.py OUT.mp4 TAKE:SHOT:LABEL[:KEEP_FRAMES] ...
    python3 picks_reel.py ~/picks.mp4 t01_s7:S01:"village walk" p02_s21:S05:"walk out":66

TAKE is a file in ~/.cache/music/vaibhav-video/skyreels (or a path to any clip). KEEP_FRAMES is how many frames of the
take are used (the clip check's cut_end, in frames at 24 fps). All local: ffmpeg only.
"""
import os, subprocess, sys, tempfile

SK = os.path.expanduser("~/.cache/music/vaibhav-video/skyreels")
FONTS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/Library/Fonts/Arial Bold.ttf",
         "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"]
FONT = next((f for f in FONTS if os.path.exists(f)), None)


def esc(s):
    return s.replace("\\", "/").replace(":", r"\:").replace("'", r"\'")


def font():
    return f"fontfile='{esc(FONT)}':" if FONT else ""


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    out, items = os.path.expanduser(sys.argv[1]), sys.argv[2:]
    tmp = tempfile.mkdtemp()
    segs = []
    for n, item in enumerate(items, 1):
        parts = item.split(":")
        take, shot, label = parts[0], parts[1], parts[2]
        keep = int(parts[3]) / 24 if len(parts) > 3 and parts[3] else None
        src = take if os.path.exists(take) else os.path.join(SK, f"{take}.mp4")
        name = os.path.splitext(os.path.basename(src))[0]
        f = ["scale=960:544:force_original_aspect_ratio=decrease", "pad=960:544:(ow-iw)/2:(oh-ih)/2", "fps=24",
             "drawbox=x=0:y=0:w=iw:h=44:color=black@0.65:t=fill",
             f"drawtext={font()}text='{n}/{len(items)}   {esc(shot)}  {esc(label)}  ({esc(name)})':x=14:y=11:"
             "fontsize=22:fontcolor=white"]
        if keep:
            f += [f"hue=s=0:enable='gte(t,{keep:.3f})'",
                  f"drawbox=x=0:y=ih/2-30:w=iw:h=60:color=0xC62828@0.85:t=fill:enable='gte(t,{keep:.3f})'",
                  f"drawtext={font()}text='CUT HERE - the grey part is not used':x=(w-tw)/2:y=h/2-14:fontsize=26:"
                  f"fontcolor=white:enable='gte(t,{keep:.3f})'"]
        f += ["tpad=stop_mode=clone:stop_duration=0.6"]
        seg = os.path.join(tmp, f"seg{n:02d}.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-an", "-vf", ",".join(f), "-c:v", "libx264",
                        "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", seg], check=True)
        segs.append(seg)
    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as fh:
        fh.writelines(f"file '{s}'\n" for s in segs)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                    "-movflags", "+faststart", out], check=True)
    print(out)


if __name__ == "__main__":
    main()
