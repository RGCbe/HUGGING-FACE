"""Runs on the rented GPU: turns each keyframe in the drop box's job.json into a short video clip with Wan 2.2
TI2V-5B (Apache-2.0, image-to-video) and uploads it as out/NAME.mp4, with progress in out/status.txt.

job.json: {"model": "Wan-AI/Wan2.2-TI2V-5B-Diffusers", "width": 1280, "height": 704, "fps": 24, "steps": 30,
           "guidance": 5.0, "negative": "...",
           "clips": [{"name": "S09_a", "image": "keyframes/S09.jpg", "prompt": "...", "frames": 81, "seed": 1}]}
DROP_URL is this run's folder in the drop box (DROP_URL/NAME).
"""
import io
import json
import os
import threading
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
    urllib.request.urlopen(req, timeout=600).read()


def note(msg):
    print(msg, flush=True)
    lines.append(f"{time.strftime('%H:%M:%S')} {msg}")
    try:
        put("out/status.txt", "\n".join(lines[-300:]).encode())
    except Exception as e:  # noqa: BLE001
        print("status upload failed:", e, flush=True)


def fit(img, w, h):
    """Scale and centre-crop the keyframe to the clip size (the keyframes are 1664x928, about 16:9)."""
    from PIL import Image
    s = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x, y = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


try:
    import torch
    from PIL import Image
    job = json.loads(get("job.json"))
    vram = torch.cuda.get_device_properties(0).total_memory / 1e9
    note(f"gpu {torch.cuda.get_device_name(0)} {vram:.1f} GB, torch {torch.__version__}, {len(job['clips'])} clips to make")
    from huggingface_hub import snapshot_download
    t = time.time()
    local = os.path.join("/workspace/models", job["model"].split("/")[-1])
    downloading = True

    def report():
        while downloading:
            time.sleep(60)
            size = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(local) for f in fs if os.path.isfile(os.path.join(r, f)))
            if downloading:
                note(f"downloading the video model: {size / 1e9:.1f} of about 31 GB, {time.time() - t:.0f} s")

    threading.Thread(target=report, daemon=True).start()
    path = snapshot_download(job["model"], local_dir=local)
    downloading = False
    note(f"model ready in {time.time() - t:.0f} s")
    import diffusers
    from diffusers import AutoencoderKLWan, WanImageToVideoPipeline
    from diffusers.utils import export_to_video
    vae = AutoencoderKLWan.from_pretrained(path, subfolder="vae", torch_dtype=torch.float32)
    pipe = WanImageToVideoPipeline.from_pretrained(path, vae=vae, torch_dtype=torch.bfloat16)
    pipe.enable_model_cpu_offload()  # 5B transformer + 11 GB text encoder do not fit in 24 GB together
    note(f"diffusers {diffusers.__version__}: pipeline loaded")
    done = 0
    for c in job["clips"]:
        t = time.time()
        try:
            img = fit(Image.open(io.BytesIO(get(c["image"]))).convert("RGB"), job["width"], job["height"])
            frames = pipe(image=img, prompt=c["prompt"], negative_prompt=job.get("negative", ""), height=job["height"],
                          width=job["width"], num_frames=c.get("frames", 81), guidance_scale=job.get("guidance", 5.0),
                          num_inference_steps=job.get("steps", 30),
                          generator=torch.Generator("cuda").manual_seed(c.get("seed", 1))).frames[0]
            out = f"/root/{c['name']}.mp4"
            export_to_video(frames, out, fps=job.get("fps", 24))
            put(f"out/{c['name']}.mp4", open(out, "rb").read(), "video/mp4")
            done += 1
            note(f"{c['name']} made in {time.time() - t:.0f} s ({done}/{len(job['clips'])})")
        except Exception as e:  # noqa: BLE001
            note(f"{c['name']} FAILED: {type(e).__name__}: {str(e)[:500]}")
            if done == 0:
                raise
    note(f"ALL DONE: {done} of {len(job['clips'])} clips")
except Exception:  # noqa: BLE001
    note("STOPPED WITH AN ERROR:\n" + traceback.format_exc()[-2500:])
