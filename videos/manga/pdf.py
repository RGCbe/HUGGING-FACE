"""A lettered episode as a PDF to read or share: cover, the strip cut into pages, a credits page.

    python pdf.py EPISODE_DIR "Series" "Episode 1 - Title" OUT.pdf

Uses EPISODE_DIR/out/webtoon/strip.png (from letter.py) and EPISODE_DIR/upload/thumb-vertical.jpg. Pages
break only on rows that are plain white, so no panel, bubble or caption is cut in half.
"""
import io
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_H, MIN_H, SCALE = 1800, 900, 0.75  # page heights in strip pixels; 800 px wide pages are 600 pt

ep_dir, series, episode, out = sys.argv[1:5]
strip = Image.open(os.path.join(ep_dir, "out", "webtoon", "strip.png")).convert("RGB")
white = (np.asarray(strip.convert("L")) > 245).all(axis=1)

pages, top = [], 0
while top < strip.height:
    if strip.height - top <= MAX_H:
        cut = strip.height
    else:
        rows = np.nonzero(white[top + MIN_H:top + MAX_H])[0]
        cut = top + MIN_H + int(rows[-1]) if len(rows) else top + MAX_H
    page = strip.crop((0, top, strip.width, cut))
    if not white[top:cut].all():  # skip a page that would be only white space
        pages.append(page)
    top = cut


def credits():
    im = Image.new("RGB", (800, 1100), "#0d0d0f")
    d = ImageDraw.Draw(im)
    big = ImageFont.truetype(os.path.join(HERE, "fonts", "Bangers-Regular.ttf"), 76)
    small = ImageFont.truetype(os.path.join(HERE, "fonts", "ComicNeue-Bold.ttf"), 30)
    lines = [(series.upper(), big, "#ffd43b"), (episode, small, "white"), ("", small, "white"),
             ("Story and lettering by Manoj", small, "white"), ("Art made with AI tools", small, "#bbbbbb"),
             ("", small, "white"), ("New episode every week on WEBTOON CANVAS", small, "white")]
    y = 330
    for text, font, fill in lines:
        d.text((400 - font.getlength(text) / 2, y), text, font=font, fill=fill)
        y += font.size * 1.5
    return im


c = canvas.Canvas(out)
c.setTitle(f"{series} - {episode}")
c.setAuthor("Manoj")
cover = Image.open(os.path.join(ep_dir, "upload", "thumb-vertical.jpg")).convert("RGB").resize((800, 1422), Image.LANCZOS)
for im in [cover] + pages + [credits()]:
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=90)
    w, h = im.width * SCALE, im.height * SCALE
    c.setPageSize((w, h))
    c.drawImage(ImageReader(io.BytesIO(buf.getvalue())), 0, 0, w, h)
    c.showPage()
c.save()
print(f"{out}: {len(pages) + 2} pages, {os.path.getsize(out) / 1e6:.1f} MB")
