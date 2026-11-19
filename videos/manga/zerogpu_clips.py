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
import subprocess
import sys
import time
import urllib.request
import uuid

SPACE_URL = "https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space"


def _req(url, data=None, ctype=None, timeout=120):
    headers = {"User-Agent": "zerogpu-clips/1.0"}
    # Only a read-only token ever goes to the Space: it belongs to another account and its code sees the header.
    # check_token() has made sure HF_READ_TOKEN is a "read" token before any call; HF_TOKEN (it can write) is never sent.
    token = (os.environ.get("HF_READ_TOKEN") or "").strip()
    if token:
        # The account's (PRO) GPU time is only used when the token comes in X-HF-Authorization, as the official
        # gradio_client sends it to *.hf.space; with a plain Authorization header the call counted as anonymous.
        headers["X-HF-Authorization"] = "Bearer " + token
    if ctype:
        headers["Content-Type"] = ctype
    return urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=timeout)


def check_token():
    """Stop unless HF_READ_TOKEN exists and Hugging Face says its role is "read" (no write access of any kind)."""
    token = (os.environ.get("HF_READ_TOKEN") or "").strip()
    if not token:
        sys.exit("HF_READ_TOKEN is not set: make a Read-Only token on huggingface.co/settings/tokens and save it")
    req = urllib.request.Request("https://huggingface.co/api/whoami-v2",
                                 headers={"Authorization": "Bearer " + token, "User-Agent": "zerogpu-clips/1.0"})
    me = json.load(urllib.request.urlopen(req, timeout=30))
    role = (me.get("auth", {}).get("accessToken") or {}).get("role")
    if role != "read":
        sys.exit(f"HF_READ_TOKEN has role '{role}', not 'read': it is not sent to another account's Space. "
                 "Make a token with the Read-Only option and save it as HF_READ_TOKEN.")
    print(f"token ok: read-only, account {me.get('name')}, PRO {me.get('isPro')}", flush=True)


def space_video(image_path, prompt, steps, negative, seconds, seed):
    """One clip through the Space's own web API (upload, call, read the event stream, download).
    The gradio_client library stopped working with this Space (every job came back cancelled), the plain API works."""
    boundary = uuid.uuid4().hex
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"files\"; filename=\"{os.path.basename(image_path)}\"\r\n"
            f"Content-Type: image/jpeg\r\n\r\n").encode() + open(image_path, "rb").read() + f"\r\n--{boundary}--\r\n".encode()
    path = json.load(_req(f"{SPACE_URL}/gradio_api/upload", body, f"multipart/form-data; boundary={boundary}"))[0]
    call = {"data": [{"path": path, "meta": {"_type": "gradio.FileData"}}, prompt, steps, negative, seconds, 1, 1, seed, False]}
    event_id = json.load(_req(f"{SPACE_URL}/gradio_api/call/generate_video", json.dumps(call).encode(),
                              "application/json"))["event_id"]
    event = None
    with _req(f"{SPACE_URL}/gradio_api/call/generate_video/{event_id}", timeout=900) as stream:
        for raw in stream:
            line = raw.decode("utf-8", "replace").strip()
            if line.startswith("event:"):
                event = line[6:].strip()
            elif line.startswith("data:") and event in ("complete", "error"):
                data = line[5:].strip()
                if event == "error":
                    raise RuntimeError(f"the Space said: {data[:400]}")
                out = json.loads(data)[0]
                out = out.get("video", out) if isinstance(out, dict) else out
                return _req(out["url"], timeout=300).read()
    raise RuntimeError("the Space closed the stream without a video")

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
    check_token()
    log = open(os.path.join(a.out_dir, "zerogpu_log.jsonl"), "a")
    made = fails = 0
    for name, s, seed in todo:
        if fails >= 2:  # once the free time is gone the Space often hides the reason: stop rather than queue for nothing
            print(f"two failures in a row: stopping after {made} clips (most likely the free GPU time is used up)")
            return
        t = time.time()
        rec = {"name": name, "space": SPACE, "seed": seed, "steps": a.steps, "prompt": s["prompt"]}
        try:
            data = space_video(os.path.join(a.keyframes_dir, s["image"]), s["prompt"], a.steps, NEGATIVE,
                               min(MAX_S, float(s["seconds"])), seed)
            raw = os.path.join(raw_dir, name + ".mp4")
            open(raw, "wb").write(data)
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
