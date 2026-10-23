"""Illustrations for a video's scenes, from Qwen-Image (Apache-2.0) on a Hugging Face Space.

    python3 imagegen.py IMAGES_JSON OUT_DIR [--only s1,s3] [--fast]

IMAGES_JSON: {"style": "...", "aspect": "16:9", "images": [{"name": "s1", "prompt": "...", "seed": 7}]}
Each image is generated from its prompt plus the shared style (so a video's pictures match) and
saved as OUT_DIR/NAME.png. Images that already exist are skipped, so a rerun only makes the
missing ones; delete a file (or use --only) to make it again, with a new seed if it had mistakes.
--fast uses the 8-step Qwen-Image-Lightning Space (smaller, 1152x640) instead of the full model.

Uses HF_TOKEN (a read token is enough) so the Space runs on the account's own GPU quota. Standard
library only, plus ffmpeg to convert the Space's WebP output.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

SPACES = {False: "https://mcp-tools-qwen-image.hf.space", True: "https://mcp-tools-qwen-image-fast.hf.space"}
NEGATIVE = "text, letters, words, numbers, watermark, signature, logo, blurry, low resolution, photo, 3d render"

ap = argparse.ArgumentParser()
ap.add_argument("spec")
ap.add_argument("out_dir")
ap.add_argument("--only")
ap.add_argument("--fast", action="store_true")
a = ap.parse_args()

spec = json.load(open(a.spec))
os.makedirs(a.out_dir, exist_ok=True)
base = SPACES[a.fast]
headers = {"Authorization": "Bearer " + os.environ["HF_TOKEN"], "Content-Type": "application/json"}
only = set(a.only.split(",")) if a.only else None


def call(prompt, seed):
    # Gradio's two-step REST API: start a job, then read its event stream until it completes.
    data = [prompt, seed, False, spec.get("aspect", "16:9")]
    data += [1, 8] if a.fast else [NEGATIVE, 4.0, 16]
    url = base + "/gradio_api/call/generate_image"
    req = urllib.request.Request(url, data=json.dumps({"data": data}).encode(), headers=headers, method="POST")
    event = json.load(urllib.request.urlopen(req, timeout=60))["event_id"]
    with urllib.request.urlopen(urllib.request.Request(f"{url}/{event}", headers=headers), timeout=600) as r:
        stream = r.read().decode()
    kind, payload = None, None
    for line in stream.splitlines():
        if line.startswith("event:"):
            kind = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            payload = line.split(":", 1)[1].strip()
    if kind != "complete":
        raise RuntimeError(f"the Space answered {kind}: {payload}")
    return json.loads(payload)[0]["url"]


for im in spec["images"]:
    out = os.path.join(a.out_dir, im["name"] + ".png")
    if (only and im["name"] not in only) or (not only and os.path.exists(out)):
        continue
    prompt = f"{im['prompt']} {spec.get('style', '')}".strip()
    for attempt in range(3):
        try:
            started = time.time()
            url = call(prompt, im.get("seed", 7))
            break
        except (urllib.error.URLError, RuntimeError, OSError) as e:
            print(f"{im['name']}: try {attempt + 1} failed: {e}", file=sys.stderr)
            if attempt == 2:
                sys.exit(f"could not make {im['name']}; the Space may be busy or the GPU quota used up")
            time.sleep(20 * (attempt + 1))
    webp = out[:-4] + ".webp"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=120) as r:
        open(webp, "wb").write(r.read())
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", webp, out], check=True)
    os.remove(webp)
    print(f"{im['name']}: {out} ({time.time() - started:.0f}s)")
