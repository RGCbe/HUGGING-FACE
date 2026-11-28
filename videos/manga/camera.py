"""Movie-style camera moves on still keyframes (free, made here with ffmpeg): slow push-in, pull-back, pans, tilts
and a small shake, at 1920x1080, 24 fps.

    python3 camera.py SHOTS.json KEYFRAMES_DIR OUT_DIR [--only S05,S07]

Every shot with "anim": "camera" gets OUT_DIR/SNN.mp4, as long as the shot plus half a second (cut room).
The move comes from MOVES below (zoom from -> to, the picture's centre from -> to as fractions, shake), chosen per
shot from its "motion" direction in the shot list; a shot not listed gets a slow push-in.
"""
import argparse
import json
import os
import subprocess

FPS = 24
# shot: (zoom from, zoom to, centre x from, centre x to, centre y from, centre y to, shake pixels)
MOVES = {
    "S05": (1.06, 1.12, 0.42, 0.58, 0.50, 0.50, 0),   # aerial glide along the bay
    "S06": (1.18, 1.02, 0.50, 0.50, 0.50, 0.50, 0),   # hunters walk toward us, the camera tracks back
    "S07": (1.20, 1.10, 0.55, 0.62, 0.30, 0.55, 0),   # floats down toward the tea stall
    "S10": (1.10, 1.12, 0.60, 0.42, 0.52, 0.52, 0),   # hunters walk past: pan left
    "S11": (1.02, 1.12, 0.50, 0.50, 0.45, 0.42, 0),
    "S12": (1.04, 1.22, 0.50, 0.62, 0.48, 0.40, 0),   # push in toward the licence card
    "S13": (1.02, 1.12, 0.50, 0.50, 0.50, 0.48, 0),
    "S16": (1.10, 1.12, 0.42, 0.58, 0.50, 0.50, 0),   # crowd laughing: pan right
    "S21": (1.02, 1.10, 0.50, 0.50, 0.50, 0.48, 0),
    "S24": (1.18, 1.32, 0.50, 0.50, 0.40, 0.36, 0),   # Arjun's close-up: cropped tighter, slow push
    "S25": (1.00, 1.12, 0.50, 0.50, 0.50, 0.46, 0),   # walking into the light
    "S27": (1.04, 1.16, 0.50, 0.50, 0.45, 0.40, 6),   # the ogre roars: push in with a shake
    "S29": (1.02, 1.12, 0.50, 0.52, 0.45, 0.40, 2),
    "S34": (1.00, 1.08, 0.50, 0.50, 0.45, 0.42, 0),
    "S35": (1.02, 1.12, 0.50, 0.50, 0.42, 0.38, 0),
    "S37": (1.00, 1.14, 0.50, 0.50, 0.50, 0.48, 2),   # running toward us
    "S39": (1.16, 1.06, 0.50, 0.50, 0.70, 0.42, 3),   # the minotaur rises: tilt up
    "S40": (1.02, 1.10, 0.40, 0.42, 0.42, 0.40, 0),
    "S44": (1.02, 1.10, 0.45, 0.45, 0.45, 0.40, 0),
    "S47": (1.14, 1.04, 0.50, 0.50, 0.48, 0.50, 0),   # the camera lowers over him
    "S48": (1.08, 1.12, 0.42, 0.52, 0.50, 0.50, 0),
    "S50": (1.04, 1.12, 0.50, 0.50, 0.42, 0.40, 0),   # "...Cardamom.": very slow push
    "S51": (1.02, 1.10, 0.50, 0.50, 0.42, 0.40, 0),
    "S52": (1.02, 1.10, 0.50, 0.50, 0.42, 0.40, 0),
    "S53": (1.16, 1.00, 0.52, 0.50, 0.52, 0.50, 0),   # pull back from the lonely stall
    "S54": (1.02, 1.12, 0.45, 0.48, 0.45, 0.42, 0),
    "S55": (1.18, 1.06, 0.45, 0.50, 0.75, 0.40, 0),   # rises from the stall up to the Gate
}
DEFAULT = (1.02, 1.10, 0.50, 0.50, 0.50, 0.47, 0)


def render(img, out, seconds, move):
    zs, ze, xs, xe, ys, ye, shake = move
    n = int(round(seconds * FPS))
    p = f"(on/{max(n - 1, 1)})"
    ease = f"(0.5-0.5*cos(PI*{p}))"  # smooth start and stop
    z = f"{zs}+({ze}-{zs})*{ease}"
    cx = f"({xs}+({xe}-{xs})*{ease})"
    cy = f"({ys}+({ye}-{ys})*{ease})"
    sx = f"+{shake}*2*sin(on*1.7)" if shake else ""
    sy = f"+{shake}*2*cos(on*2.3)" if shake else ""
    # crop to 16:9, enlarge 2x so the slow move is smooth (zoompan moves in whole pixels), then move
    vf = (f"crop='min(iw,ih*16/9)':'min(ih,iw*9/16)',scale=3840:2160:flags=lanczos,"
          f"zoompan=z='{z}':x='max(0,min(iw-iw/zoom,{cx}*iw-iw/zoom/2{sx}))':"
          f"y='max(0,min(ih-ih/zoom,{cy}*ih-ih/zoom/2{sy}))':d={n}:s=1920x1080:fps={FPS},format=yuv420p")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", img, "-vf", vf, "-frames:v", str(n),
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", out], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shots")
    ap.add_argument("keyframes_dir")
    ap.add_argument("out_dir")
    ap.add_argument("--only")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    only = set(a.only.split(",")) if a.only else None
    for s in json.load(open(a.shots))["shots"]:
        if s.get("anim") != "camera" or (only and s["id"] not in only):
            continue
        img = os.path.join(a.keyframes_dir, f"{s['id']}.jpg")
        if not os.path.exists(img):
            print(f"{s['id']}: no approved keyframe yet, skipped")
            continue
        out = os.path.join(a.out_dir, f"{s['id']}.mp4")
        render(img, out, s["seconds"] + 0.5, MOVES.get(s["id"], DEFAULT))
        print(f"{s['id']}: {s['seconds'] + 0.5:.1f} s {MOVES.get(s['id'], DEFAULT)[:2]}", flush=True)


if __name__ == "__main__":
    main()
