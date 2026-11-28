"""Make an AI-animated clip feel like TV anime: drawn "on twos" (12 drawings a second, each held for two frames),
with an impact frame, speed lines and a camera shake on the hit (the owner, 26 Nov 2026: make it like the real
anime, Dragon Ball and One Piece).

    python3 anime_fx.py IN.mp4 OUT.mp4 [--twos] [--impact T] [--lines T0 T1] [--shake T0 T1] [--fps 30]

--twos         12 drawings a second, the anime look (the clip's own motion is kept, only fewer distinct frames).
--impact T     at T seconds: 3 frames of impact flash (inverted, then black-and-white high contrast, then white),
               the classic hit frame.
--lines T0 T1  radial speed lines from the centre between T0 and T1, fading out.
--shake T0 T1  a camera shake between T0 and T1, strongest at T0.
Local only (numpy + ffmpeg).
"""
import argparse
import subprocess

import numpy as np


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate,nb_frames", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout.strip().split(",")
    w, h = int(out[0]), int(out[1])
    num, den = out[2].split("/")
    return w, h, float(num) / float(den)


def speed_lines(w, h, rng, count=90):
    """An alpha mask of thin radial lines from the edges towards (not reaching) the centre."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = w / 2, h / 2
    ang = np.arctan2(yy - cy, xx - cx)
    rad = np.hypot(xx - cx, yy - cy) / np.hypot(cx, cy)
    mask = np.zeros((h, w), np.float32)
    for a in rng.uniform(-np.pi, np.pi, count):
        width = rng.uniform(0.002, 0.007)
        start = rng.uniform(0.35, 0.6)
        d = np.abs(np.angle(np.exp(1j * (ang - a))))
        mask = np.maximum(mask, np.clip(1 - d / width, 0, 1) * np.clip((rad - start) / 0.15, 0, 1))
    return mask


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--twos", action="store_true")
    ap.add_argument("--impact", type=float)
    ap.add_argument("--lines", type=float, nargs=2)
    ap.add_argument("--shake", type=float, nargs=2)
    ap.add_argument("--fps", type=int, default=30)
    a = ap.parse_args()
    w, h, _ = probe(a.src)
    fps = a.fps
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", a.src, "-vf", f"fps={fps}", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3).copy()
    n = len(frames)
    rng = np.random.default_rng(7)
    lines = [speed_lines(w, h, rng) for _ in range(3)] if a.lines else None
    out = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s",
                            f"{w}x{h}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
                            "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
    step = fps / 12.0  # on twos: each drawing shown for fps/12 frames
    for i in range(n):
        t = i / fps
        src = frames[min(n - 1, int(int(i / step) * step))] if a.twos else frames[i]
        f = src.astype(np.float32)
        if a.impact is not None:
            k = int(round((t - a.impact) * fps))
            if k == 0:
                f = 255 - f  # inverted
            elif k == 1:
                g = f.mean(axis=2, keepdims=True)
                f = np.repeat(np.where(g > 110, 255.0, 0.0), 3, axis=2)  # black and white, hard
            elif k == 2:
                f = f * 0.3 + 255 * 0.7  # white flash
        if lines is not None and a.lines[0] <= t <= a.lines[1]:
            strength = 1 - (t - a.lines[0]) / max(1e-6, a.lines[1] - a.lines[0])
            m = lines[(i // 2) % 3][..., None] * (0.85 * strength)
            f = f * (1 - m) + 255 * m
        if a.shake and a.shake[0] <= t <= a.shake[1]:
            amp = 18 * (1 - (t - a.shake[0]) / max(1e-6, a.shake[1] - a.shake[0]))
            dx, dy = int(rng.uniform(-amp, amp)), int(rng.uniform(-amp, amp))
            f = np.roll(np.roll(f, dy, axis=0), dx, axis=1)
        out.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
    out.stdin.close()
    if out.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print("anime fx:", a.out)


if __name__ == "__main__":
    main()
