"""Bring webtoon panels to life: each panel becomes a short anime clip on our private ZeroGPU Space
Rggroups/anime-motion (a copy of multimodalart/wan2-1-fast: Wan 2.1 image-to-video 14B, 480p, with the CausVid
LoRA so 4 steps are enough).

    python animate.py SHOTS.json IMG_DIR OUT_DIR

SHOTS.json is a list of {"name", "motion", "seconds"?, "seed"?}: "name" is a panel in IMG_DIR (NAME.png) and
"motion" says what moves ("her braid and robe blow in the wind, golden light pulses, the camera slowly pushes
in"). A clip already in OUT_DIR is skipped, so delete one to make it again. Each 2-second clip reserves about
60 s of the account's daily ZeroGPU time (300 s free, 40 min with PRO); the script stops cleanly when the day's
time runs out, and running it again the next day carries on. Needs HF_TOKEN.
"""
import json
import os
import shutil
import sys
import time

from gradio_client import Client, handle_file
from huggingface_hub import get_zero_gpu_quota
from PIL import Image

SPACE = "Rggroups/anime-motion"
STYLE = "anime, 2d animation, clean line art, consistent character, "
NEGATIVE = ("static, still picture, blurred details, worst quality, low quality, deformed, disfigured, extra fingers, "
            "poorly drawn hands, poorly drawn faces, morphing, flicker, watermark, text, subtitles, signature")
RESERVE = {2: 60, 3: 75}  # seconds of GPU time the Space reserves for a clip of this length at 4 steps

shots_file, img_dir, out_dir = sys.argv[1:4]
os.makedirs(out_dir, exist_ok=True)
token = os.environ["HF_TOKEN"]
client = None
for s in json.load(open(shots_file)):
    out = os.path.join(out_dir, s["name"] + ".mp4")
    if os.path.exists(out):
        continue
    secs = s.get("seconds", 2)
    left = get_zero_gpu_quota(token=token).remaining
    if left < RESERVE.get(secs, 75):
        print(f"stopping: {left:.0f} s of GPU time left today; run again after the daily reset")
        break
    img = os.path.join(img_dir, s["name"] + ".png")
    w, h = Image.open(img).size
    # 480p: the longer side 832, the shorter one in proportion, both multiples of 32
    scale = 832 / max(w, h)
    width, height = (round(w * scale / 32) * 32, round(h * scale / 32) * 32)
    client = client or Client(SPACE, token=token, verbose=False)
    t = time.time()
    r = client.predict(handle_file(img), STYLE + s["motion"], height, width, NEGATIVE, secs, 1.0, 4,
                       s.get("seed", 7), False, api_name="/generate_video")
    video = r[0]["video"] if isinstance(r[0], dict) else r[0]
    shutil.copy(video, out)
    print(f"{s['name']}: {secs}s clip {width}x{height} in {time.time() - t:.0f}s, "
          f"{left - get_zero_gpu_quota(token=token).remaining:.0f}s of GPU time", flush=True)
print(f"GPU time left today: {get_zero_gpu_quota(token=token).remaining:.0f}s")
