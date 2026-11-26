"""Fix one small area of a picture and leave the rest of it exactly as it was (a masked repaint).

    python3 patch_edit.py SRC.png OUT.png --box X0 Y0 X1 Y1 --prompt "his lower glove wraps the same handle ..."
                         [--seed 7] [--margin 0.6] [--feather 18] [--engine auto]
    python3 patch_edit.py SRC.png OUT.png --paintout X0 Y0 X1 Y1 [--paintout ...]   # remove small things only

--box: the area to redraw, in SRC pixels. A square crop around it (the box plus --margin of its size on each side,
for context) goes to the picture model as an edit at 1328x1328, so the model sees the area large. Only the box,
with a soft --feather edge, is pasted back. Every pixel outside it stays the original.
--paintout: small things to remove (a stray ball, a sticker, letters). The area is filled from its surroundings with
OpenCV (Navier-Stokes inpainting), locally, with no GPU. Applied after the box.
Why (26 Nov 2026): a whole-picture edit kept the old pose or broke other parts (it took a stick from every drummer).
Where data goes: the crop goes only to the owner's own picture Space (imagegen.py --engine own), or to Cloudflare
with --engine auto when its GPU time is used up, like every picture we make.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))


def square_crop(box, margin, w, h):
    x0, y0, x1, y1 = box
    side = int(max(x1 - x0, y1 - y0) * (1 + 2 * margin))
    side = max(160, min(side, w, h))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    left = min(max(0, cx - side // 2), w - side)
    top = min(max(0, cy - side // 2), h - side)
    return left, top, left + side, top + side


def repaint(img, box, prompt, seed, margin, feather, engine):
    w, h = img.size
    crop_box = square_crop(box, margin, w, h)
    crop = img.crop(crop_box)
    with tempfile.TemporaryDirectory() as d:
        crop.save(os.path.join(d, "crop.png"))
        spec = {"style": "", "aspect": "1:1", "images": [{
            "name": "patch", "edit": os.path.join(d, "crop.png"), "seed": seed,
            "prompt": ("A close-up crop of a painted anime picture. The same crop, but " + prompt.rstrip(".") +
                       ". Everything else in the crop stays exactly the same, in the same painted anime style.")}]}
        json.dump(spec, open(os.path.join(d, "spec.json"), "w"))
        subprocess.run([sys.executable, os.path.join(HERE, "imagegen.py"), os.path.join(d, "spec.json"), d,
                        "--engine", engine], check=True)
        patch = Image.open(os.path.join(d, "patch.png")).convert("RGB").resize(crop.size, Image.LANCZOS)
    # paste back only the box (relative to the crop), with a soft edge
    mask = Image.new("L", crop.size, 0)
    bx0, by0 = box[0] - crop_box[0], box[1] - crop_box[1]
    bx1, by1 = box[2] - crop_box[0], box[3] - crop_box[1]
    mask.paste(255, (bx0, by0, bx1, by1))
    mask = mask.filter(ImageFilter.GaussianBlur(feather))
    out = img.copy()
    out.paste(Image.composite(patch, crop, mask), crop_box[:2])
    return out


def paintout(img, boxes):
    import cv2
    a = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    mask = np.zeros(a.shape[:2], np.uint8)
    for x0, y0, x1, y1 in boxes:
        mask[y0:y1, x0:x1] = 255
    a = cv2.inpaint(a, mask, 4, cv2.INPAINT_NS)
    return Image.fromarray(cv2.cvtColor(a, cv2.COLOR_BGR2RGB))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--box", type=int, nargs=4)
    ap.add_argument("--prompt")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--margin", type=float, default=0.6)
    ap.add_argument("--feather", type=int, default=18)
    ap.add_argument("--engine", default="auto", choices=["own", "auto", "cloudflare"])
    ap.add_argument("--paintout", type=int, nargs=4, action="append", default=[])
    a = ap.parse_args()
    if a.box and not a.prompt:
        ap.error("--box needs --prompt")
    img = Image.open(a.src).convert("RGB")
    if a.box:
        img = repaint(img, a.box, a.prompt, a.seed, a.margin, a.feather, a.engine)
    if a.paintout:
        img = paintout(img, a.paintout)
    img.save(a.out)
    diff = (np.abs(np.asarray(img, np.int16) - np.asarray(Image.open(a.src).convert("RGB"), np.int16)).sum(2) > 30)
    print(f"{a.out}: {diff.mean() * 100:.1f}% of the pixels changed")


if __name__ == "__main__":
    main()
