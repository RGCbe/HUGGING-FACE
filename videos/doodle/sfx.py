"""Small sound effects for doodle videos, synthesised here so there is nothing for a copyright claim
to match: pop, stamp (a soft thump), whoosh (a picture arriving) and ding.

    python3 sfx.py EVENTS_JSON SECONDS OUT_WAV

EVENTS_JSON is render.mjs --events output, [{"t": seconds, "kind": "pop"}, ...]; every event whose
kind is a sound is placed on one mono 44.1 kHz track as long as the video (punchlines are left to
mix.py). Standard library only.
"""
import array
import json
import math
import random
import sys
import wave

SR = 44100


def pop():
    n = int(0.07 * SR)
    out, phase = [], 0.0
    for i in range(n):
        f = 900 - 600 * i / n  # pitch drops like a cork
        phase += 2 * math.pi * f / SR
        out.append(0.55 * math.sin(phase) * math.exp(-i / (0.018 * SR)))
    return out


def stamp():
    rnd = random.Random(2)
    n = int(0.16 * SR)
    out, phase, noise = [], 0.0, 0.0
    for i in range(n):
        phase += 2 * math.pi * (110 - 50 * i / n) / SR
        noise = 0.7 * noise + 0.3 * rnd.uniform(-1, 1)  # a dull slap on top of the thump
        out.append(0.6 * math.sin(phase) * math.exp(-i / (0.05 * SR)) + 0.35 * noise * math.exp(-i / (0.012 * SR)))
    return out


def whoosh():
    rnd = random.Random(3)
    n = int(0.45 * SR)
    out, lo, hi = [], 0.0, 0.0
    for i in range(n):
        x = rnd.uniform(-1, 1)
        k = 0.02 + 0.25 * math.sin(math.pi * i / n)  # the band sweeps up and back down
        lo += k * (x - lo)
        hi += 0.5 * (lo - hi)
        out.append(0.5 * (lo - hi) * math.sin(math.pi * i / n) ** 2)
    return out


def ding():
    n = int(0.9 * SR)
    return [math.exp(-i / (0.25 * SR)) * sum(a * math.sin(2 * math.pi * f * i / SR)
                                             for f, a in ((1318.5, 0.35), (2637.0, 0.1), (3955.5, 0.04)))
            for i in range(n)]


SOUNDS = {"pop": pop, "stamp": stamp, "whoosh": whoosh, "ding": ding}


def track(events, seconds):
    out = [0.0] * int(seconds * SR)
    cache = {}
    for e in events:
        if e["kind"] not in SOUNDS:
            continue
        clip = cache.setdefault(e["kind"], SOUNDS[e["kind"]]())
        start = int(e["t"] * SR)
        for i, v in enumerate(clip[: max(0, len(out) - start)]):
            out[start + i] += v
    return out


def write(path, samples):
    pcm = array.array("h", (int(max(-1.0, min(1.0, v)) * 32767) for v in samples))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    events_json, seconds, out_wav = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    write(out_wav, track(json.load(open(events_json)), seconds))
    print("wrote", out_wav)
