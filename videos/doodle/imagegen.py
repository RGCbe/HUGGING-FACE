"""Illustrations for a video's scenes, from an open text-to-image model whose licence allows commercial use.

    python3 imagegen.py IMAGES_JSON OUT_DIR [--only s1,s3] [--engine cloudflare|qwen|qwen-fast]

IMAGES_JSON: {"style": "...", "aspect": "16:9", "style_ref": "s2",
              "images": [{"name": "s1", "prompt": "...", "seed": 7}]}
Each image is generated from its prompt plus the shared style (so a video's pictures match) and
saved as OUT_DIR/NAME.png. Images that already exist are skipped, so a rerun only makes the
missing ones; delete a file (or use --only) to make it again, with a new seed if it had mistakes.

Engines:
  cloudflare  FLUX.2 [klein] 4B (Apache-2.0) on Cloudflare Workers AI: 1664x928, about 60 pictures a
              day on the free plan (10,000 neurons, reset at 00:00 UTC). Needs CF_ACCOUNT_ID and
              CF_API_TOKEN (a "Workers AI" API token). If "style_ref" names a picture that already
              exists in OUT_DIR, a small copy of it is sent as a reference, so new pictures copy its style.
  qwen        Qwen-Image (Apache-2.0) on a Hugging Face ZeroGPU Space, 1664x928. Needs HF_TOKEN; the
              free daily GPU quota covers only a few pictures.
  qwen-fast   the 8-step Qwen-Image-Lightning Space, 1152x640, same quota.

Standard library only, plus ffmpeg to convert and resize images.
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid

SPACES = {"qwen": "https://mcp-tools-qwen-image.hf.space", "qwen-fast": "https://mcp-tools-qwen-image-fast.hf.space"}
NEGATIVE = "text, letters, words, numbers, watermark, signature, logo, blurry, low resolution, photo, 3d render"
CF_MODEL = "@cf/black-forest-labs/flux-2-klein-4b"
SIZES = {"16:9": (1664, 928), "9:16": (928, 1664), "1:1": (1328, 1328)}

ap = argparse.ArgumentParser()
ap.add_argument("spec")
ap.add_argument("out_dir")
ap.add_argument("--only")
ap.add_argument("--engine", default="cloudflare", choices=["cloudflare", "qwen", "qwen-fast"])
a = ap.parse_args()

spec = json.load(open(a.spec))
os.makedirs(a.out_dir, exist_ok=True)
only = set(a.only.split(",")) if a.only else None
aspect = spec.get("aspect", "16:9")


class QuotaUsedUp(Exception):
    pass


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *args], check=True)


def qwen(prompt, seed):
    # Gradio's two-step REST API: start a job, then read its event stream until it completes.
    headers = {"Authorization": "Bearer " + os.environ["HF_TOKEN"], "Content-Type": "application/json"}
    fast = a.engine == "qwen-fast"
    data = [prompt, seed, False, aspect] + ([1, 8] if fast else [NEGATIVE, 4.0, 16])
    url = SPACES[a.engine] + "/gradio_api/call/generate_image"
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
        if "quota" in (payload or "").lower():
            raise QuotaUsedUp(payload)
        raise RuntimeError(f"the Space answered {kind}: {payload}")
    with urllib.request.urlopen(urllib.request.Request(json.loads(payload)[0]["url"], headers=headers), timeout=120) as r:
        return r.read()


def multipart(fields):
    boundary = uuid.uuid4().hex
    body = b""
    for name, value in fields.items():
        if isinstance(value, bytes):
            head = f'Content-Disposition: form-data; name="{name}"; filename="{name}.png"\r\nContent-Type: image/png'
        else:
            head, value = f'Content-Disposition: form-data; name="{name}"', str(value).encode()
        body += f"--{boundary}\r\n{head}\r\n\r\n".encode() + value + b"\r\n"
    return body + f"--{boundary}--\r\n".encode(), f"multipart/form-data; boundary={boundary}"


def cloudflare(prompt, seed, ref):
    w, h = SIZES[aspect]
    fields = {"prompt": prompt, "width": w, "height": h, "seed": seed}
    if ref:
        fields["input_image_0"] = ref
    url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CF_ACCOUNT_ID']}/ai/run/{CF_MODEL}"
    for _ in range(2):
        body, ctype = multipart(fields)
        req = urllib.request.Request(url, data=body, method="POST",
                                     headers={"Authorization": "Bearer " + os.environ["CF_API_TOKEN"], "Content-Type": ctype})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return base64.b64decode(json.load(r)["result"]["image"])
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")
            if "seed" in detail and "seed" in fields:  # this model version may not take a seed
                del fields["seed"]
                continue
            if e.code == 429 or "neurons" in detail.lower():
                raise QuotaUsedUp(detail)
            raise RuntimeError(f"Workers AI answered {e.code}: {detail[:300]}")
    raise RuntimeError("Workers AI refused the request")


def style_reference():
    # the reference must be smaller than 512x512
    name = spec.get("style_ref")
    src = os.path.join(a.out_dir, f"{name}.png") if name else None
    if a.engine != "cloudflare" or not src or not os.path.exists(src):
        return None
    small = os.path.join(a.out_dir, f".{name}_ref.png")
    ffmpeg("-i", src, "-vf", "scale='min(504,iw)':'min(504,ih)':force_original_aspect_ratio=decrease", small)
    data = open(small, "rb").read()
    os.remove(small)
    return data


ref = style_reference()
for im in spec["images"]:
    out = os.path.join(a.out_dir, im["name"] + ".png")
    if (only and im["name"] not in only) or (not only and os.path.exists(out)):
        continue
    prompt = f"{im['prompt']} {spec.get('style', '')}".strip()
    if ref is not None and im["name"] != spec.get("style_ref"):
        prompt = ("Draw in exactly the same art style as image 0: the same black ink outlines, flat colours, "
                  "warm cream paper background and soft shadows. " + prompt)
    for attempt in range(3):
        try:
            started = time.time()
            data = cloudflare(prompt, im.get("seed", 7), ref) if a.engine == "cloudflare" else qwen(prompt, im.get("seed", 7))
            break
        except QuotaUsedUp as e:
            sys.exit(f"{im['name']}: the free daily quota is used up ({str(e)[:200]}); run again after it resets")
        except (urllib.error.URLError, RuntimeError, OSError) as e:
            print(f"{im['name']}: try {attempt + 1} failed: {e}", file=sys.stderr)
            if attempt == 2:
                sys.exit(f"could not make {im['name']}")
            time.sleep(20 * (attempt + 1))
    raw = out + ".download"
    open(raw, "wb").write(data)
    ffmpeg("-i", raw, out)
    os.remove(raw)
    print(f"{im['name']}: {out} ({time.time() - started:.0f}s, {a.engine})")
