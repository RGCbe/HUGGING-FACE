"""Runs on the rented GPU: makes every picture in the drop box's job.json with FLUX.2 [klein] 4B (Apache-2.0) and
uploads each one to the drop box as out/NAME.jpg, with progress in out/status.txt. DROP_URL is this run's
folder in the drop box (DROP_URL/NAME).

job.json: {"model": "black-forest-labs/FLUX.2-klein-4B", "width": 1664, "height": 928, "steps": 4,
           "cast": ["arjun", ...],                       face files in the drop box as cast/NAME.jpg
           "images": [{"name": "S05_a", "prompt": "...", "seed": 1, "refs": ["arjun"]}]}
"refs" are given to the model as reference pictures (image 0, image 1, ... in the prompt's words).
"""
import inspect
import io
import json
import os
import time
import traceback
import urllib.request

D = os.environ["DROP_URL"].rstrip("/")
UA = {"User-Agent": "gs-machine/1.0"}
lines = []


def get(name):
    return urllib.request.urlopen(urllib.request.Request(f"{D}/{name}", headers=UA), timeout=300).read()


def put(name, data, ctype="application/octet-stream"):
    req = urllib.request.Request(f"{D}/{name}", data=data, method="PUT", headers={"Content-Type": ctype, **UA})
    urllib.request.urlopen(req, timeout=300).read()


def note(msg):
    print(msg, flush=True)
    lines.append(f"{time.strftime('%H:%M:%S')} {msg}")
    try:
        put("out/status.txt", "\n".join(lines[-300:]).encode())
    except Exception as e:  # noqa: BLE001
        print("status upload failed:", e, flush=True)


try:
    import torch
    from PIL import Image
    job = json.loads(get("job.json"))
    vram = torch.cuda.get_device_properties(0).total_memory / 1e9
    note(f"gpu {torch.cuda.get_device_name(0)} {vram:.1f} GB, torch {torch.__version__}, {len(job['images'])} pictures to make")
    import threading
    from huggingface_hub import snapshot_download
    t = time.time()
    downloading = True

    def report():  # the download takes many minutes: say how far it got every minute, so the watcher sees progress
        cache = "/workspace/models"
        while downloading:
            time.sleep(60)
            size = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(cache) for f in fs
                       if os.path.isfile(os.path.join(r, f)))
            if downloading:
                note(f"downloading the model: {size / 1e9:.1f} of about 16 GB, {time.time() - t:.0f} s")

    threading.Thread(target=report, daemon=True).start()
    # the model lives in /workspace/models/, which GridShare keeps when the machine is stopped with "keep my large
    # files" on, and restores (public models: re-downloads itself) before billing starts on the next machine
    local = os.path.join("/workspace/models", job["model"].split("/")[-1])
    have = os.path.exists(os.path.join(local, "transformer", "diffusion_pytorch_model.safetensors"))
    note("model found in /workspace/models (restored)" if have else "model not saved yet: downloading it into /workspace/models")
    path = snapshot_download(job["model"], local_dir=local,
                             allow_patterns=["model_index.json", "scheduler/*", "text_encoder/*", "tokenizer/*", "transformer/*", "vae/*"])
    downloading = False
    note(f"model ready in {time.time() - t:.0f} s")
    import diffusers
    from diffusers import Flux2KleinPipeline
    pipe = Flux2KleinPipeline.from_pretrained(path, torch_dtype=torch.bfloat16)
    if vram < 23:
        pipe.enable_model_cpu_offload()
    else:
        pipe.to("cuda")
    params = list(inspect.signature(pipe.__call__).parameters)
    note(f"diffusers {diffusers.__version__}; pipeline takes: {', '.join(params)}")
    refs = {c: Image.open(io.BytesIO(get(f"cast/{c}.jpg"))).convert("RGB") for c in job.get("cast", [])}
    done = 0
    for it in job["images"]:
        t = time.time()
        try:
            kw = dict(prompt=it["prompt"], width=job["width"], height=job["height"], guidance_scale=1.0,
                      num_inference_steps=job.get("steps", 4), generator=torch.Generator("cuda").manual_seed(it["seed"]))
            images = [refs[c] for c in it.get("refs", [])]
            if images:
                kw["image"] = images
            out = pipe(**kw).images[0]
            buf = io.BytesIO()
            out.save(buf, "JPEG", quality=94)
            put(f"out/{it['name']}.jpg", buf.getvalue(), "image/jpeg")
            done += 1
            note(f"{it['name']} made in {time.time() - t:.1f} s ({done}/{len(job['images'])})")
        except Exception as e:  # noqa: BLE001
            note(f"{it['name']} FAILED: {type(e).__name__}: {str(e)[:400]}")
            if done == 0 and "out of memory" not in str(e).lower():
                raise
    note(f"ALL DONE: {done} of {len(job['images'])} pictures")
except Exception:  # noqa: BLE001
    note("STOPPED WITH AN ERROR:\n" + traceback.format_exc()[-2500:])
