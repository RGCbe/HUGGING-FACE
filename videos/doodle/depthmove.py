"""Pictures that move in 3D: a camera that pushes in or slides past a picture, near things moving more than far ones.

    python3 depthmove.py PICTURE.png OUT.mp4 SECONDS [--move 0-3] [--size 1080x1920] [--fps 30]

The owner's wish (22 Nov 2026, "Ok"): our flat doodles should move like a camera moving through them. Blender can do
this, but in our cloud machine (no graphics card) it took about an hour per Short.

How it works:
- A small depth model guesses how near each part of the picture is (1 = near, 0 = far). The model is Depth Anything V2
  Small, Apache-2.0, as ONNX, run with onnxruntime on the CPU in about a second. The depth map is kept next to the
  picture as NAME.depth.png, so the Tamil and English videos share it.
- Each frame is warped from the picture: near parts zoom and slide more than the background. The moves are
  push in, slide left to right, pull out, and slide up.
- A host picture that has NAME.open.png and NAME.closed.png next to it talks: its mouth opens on the voice's loud
  peaks (mouth_flags) and closes in the pauses. The owner's doodle host has these: videos/office/host/.

Safety (CLAUDE.md):
- The model is an ONNX file, so it holds no pickle and can't run hidden code.
- It is downloaded once at a pinned revision, and its SHA-256 is checked before use.
- Its libraries (onnxruntime 1.32.0, opencv-python-headless 5.1.0.95) had no known issues on 22 Nov 2026.
"""
import argparse
import hashlib
import os
import subprocess
import urllib.request

import numpy as np

MODEL_REPO = "onnx-community/depth-anything-v2-small"
MODEL_REV = "4472b7362082ad9968fee890ca0f1e5aca36b93d"
MODEL_SHA256 = "afb6a5c28f3b6bf1618c6e43f02073ef9dfdc70e937502d51603e57b0a1df10c"
MODEL_PATH = os.path.expanduser(f"~/.cache/doodle/depth-anything-v2-small-{MODEL_REV[:8]}.onnx")
SIDE = 518  # the model's input side (a multiple of 14)
MEAN, STD = np.array([0.485, 0.456, 0.406], np.float32), np.array([0.229, 0.224, 0.225], np.float32)


def model_file():
    if not os.path.exists(MODEL_PATH):
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        url = f"https://huggingface.co/{MODEL_REPO}/resolve/{MODEL_REV}/onnx/model.onnx"
        tmp = MODEL_PATH + ".part"
        urllib.request.urlretrieve(url, tmp)  # a public model: no token is sent
        got = hashlib.sha256(open(tmp, "rb").read()).hexdigest()
        if got != MODEL_SHA256:
            os.remove(tmp)
            raise SystemExit(f"depth model checksum mismatch ({got}); refusing to use it")
        os.replace(tmp, MODEL_PATH)
    return MODEL_PATH


def depth(img_path):
    """The picture's depth as float32 in [0, 1] (1 = near), at the picture's size; cached as NAME.depth.png."""
    import cv2
    cache = os.path.splitext(img_path)[0] + ".depth.png"
    if os.path.exists(cache) and os.path.getmtime(cache) >= os.path.getmtime(img_path):
        return cv2.imread(cache, cv2.IMREAD_UNCHANGED).astype(np.float32) / 65535.0
    import onnxruntime as ort
    bgr = cv2.imread(img_path, cv2.IMREAD_COLOR)
    h, w = bgr.shape[:2]
    rgb = cv2.cvtColor(cv2.resize(bgr, (SIDE, SIDE), interpolation=cv2.INTER_CUBIC), cv2.COLOR_BGR2RGB)
    x = ((rgb.astype(np.float32) / 255.0 - MEAN) / STD).transpose(2, 0, 1)[None]
    sess = ort.InferenceSession(model_file(), providers=["CPUExecutionProvider"])
    d = sess.run(None, {sess.get_inputs()[0].name: x})[0].squeeze().astype(np.float32)
    d = cv2.resize(d, (w, h), interpolation=cv2.INTER_CUBIC)
    lo, hi = np.percentile(d, 2), np.percentile(d, 98)
    d = np.clip((d - lo) / max(hi - lo, 1e-6), 0, 1)
    d = cv2.GaussianBlur(d, (0, 0), sigmaX=max(w, h) / 200)  # soft edges: less tearing around outlines
    cv2.imwrite(cache, (d * 65535).astype(np.uint16))
    return d


MOVES = [  # (zoom start, zoom end, slide x start, slide x end, slide y start, slide y end); slides in parts of the width
    (1.06, 1.18, 0.0, 0.0, 0.0, 0.0),       # push in
    (1.12, 1.12, -0.025, 0.025, 0.0, 0.0),  # slide left to right
    (1.18, 1.06, 0.0, 0.0, 0.0, 0.0),       # pull out
    (1.12, 1.12, 0.0, 0.0, 0.02, -0.02),    # slide up
]


def mouth_flags(voice, sr, f0, f1, fps=30):
    """For frames f0..f1-1 of a voice timeline that starts at frame 0: True where the mouth should be open. It opens
    on the loud peaks of speech (about one per syllable) and stays shut in pauses; no state lasts a single frame."""
    hop = sr / fps
    def rms(f):
        a = voice[int(f * hop): int((f + 1) * hop)]
        return float(np.sqrt(np.mean(a * a))) if len(a) else 0.0
    every = np.array([rms(f) for f in range(int(len(voice) / hop))])
    loud = every[every > 1e-4]
    thr = 0.18 * (np.percentile(loud, 95) if len(loud) else 1.0)
    r = np.array([rms(f) for f in range(max(0, f0 - 2), f1 + 2)])
    off = f0 - max(0, f0 - 2)
    flags = []
    for f in range(f0, f1):
        i = f - f0 + off
        flags.append(bool(r[i] > thr and r[i] >= 0.6 * r[max(0, i - 2): i + 3].max()))
    for i in range(1, len(flags) - 1):  # no one-frame flicker
        if flags[i] != flags[i - 1] and flags[i] != flags[i + 1]:
            flags[i] = flags[i - 1]
    return flags


def shot(img_path, out, seconds, move=0, size=(1080, 1920), fps=30, punch=True, talk=None):
    """One picture as a 3D-moving shot, written to out (H.264). talk = (open_png, closed_png, flags): a host picture
    whose mouth opens on the frames where flags is True (mouth_flags), so the host speaks with the voice."""
    import cv2
    W, H = size
    n = max(2, int(round(seconds * fps)))
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    d = depth(img_path)
    # cover the frame (crop the picture to 9:16 around its centre), at the output size
    h, w = img.shape[:2]
    s = max(W / w, H / h)
    size_s = (int(round(w * s)), int(round(h * s)))
    interp = cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC
    img = cv2.resize(img, size_s, interpolation=interp)
    faces = None
    if talk:
        faces = [cv2.resize(cv2.imread(talk[1], cv2.IMREAD_COLOR), size_s, interpolation=interp),
                 cv2.resize(cv2.imread(talk[0], cv2.IMREAD_COLOR), size_s, interpolation=interp)]
    d = cv2.resize(d, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR)
    oy, ox = (img.shape[0] - H) // 2, (img.shape[1] - W) // 2
    cx, cy = img.shape[1] / 2, img.shape[0] / 2
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    x0, y0 = xs + ox - cx, ys + oy - cy  # each output pixel, centred on the picture's centre
    z0, z1, sx0, sx1, sy0, sy1 = MOVES[move % len(MOVES)]
    ff = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s",
                           f"{W}x{H}", "-r", str(fps), "-i", "-", "-vf", "eq=contrast=1.04:saturation=1.08,format=yuv420p",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", out], stdin=subprocess.PIPE)
    for i in range(n):
        t = i / (n - 1)
        t = t * t * (3 - 2 * t)  # ease in and out
        z = z0 + (z1 - z0) * t
        if punch:
            z *= 1 + 0.05 * max(0.0, 1 - i / 5)  # the small punch-in on every cut
        shift_x, shift_y = (sx0 + (sx1 - sx0) * t) * W, (sy0 + (sy1 - sy0) * t) * H
        # depth where each output pixel lands under the plain move, then the move scaled by that depth:
        # near things (d = 1) zoom and slide fully, the far background (d = 0) about 55% as much: gentle enough that
        # outlines don't smear
        for _ in range(2):
            if _ == 0:
                mx, my = x0 / z + cx - shift_x, y0 / z + cy - shift_y
            k = cv2.remap(d, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            weight = 0.55 + 0.45 * k
            zz = 1 + (z - 1) * weight
            mx = (x0 / zz + cx - shift_x * weight).astype(np.float32)
            my = (y0 / zz + cy - shift_y * weight).astype(np.float32)
        src = faces[int(bool(talk[2][min(i, len(talk[2]) - 1)]))] if faces else img
        frame = cv2.remap(src, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        ff.stdin.write(frame.tobytes())
    ff.stdin.close()
    if ff.wait() != 0:
        raise SystemExit(f"ffmpeg failed writing {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("picture")
    ap.add_argument("out")
    ap.add_argument("seconds", type=float)
    ap.add_argument("--move", type=int, default=0)
    ap.add_argument("--size", default="1080x1920")
    ap.add_argument("--fps", type=int, default=30)
    a = ap.parse_args()
    w, h = map(int, a.size.split("x"))
    shot(a.picture, a.out, a.seconds, a.move, (w, h), a.fps)


if __name__ == "__main__":
    main()
