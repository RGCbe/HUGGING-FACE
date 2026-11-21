"""Illustrations for a video's scenes, from an open text-to-image model whose licence allows commercial use.

    python3 imagegen.py IMAGES_JSON OUT_DIR [--only s1,s3] [--engine own|cloudflare|auto|qwen|qwen-fast]

IMAGES_JSON: {"style": "...", "aspect": "16:9", "style_ref": "s2",
              "images": [{"name": "s1", "prompt": "...", "seed": 7, "edit": "path/to/picture.png"?}]}
An image with "edit" is a correction of an existing picture (own, cloudflare and auto engines): that picture is sent as
image 0 and the prompt is used as written (no shared style), e.g. "The same photo, but the tea seller's left
hand holds ...". The model redraws the picture with the change, keeping the rest as close as it can.
An image may also list "also": ["path", ...]: more pictures sent after image 0 (image 1, image 2, ...), e.g. a face
file, so the prompt can say "... with exactly the face of the man in image 1" (own, cloudflare and auto).
Each image is generated from its prompt plus the shared style (so a video's pictures match) and
saved as OUT_DIR/NAME.png. Images that already exist are skipped, so a rerun only makes the
missing ones; delete a file (or use --only) to make it again, with a new seed if it had mistakes.

Engines:
  own         the same FLUX.2 [klein] 4B on the owner's own private ZeroGPU Space Rggroups/pictures (Hugging Face
              PRO: 40 GPU minutes a day, a picture uses about 5-15 seconds). Needs HF_TOKEN. The Space sleeps when
              unused; the first picture wakes it (a few minutes).
  auto        own, and Cloudflare for the rest if the own Space's GPU time is used up (or it is down).
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

OWN_SPACE, OWN_URL = "Rggroups/pictures", "https://rggroups-pictures.hf.space"
SPACES = {"qwen": "https://mcp-tools-qwen-image.hf.space", "qwen-fast": "https://mcp-tools-qwen-image-fast.hf.space"}
NEGATIVE = "text, letters, words, numbers, watermark, signature, logo, blurry, low resolution, photo, 3d render"
CF_MODEL = "@cf/black-forest-labs/flux-2-klein-4b"
SIZES = {"16:9": (1664, 928), "9:16": (928, 1664), "1:1": (1328, 1328)}

ap = argparse.ArgumentParser()
ap.add_argument("spec")
ap.add_argument("out_dir")
ap.add_argument("--only")
ap.add_argument("--engine", default="cloudflare", choices=["own", "auto", "cloudflare", "qwen", "qwen-fast"])
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


def multipart(fields, filename=None):
    boundary = uuid.uuid4().hex
    body = b""
    for name, value in fields.items():
        if isinstance(value, bytes):
            head = (f'Content-Disposition: form-data; name="{name}"; filename="{filename or name + ".png"}"\r\n'
                    'Content-Type: image/png')
        else:
            head, value = f'Content-Disposition: form-data; name="{name}"', str(value).encode()
        body += f"--{boundary}\r\n{head}\r\n\r\n".encode() + value + b"\r\n"
    return body + f"--{boundary}--\r\n".encode(), f"multipart/form-data; boundary={boundary}"


def cloudflare(prompt, seed, refs):
    w, h = SIZES[aspect]
    fields = {"prompt": prompt, "width": w, "height": h, "seed": seed}
    for i, ref in enumerate(r for r in refs if r):  # image 0, image 1, ... in the order given
        fields[f"input_image_{i}"] = ref
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


def hf_headers(extra=None):
    return dict({"Authorization": "Bearer " + os.environ["HF_TOKEN"]}, **(extra or {}))


def own_awake():
    # the owner's own Space: refuse it if it is not private; wake it if it sleeps, and wait until it runs
    info_url = f"https://huggingface.co/api/spaces/{OWN_SPACE}"
    for i in range(40):
        info = json.load(urllib.request.urlopen(urllib.request.Request(info_url, headers=hf_headers()), timeout=60))
        if not info.get("private"):
            sys.exit(f"{OWN_SPACE} is not private: not using it")
        stage = (info.get("runtime") or {}).get("stage")
        if stage == "RUNNING":
            return
        if stage in ("BUILD_ERROR", "RUNTIME_ERROR", "CONFIG_ERROR"):
            raise RuntimeError(f"{OWN_SPACE} is {stage}")
        if i == 0:
            print(f"{OWN_SPACE} is {stage}: waking it", flush=True)
            if stage in ("SLEEPING", "PAUSED", "STOPPED"):
                req = urllib.request.Request(info_url + "/restart", data=b"", method="POST", headers=hf_headers())
                urllib.request.urlopen(req, timeout=60)
        time.sleep(30)
    raise RuntimeError(f"{OWN_SPACE} did not start in 20 minutes")


def own_upload(data, tag):
    body, ctype = multipart({"files": data}, filename=tag + ".png")
    req = urllib.request.Request(OWN_URL + "/gradio_api/upload", data=body, method="POST",
                                 headers=hf_headers({"Content-Type": ctype}))
    path = json.load(urllib.request.urlopen(req, timeout=120))[0]
    return {"path": path, "meta": {"_type": "gradio.FileData"}}


def own(prompt, seed, refs):
    w, h = SIZES[aspect]
    files = [own_upload(r, f"ref{i}") for i, r in enumerate(r for r in refs if r)]
    data = [prompt, w, h, seed] + (files + [None, None, None])[:3]
    url = OWN_URL + "/gradio_api/call/generate"
    req = urllib.request.Request(url, data=json.dumps({"data": data}).encode(), method="POST",
                                 headers=hf_headers({"Content-Type": "application/json"}))
    event = json.load(urllib.request.urlopen(req, timeout=60))["event_id"]
    with urllib.request.urlopen(urllib.request.Request(f"{url}/{event}", headers=hf_headers()), timeout=600) as r:
        stream = r.read().decode()
    kind, payload = None, None
    for line in stream.splitlines():
        if line.startswith("event:"):
            kind = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            payload = line.split(":", 1)[1].strip()
    if kind != "complete":
        text = (payload or "").lower()
        if "quota" in text or "gpu time" in text:
            raise QuotaUsedUp(payload)
        raise RuntimeError(f"{OWN_SPACE} answered {kind}: {payload}")
    with urllib.request.urlopen(urllib.request.Request(json.loads(payload)[0]["url"], headers=hf_headers()),
                                timeout=120) as r:
        return r.read()


def small_copy(src, tag, limit):
    # Cloudflare takes references under 512x512; the own Space takes up to about 1 megapixel
    small = os.path.join(a.out_dir, f".{tag}_ref.png")
    ffmpeg("-i", src, "-vf", f"scale='min({limit},iw)':'min({limit},ih)':force_original_aspect_ratio=decrease", small)
    data = open(small, "rb").read()
    os.remove(small)
    return data


def references(paths, tag, eng):
    limit = 1024 if eng == "own" else 504
    return [small_copy(p, f"{tag}_{i}", limit) if p else None for i, p in enumerate(paths)]


FLUX = ("own", "auto", "cloudflare")
engine = a.engine
if engine in ("own", "auto"):
    try:
        own_awake()
        engine = "own"
    except (urllib.error.URLError, RuntimeError, OSError) as e:
        if a.engine == "own":
            sys.exit(f"the own picture Space is not available: {e}")
        print(f"the own picture Space is not available ({e}): using Cloudflare", file=sys.stderr)
        engine = "cloudflare"
style_src = os.path.join(a.out_dir, f"{spec['style_ref']}.png") if spec.get("style_ref") else None
if a.engine not in FLUX or not (style_src and os.path.exists(style_src)):
    style_src = None
failed = []
for im in spec["images"]:
    out = os.path.join(a.out_dir, im["name"] + ".png")
    if (only and im["name"] not in only) or (not only and os.path.exists(out)):
        continue
    prompt = f"{im['prompt']} {spec.get('style', '')}".strip()
    first = style_src
    if im.get("edit"):
        prompt, first = im["prompt"], im["edit"]
    elif style_src and im["name"] != spec.get("style_ref"):
        prompt = ("Draw in exactly the same art style as image 0: the same black ink outlines, flat colours, "
                  "warm cream paper background and soft shadows. " + prompt)
    elif style_src:
        first = None
    # extra pictures sent after image 0 (FLUX engines), e.g. a face file: "... the face of the man in image 1"
    ref_paths = [first] + list(im.get("also", []))
    data, attempt, seed = None, 0, im.get("seed", 7)
    while attempt < 3:
        try:
            started = time.time()
            # the safety filter sometimes flags a harmless picture; another seed usually passes
            seed = im.get("seed", 7) + 1000 * attempt
            if engine == "own":
                data = own(prompt, seed, references(ref_paths, im["name"], "own"))
            elif engine == "cloudflare":
                data = cloudflare(prompt, seed, references(ref_paths, im["name"], "cloudflare"))
            else:
                data = qwen(prompt, seed)
            break
        except QuotaUsedUp as e:
            if a.engine == "auto" and engine == "own":
                print(f"{im['name']}: the own Space's GPU time is used up: Cloudflare for the rest", file=sys.stderr)
                engine = "cloudflare"
                continue  # the same picture again, same seed, on Cloudflare
            sys.exit(f"{im['name']}: the daily picture allowance is used up ({str(e)[:200]}); run again after it resets")
        except (urllib.error.URLError, RuntimeError, OSError) as e:
            print(f"{im['name']}: try {attempt + 1} failed: {e}", file=sys.stderr)
            attempt += 1
            if a.engine == "auto" and engine == "own" and attempt == 2:
                print(f"{im['name']}: the own Space failed twice: Cloudflare for the rest", file=sys.stderr)
                engine, attempt = "cloudflare", 0
            elif attempt < 3:
                time.sleep(20 * attempt)
    if data is None:
        failed.append(im["name"])  # carry on with the others; reword this one's prompt and run again
        continue
    raw = out + ".download"
    open(raw, "wb").write(data)
    ffmpeg("-i", raw, out)
    os.remove(raw)
    print(f"{im['name']}: {out} ({time.time() - started:.0f}s, {engine}, seed {seed})", flush=True)
if failed:
    sys.exit(f"could not make {', '.join(failed)} (flagged by the safety filter, or the service failed): "
             "reword those prompts and run again")
