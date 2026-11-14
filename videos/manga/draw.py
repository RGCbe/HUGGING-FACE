"""Draw manga panels on our private ZeroGPU Space (Rggroups/manga-panels): Animagine XL 4.0, nothing to download.

    python draw.py SHOTS.json OUT_DIR

SHOTS.json is a list of {"name", "prompt", "seed"?, "ref"?, "ref_scale"?, "w"?, "h"?, "steps"?}. "ref" is a picture
to copy the character from (a character sheet or an earlier panel), a path relative to SHOTS.json. A panel whose
OUT_DIR/NAME.png already exists is skipped, so delete one to redraw it. Needs HF_TOKEN; each panel uses about
5 seconds of the account's daily ZeroGPU time (5 minutes free, 40 with PRO).
"""
import json
import os
import shutil
import sys
import time

from gradio_client import Client, handle_file
from huggingface_hub import get_zero_gpu_quota

SPACE = "Rggroups/manga-panels"

shots_file, out_dir = sys.argv[1], sys.argv[2]
base = os.path.dirname(os.path.abspath(shots_file))
os.makedirs(out_dir, exist_ok=True)
client = Client(SPACE, token=os.environ["HF_TOKEN"], verbose=False)
for s in json.load(open(shots_file)):
    out = os.path.join(out_dir, s["name"] + ".png")
    if os.path.exists(out) or "prompt" not in s:  # a lettering-only panel (a caption card) has no prompt
        continue
    ref = s.get("ref")
    t = time.time()
    img = client.predict(s["prompt"], "", s.get("seed", 7), s.get("w", 832), s.get("h", 1216), s.get("steps", 28), 5,
                         handle_file(os.path.join(base, ref)) if ref else None, s.get("ref_scale", 0.55),
                         api_name="/draw")
    shutil.copy(img, out)
    print(f"{s['name']}: {time.time() - t:.1f}s" + (f" (ref {ref})" if ref else ""), flush=True)
q = get_zero_gpu_quota(token=os.environ["HF_TOKEN"])
print(f"GPU time left today: {q.remaining:.0f}s of {q.base}s")
