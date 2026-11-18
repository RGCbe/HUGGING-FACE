"""Make an episode's AI shots automatically with Google Veo 3.1 (the model inside Google Flow) through the Gemini API:
each approved start picture + its prompt goes in, a video clip comes back as OUT_DIR/SNN_a.mp4 (second take SNN_b.mp4),
which is where edit.py looks for clips.

    python3 veo_clips.py FLOW_SHOTS.json KEYFRAMES_DIR OUT_DIR [--model lite|fast|best] [--only S09,S31]
                         [--takes 1] [--max-usd 15] [--dry-run] [--models]

The Gemini API key is never in this file or in git: either GEMINI_API_KEY is set, or (in the cloud session) the network
proxy adds the saved key to every request to generativelanguage.googleapis.com. Veo is paid per second of video; the
script prints the cost first and refuses to start when it would pass --max-usd. A clip that exists is kept (delete it
to make it again). Every clip's prompt, model, length and outcome go to OUT_DIR/veo_log.jsonl.
"""
import argparse
import base64
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request

API = "https://generativelanguage.googleapis.com/v1beta"
# Gemini API price per second of video at 720p (Google's pricing page, Oct 2026); used for the cost guard only
MODELS = {"lite": ("veo-3.1-lite-generate-preview", 0.05),
          "fast": ("veo-3.1-fast-generate-preview", 0.10),
          "best": ("veo-3.1-generate-preview", 0.40)}
NEGATIVE = ("cartoon, anime, illustration, drawing, 3d render, blurry, low quality, deformed face, changing face, "
            "extra fingers, extra people, text, subtitles, watermark, logo")


def call(method, path, body=None, raw=False, timeout=120):
    headers = {"Content-Type": "application/json", "User-Agent": "veo-clips/1.0"}
    if os.environ.get("GEMINI_API_KEY"):
        headers["x-goog-api-key"] = os.environ["GEMINI_API_KEY"].strip()
    url = path if path.startswith("http") else f"{API}/{path}"
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None, method=method,
                                 headers=headers)
    for k in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                b = r.read()
                return b if raw else (json.loads(b) if b.strip() else {})
        except urllib.error.HTTPError as e:
            msg = e.read()[:600].decode("utf-8", "replace")
            if e.code in (429, 500, 502, 503) and k < 3:
                time.sleep(20 * (k + 1))
                continue
            raise RuntimeError(f"Gemini API {e.code}: {msg}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            if k < 3:
                time.sleep(10 * (k + 1))
                continue
            raise RuntimeError(f"network: {e}") from None


def video_uri(op):
    """The finished operation's video link, or why there is none (e.g. the safety filter)."""
    resp = op.get("response", {})
    gv = resp.get("generateVideoResponse", resp)
    for s in gv.get("generatedSamples", []) or gv.get("generatedVideos", []):
        v = s.get("video", {})
        if v.get("uri"):
            return v["uri"], None
    why = gv.get("raiMediaFilteredReasons") or op.get("error") or "no video in the answer"
    return None, json.dumps(why)[:400]


def make(clip, model, out_dir, log, lock):
    t = time.time()
    img = base64.b64encode(open(clip["image"], "rb").read()).decode()
    body = {"instances": [{"prompt": clip["prompt"], "image": {"bytesBase64Encoded": img, "mimeType": "image/jpeg"}}],
            "parameters": {"aspectRatio": "16:9", "durationSeconds": clip["seconds"], "resolution": "720p",
                           "personGeneration": "allow_adult", "negativePrompt": NEGATIVE}}
    rec = {"name": clip["name"], "model": model, "seconds": clip["seconds"], "prompt": clip["prompt"]}
    try:
        op = call("POST", f"models/{model}:predictLongRunning", body)
        while not op.get("done"):
            time.sleep(10)
            if time.time() - t > 15 * 60:
                raise RuntimeError("no answer after 15 minutes")
            op = call("GET", op["name"])
        uri, why = video_uri(op)
        if not uri:
            raise RuntimeError(f"refused or empty: {why}")
        if ":download" in uri and "alt=" not in uri:
            uri += ("&" if "?" in uri else "?") + "alt=media"
        data = call("GET", uri, raw=True, timeout=300)
        path = os.path.join(out_dir, clip["name"] + ".mp4")
        open(path + ".part", "wb").write(data)
        os.replace(path + ".part", path)
        rec.update(ok=True, bytes=len(data), took_s=round(time.time() - t))
        msg = f"{clip['name']}: made in {time.time() - t:.0f} s ({len(data) / 1e6:.1f} MB)"
    except Exception as e:  # noqa: BLE001 - one bad clip must not stop the others
        rec.update(ok=False, error=str(e)[:600], took_s=round(time.time() - t))
        msg = f"{clip['name']}: FAILED - {str(e)[:300]}"
    with lock:
        log.write(json.dumps(rec) + "\n")
        log.flush()
        print(msg, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shots", nargs="?")
    ap.add_argument("keyframes_dir", nargs="?")
    ap.add_argument("out_dir", nargs="?")
    ap.add_argument("--model", choices=MODELS, default="lite")
    ap.add_argument("--only")
    ap.add_argument("--takes", type=int, help="takes per shot (default: as the shot list says)")
    ap.add_argument("--max-usd", type=float, default=15)
    ap.add_argument("--parallel", type=int, default=3)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--models", action="store_true", help="list the Veo models this key can use, then stop")
    a = ap.parse_args()
    if a.models:
        for m in call("GET", "models?pageSize=200").get("models", []):
            if "veo" in m["name"]:
                print(m["name"], m.get("supportedGenerationMethods"))
        return
    model, rate = MODELS[a.model]
    only = set(a.only.split(",")) if a.only else None
    os.makedirs(a.out_dir, exist_ok=True)
    clips = []
    for s in json.load(open(a.shots)):
        if only and s["id"] not in only:
            continue
        for k in range(a.takes or s.get("takes", 1)):
            name = f"{s['id']}_{'abc'[k]}"
            if not os.path.exists(os.path.join(a.out_dir, name + ".mp4")):
                clips.append({"name": name, "image": os.path.join(a.keyframes_dir, s["image"]),
                              "seconds": s["seconds"] if s["seconds"] in (4, 6, 8) else 8, "prompt": s["prompt"]})
    secs = sum(c["seconds"] for c in clips)
    cost = secs * rate
    print(f"{len(clips)} clips, {secs} s of video with {model}: about ${cost:.2f} (limit ${a.max_usd:.2f})")
    for c in clips:
        if not os.path.exists(c["image"]):
            sys.exit(f"{c['name']}: start picture missing: {c['image']}")
    if a.dry_run or not clips:
        for c in clips:
            print(f"  {c['name']}  {c['seconds']} s  {c['prompt'][:80]}")
        return
    if cost > a.max_usd:
        sys.exit("over the money limit: raise --max-usd or make fewer clips (--only)")
    lock = threading.Lock()
    with open(os.path.join(a.out_dir, "veo_log.jsonl"), "a") as log:
        todo = list(clips)
        workers = []

        def worker():
            while True:
                with lock:
                    if not todo:
                        return
                    c = todo.pop(0)
                make(c, model, a.out_dir, log, lock)
        for _ in range(max(1, a.parallel)):
            th = threading.Thread(target=worker)
            th.start()
            workers.append(th)
        for th in workers:
            th.join()
    made = [c for c in clips if os.path.exists(os.path.join(a.out_dir, c["name"] + ".mp4"))]
    print(f"done: {len(made)} of {len(clips)} clips made")


if __name__ == "__main__":
    main()
