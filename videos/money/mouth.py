"""Lip sync for a flat host picture: the mouth is drawn by code on the SAME picture (so the face never changes), in
4 shapes (closed = the picture as it is, small, medium, wide), and each frame's shape comes from how loud the voice is
at that moment. Shapes change on twos (every 2 frames, the anime way), never for a single frame."""
import math

import numpy as np
from PIL import Image, ImageDraw

MAROON, TEETH, TONGUE, INK = (92, 30, 38), (250, 248, 242), (224, 112, 122), (38, 26, 22)
SS = 4  # supersampling for smooth edges


def _curve(p0, pm, p1, n=40):
    """Points on the quadratic through p0, pm (at u=0.5) and p1."""
    c = (2 * pm[0] - (p0[0] + p1[0]) / 2, 2 * pm[1] - (p0[1] + p1[1]) / 2)
    return [((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * c[0] + u ** 2 * p1[0],
             (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * c[1] + u ** 2 * p1[1]) for u in (i / (n - 1) for i in range(n))]


def open_mouth(img, line, h):
    """img with the mouth opened h pixels below its lip line (line = left end, middle, right end)."""
    if h <= 0:
        return img.copy()
    xs = [p[0] for p in line]
    ys = [p[1] for p in line]
    box = (int(min(xs)) - 20, int(min(ys)) - 20, int(max(xs)) + 20, int(max(ys) + h) + 20)
    crop = img.crop(box).resize(((box[2] - box[0]) * SS, (box[3] - box[1]) * SS), Image.LANCZOS)
    loc = [((x - box[0]) * SS, (y - box[1]) * SS) for x, y in line]
    top = _curve(*loc)
    n = len(top)
    bottom = [(x, y + h * SS * math.sin(math.pi * i / (n - 1)) ** 0.8) for i, (x, y) in enumerate(top)]
    shape = top + bottom[::-1]
    mask = Image.new("L", crop.size, 0)
    ImageDraw.Draw(mask).polygon(shape, fill=255)
    inside = Image.new("RGB", crop.size, MAROON)
    d = ImageDraw.Draw(inside)
    th = min(h * 0.34, 8) * SS  # upper teeth
    if h >= 9:
        a, b = int(n * 0.14), int(n * 0.86)
        d.polygon(top[a:b] + [(x, y + th) for x, y in top[a:b]][::-1], fill=TEETH)
    if h >= 16:  # the tongue at the bottom
        mx, my = bottom[n // 2]
        w = (top[-1][0] - top[0][0]) * 0.26
        d.ellipse((mx - w, my - h * SS * 0.42, mx + w, my + h * SS * 0.25), fill=TONGUE)
    crop.paste(inside, (0, 0), mask)
    d = ImageDraw.Draw(crop)
    d.line(bottom, fill=INK, width=4 * SS, joint="curve")
    d.line(top, fill=INK, width=5 * SS, joint="curve")
    crop = crop.resize((box[2] - box[0], box[3] - box[1]), Image.LANCZOS)
    out = img.copy()
    out.paste(crop, box[:2])
    return out


def levels(voice, sr, fps, n_frames, start_frame, lead=1):
    """Mouth shape 0-3 for each of n_frames, for a voice that starts at start_frame. From the loudness per frame
    (RMS, scaled to the voice's own loud peaks), with each syllable opening the mouth and the dips between syllables
    closing it part way (compared with the loudest and quietest frame within 4 frames), so it talks rather than hangs
    open. Shown `lead` frame early (the eye expects the mouth a touch before the sound); changes on twos, never for
    one frame."""
    hop = sr / fps
    m = int(len(voice) / hop) + 2
    rms = np.array([np.sqrt(np.mean(voice[int(f * hop): int((f + 1) * hop)] ** 2)) if int(f * hop) < len(voice) else 0
                    for f in range(m)])
    rms = np.convolve(rms, [0.25, 0.5, 0.25], mode="same")
    peak = np.percentile(rms[rms > 1e-4], 95) if (rms > 1e-4).any() else 1.0
    e = np.clip(rms / peak, 0, 1.2)
    lo = np.array([e[max(0, i - 4): i + 5].min() for i in range(m)])
    hi = np.array([e[max(0, i - 4): i + 5].max() for i in range(m)])
    o = e * (0.3 + 0.7 * (e - lo) / (hi - lo + 1e-6))  # a syllable's peak opens, the dip after it closes
    out = []
    for f in range(n_frames):
        k = f - start_frame + lead
        r = o[k] if 0 <= k < m else 0.0
        out.append(0 if r < 0.12 else 1 if r < 0.32 else 2 if r < 0.58 else 3)
    for f in range(1, n_frames, 2):  # on twos
        out[f] = out[f - 1]
    for f in range(2, n_frames - 2, 2):  # no lone two-frame blip between two equal shapes
        if out[f - 2] == out[f + 2] != out[f] and abs(out[f] - out[f - 2]) == 1:
            out[f] = out[f + 1] = out[f - 2]
    # a long held vowel still moves: inside a hold longer than 6 frames, the jaw eases one shape down for 2 frames
    # every 6 frames
    f = 0
    while f < n_frames:
        g = f
        while g < n_frames and out[g] == out[f]:
            g += 1
        if out[f] > 0 and g - f > 6:
            for k in range(f + 4, g - 2, 6):
                out[k] = out[k + 1] = out[f] - 1
        f = g
    return out
