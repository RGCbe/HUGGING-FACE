"""Capability test: letter panels into a WEBTOON strip (800 px wide) and cut it into upload slices."""
import json
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, GAP, MARGIN = 800, 150, 80
DIALOGUE = os.path.join(HERE, "fonts", "ComicNeue-Bold.ttf")
SFX = os.path.join(HERE, "fonts", "Bangers-Regular.ttf")


def wrap(text, font, width):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if font.getlength(trial) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]


def text_block(draw, lines, font, cx, top, fill):
    h = font.size * 1.18
    for i, line in enumerate(lines):
        draw.text((cx - font.getlength(line) / 2, top + i * h), line, font=font, fill=fill)


def bubble(img, b, box):
    """A speech or thought bubble around the text, its tail pointing at the speaker."""
    x0, y0, pw, ph = box
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(DIALOGUE, b.get("size", 27))
    lines = wrap(b["text"].upper(), font, b.get("w", 0.4) * pw)
    tw = max(font.getlength(l) for l in lines)
    th = len(lines) * font.size * 1.18
    cx, cy = x0 + b["x"] * pw, y0 + b["y"] * ph  # the bubble's centre
    rx, ry = tw / 2 * 1.32 + 14, th / 2 * 1.45 + 12
    if b.get("to"):
        tx, ty = x0 + b["to"][0] * pw, y0 + b["to"][1] * ph
        ang = math.atan2(ty - cy, tx - cx)
        base = [(cx + rx * 0.55 * math.cos(ang + s), cy + ry * 0.55 * math.sin(ang + s)) for s in (-0.35, 0.35)]
        if b.get("kind") == "thought":
            for k, r in ((0.35, 13), (0.6, 9), (0.8, 6)):
                px, py = cx + (tx - cx) * k, cy + (ty - cy) * k
                draw.ellipse([px - r, py - r, px + r, py + r], fill="white", outline="black", width=3)
        else:
            draw.polygon([base[0], (tx, ty), base[1]], fill="white", outline="black", width=3)
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill="white", outline="black", width=3)
    if b.get("to") and b.get("kind") != "thought":
        draw.polygon([base[0], (cx + (tx - cx) * 0.02, cy + (ty - cy) * 0.02), base[1]], fill="white")
        inner = [(cx + (bx - cx) * 0.9, cy + (by - cy) * 0.9) for bx, by in base]
        draw.polygon([inner[0], (tx - (tx - cx) * 0.06, ty - (ty - cy) * 0.06), inner[1]], fill="white")
    text_block(draw, lines, font, cx, cy - th / 2, "black")


def narration(img, n, top):
    """A dark caption box, centred in the gap above or below a panel."""
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(DIALOGUE, n.get("size", 26))
    lines = wrap(n["text"], font, W * 0.72)
    tw = max(font.getlength(l) for l in lines)
    th = len(lines) * font.size * 1.18
    x0 = W / 2 - tw / 2 - 22
    draw.rounded_rectangle([x0, top, W - x0, top + th + 28], radius=10, fill="#1d1d1f")
    text_block(draw, lines, font, W / 2, top + 12, "white")
    return th + 28


def sfx(img, s, box):
    x0, y0, pw, ph = box
    font = ImageFont.truetype(SFX, s.get("size", 120))
    w = int(font.getlength(s["text"])) + 40
    layer = Image.new("RGBA", (w, int(font.size * 1.4)), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((20, 10), s["text"], font=font, fill=s.get("color", "#ffd43b"), stroke_width=7, stroke_fill="black")
    layer = layer.rotate(s.get("rotate", 8), expand=True, resample=Image.BICUBIC)
    img.alpha_composite(layer, (int(x0 + s["x"] * pw - layer.width / 2), int(y0 + s["y"] * ph - layer.height / 2)))


def build(script, out_dir):
    panels = []
    for p in script:
        im = Image.open(os.path.join(HERE, "img", p["img"])).convert("RGB")
        panels.append(im.resize((W, round(im.height * W / im.width)), Image.LANCZOS))
    height = MARGIN * 2 + sum(p.height for p in panels) + GAP * (len(panels) - 1)
    strip = Image.new("RGBA", (W, height), "white")
    y, boxes = MARGIN, []
    for p, im in zip(script, panels):
        strip.paste(im, (0, y))
        boxes.append((0, y, W, im.height))
        y += im.height + GAP
    for p, box in zip(script, boxes):
        for n in p.get("before", []):  # narration in the gap above the panel
            narration(strip, n, box[1] - GAP + 20)
        for n in p.get("after", []):
            narration(strip, n, box[1] + box[3] + 20)
        for b in p.get("bubbles", []):
            bubble(strip, b, box)
        for s in p.get("sfx", []):
            sfx(strip, s, box)
    strip = strip.convert("RGB")
    os.makedirs(out_dir, exist_ok=True)
    strip.save(os.path.join(out_dir, "strip.png"))
    # WEBTOON CANVAS takes images up to 800 x 1280 px: cut the strip into slices in reading order
    for k, top in enumerate(range(0, strip.height, 1280), 1):
        strip.crop((0, top, W, min(strip.height, top + 1280))).save(os.path.join(out_dir, f"slice_{k:02d}.jpg"), quality=92)
    json.dump([{"img": p["img"], "top": b[1], "height": b[3]} for p, b in zip(script, boxes)],
              open(os.path.join(out_dir, "panels.json"), "w"), indent=1)
    return strip


SCRIPT = [
    {"img": "p1.png",
     "before": [{"text": "In 2031, Gates to monster dungeons opened in every city on Earth."}],
     "after": [{"text": "And right next to the biggest Gate in Mumbai... stood a tiny tea stall."}]},
    {"img": "p2.png",
     "bubbles": [{"text": "Chai! Hot chai! Ten rupees a glass!", "x": 0.25, "y": 0.13, "w": 0.36, "to": [0.6, 0.27]}],
     "after": [{"text": "Arjun. Eighteen years old. F-Rank: the weakest rank there is."}]},
    {"img": "p3.png",
     "bubbles": [{"text": "Tea? From an F-Rank? Is it poisoned with weakness?", "x": 0.22, "y": 0.14, "w": 0.34, "to": [0.5, 0.47]}]},
    {"img": "p4.png",
     "bubbles": [{"text": "Ha! Look, everyone! The F-Rank tea boy!", "x": 0.2, "y": 0.13, "w": 0.32, "to": [0.33, 0.2]},
                 {"text": "Enjoy your tea, sir. Good luck in there.", "x": 0.8, "y": 0.13, "w": 0.3, "size": 24, "to": [0.69, 0.3]}]},
    {"img": "p5.png",
     "before": [{"text": "One hour later. Dungeon, level 9."}],
     "sfx": [{"text": "KRAAACK!!", "x": 0.7, "y": 0.18, "size": 100, "rotate": 9}],
     "bubbles": [{"kind": "thought", "text": "What... is this power?!", "x": 0.17, "y": 0.16, "w": 0.26, "to": [0.38, 0.3]}]},
    {"img": "p6.png",
     "before": [{"text": "Nobody knew the truth about his tea."}],
     "bubbles": [{"text": "One hour. That's all you get.", "x": 0.79, "y": 0.86, "w": 0.3, "size": 24, "to": [0.62, 0.7]}]},
]

if __name__ == "__main__":
    s = build(SCRIPT, os.path.join(HERE, "out"))
    print("strip", s.size)
