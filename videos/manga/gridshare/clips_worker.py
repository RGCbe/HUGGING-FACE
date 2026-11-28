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
    import gc
    import diffusers
    from diffusers import AutoencoderKLWan, WanImageToVideoPipeline
    from diffusers.utils import export_to_video
    # Memory: these home PCs have only ~21 GB of RAM. Offloading kept the 11 GB text model AND the 10 GB video model in
    # RAM and the process was killed. So: encode every prompt first, free the text model completely, then keep the
    # video model and the VAE on the graphics card for the whole run.
    enc = WanImageToVideoPipeline.from_pretrained(path, transformer=None, vae=None, torch_dtype=torch.bfloat16)
    enc.text_encoder.to("cuda")
    embeds = {}
    with torch.no_grad():
        for c in job["clips"]:
            pe, ne = enc.encode_prompt(prompt=c["prompt"], negative_prompt=job.get("negative", ""),
                                       do_classifier_free_guidance=True, device="cuda")
            embeds[c["name"]] = (pe.to("cpu"), ne.to("cpu"))
    del enc
    gc.collect(); torch.cuda.empty_cache()
    note(f"{len(embeds)} prompts encoded; text model freed")
    vae = AutoencoderKLWan.from_pretrained(path, subfolder="vae", torch_dtype=torch.float32)
    pipe = WanImageToVideoPipeline.from_pretrained(path, vae=vae, text_encoder=None, tokenizer=None,
                                                   torch_dtype=torch.bfloat16).to("cuda")
    if hasattr(pipe.vae, "enable_tiling"):
        pipe.vae.enable_tiling()
    note(f"diffusers {diffusers.__version__}: video model on the GPU, {torch.cuda.memory_allocated() / 1e9:.1f} GB used")

    def step_note(p, i, t, kw):  # progress inside a clip, so a stall shows at once
        if i in (0, 9) or i == job.get("steps", 30) - 1:
            note(f"   step {i + 1}/{job.get('steps', 30)}")
        return kw
    done = 0
    for c in job["clips"]:
        t = time.time()
        try:
            w, h = c.get("width", job["width"]), c.get("height", job["height"])
            img = fit(Image.open(io.BytesIO(get(c["image"]))).convert("RGB"), w, h)
            pe, ne = embeds[c["name"]]
            frames = pipe(image=img, prompt_embeds=pe.to("cuda"), negative_prompt_embeds=ne.to("cuda"), height=h,
                          width=w, num_frames=c.get("frames", 81), guidance_scale=job.get("guidance", 5.0),
                          num_inference_steps=job.get("steps", 30), callback_on_step_end=step_note,
                          generator=torch.Generator("cuda").manual_seed(c.get("seed", 1))).frames[0]
            out = f"/root/{c['name']}.mp4"
            export_to_video(frames, out, fps=job.get("fps", 24))
            put(f"out/{c['name']}.mp4", open(out, "rb").read(), "video/mp4")
            done += 1
            note(f"{c['name']} made in {time.time() - t:.0f} s at {w}x{h}, {c.get('frames', 81)} frames ({done}/{len(job['clips'])})")
        except Exception as e:  # noqa: BLE001
            note(f"{c['name']} FAILED: {type(e).__name__}: {str(e)[:500]}")
            if done == 0:
                raise
    note(f"ALL DONE: {done} of {len(job['clips'])} clips")
except Exception:  # noqa: BLE001
    note("STOPPED WITH AN ERROR:\n" + traceback.format_exc()[-2500:])
