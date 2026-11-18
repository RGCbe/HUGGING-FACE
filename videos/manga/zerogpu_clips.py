"""Free AI video clips: each approved start picture + its prompt goes to the public Wan 2.2 image-to-video Space run by
Hugging Face's own ZeroGPU team (zerogpu-aoti/wan2-2-fp8da-aoti-faster, Apache-2.0 model, commercial use allowed). It
runs on Hugging Face's free GPU time, which is counted against the HF account in HF_TOKEN (a few minutes a day on a
free account; it resets about 24 hours after the first use). When that time is used up the script stops and says so;
run it again the next day and it carries on where it stopped (clips that exist are kept).

    python3 zerogpu_clips.py FLOW_SHOTS.json KEYFRAMES_DIR OUT_DIR [--only S09,S31] [--takes 1] [--steps 6]

The Space makes at most 5 s at 832x480, 16 fps. The raw clip is kept in OUT_DIR/../clips_raw/; OUT_DIR/SNN_a.mp4 is
the same clip at 24 fps (motion-interpolated) and stretched to the shot's length, which is where edit.py looks.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

SPACE = "zerogpu-aoti/wan2-2-fp8da-aoti-faster"
MAX_S = 5.0
NEGATIVE = ("cartoon, anime, illustration, 3d render, blurry, low quality, deformed face, changing face, extra fingers, "
            "extra people, text, subtitles, watermark, static picture")


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)


def finish(raw, out, seconds):
    """24 fps with smooth in-between frames, stretched to the shot length, no sound."""
    d = duration(raw)
    stretch = max(1.0, seconds / d) if d else 1.0
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", raw, "-an",
                    "-vf", f"setpts={stretch:.4f}*PTS,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:vsbmc=1",
                    "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", out], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shots")
    ap.add_argument("keyframes_dir")
    ap.add_argument("out_dir")
    ap.add_argument("--only")
    ap.add_argument("--takes", type=int)
    ap.add_argument("--steps", type=int, default=6)
    a = ap.parse_args()
    from gradio_client import Client, handle_file
    only = set(a.only.split(",")) if a.only else None
    raw_dir = os.path.join(os.path.dirname(os.path.abspath(a.out_dir)), "clips_raw")
    os.makedirs(a.out_dir, exist_ok=True)
    os.makedirs(raw_dir, exist_ok=True)
    todo = []
    for s in json.load(open(a.shots)):
        if only and s["id"] not in only:
            continue
        for k in range(a.takes or s.get("takes", 1)):
            name = f"{s['id']}_{'abc'[k]}"
            if not os.path.exists(os.path.join(a.out_dir, name + ".mp4")):
                todo.append((name, s, 7 + 1000 * k))
    print(f"{len(todo)} clips to make", flush=True)
    if not todo:
        return
    client = Client(SPACE, token=os.environ.get("HF_TOKEN"), verbose=False)
    log = open(os.path.join(a.out_dir, "zerogpu_log.jsonl"), "a")
    made = fails = 0
    for name, s, seed in todo:
        if fails >= 2:  # once the free time is gone the Space often hides the reason: stop rather than queue for nothing
            print(f"two failures in a row: stopping after {made} clips (most likely the free GPU time is used up)")
            return
        t = time.time()
        rec = {"name": name, "space": SPACE, "seed": seed, "steps": a.steps, "prompt": s["prompt"]}
        try:
            vid, _ = client.predict(handle_file(os.path.join(a.keyframes_dir, s["image"])), s["prompt"], a.steps,
                                    NEGATIVE, min(MAX_S, float(s["seconds"])), 1, 1, seed, False,
                                    api_name="/generate_video")
            raw = os.path.join(raw_dir, name + ".mp4")
            shutil.copy(vid["video"] if isinstance(vid, dict) else vid, raw)
            finish(raw, os.path.join(a.out_dir, name + ".mp4"), s["seconds"] + 0.5)
            made += 1
            fails = 0
            rec.update(ok=True, took_s=round(time.time() - t))
            print(f"{name}: made in {time.time() - t:.0f} s", flush=True)
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            rec.update(ok=False, error=msg[:500])
            log.write(json.dumps(rec) + "\n")
            log.flush()
            if "quota" in msg.lower() or "exceeded" in msg.lower():
                print(f"free GPU time used up for today after {made} clips ({msg[:200]}). Run again tomorrow.")
                return
            print(f"{name}: FAILED - {msg[:300]}", flush=True)
            fails += 1
            continue
        log.write(json.dumps(rec) + "\n")
        log.flush()
    print(f"done: {made} of {len(todo)} clips made")


if __name__ == "__main__":
    sys.exit(main())
