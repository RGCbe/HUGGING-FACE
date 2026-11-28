"""Original background music for doodle videos: a light, playful explainer loop.

    python music.py OUT_WAV SECONDS [--bpm 104] [--seed 1]

Plucked bass, marimba arpeggios, a whistled tune that comes and goes, and soft ticks, over an
eight-bar progression. Everything is synthesised here, so there is no third-party audio and nothing
for a copyright claim to match. Needs numpy and soundfile.
"""
import argparse

import numpy as np
import soundfile as sf

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("seconds", type=float)
ap.add_argument("--bpm", type=float, default=104)
ap.add_argument("--seed", type=int, default=1)
a = ap.parse_args()

SR = 44100
rng = np.random.default_rng(a.seed)
beat = 60.0 / a.bpm
bar = 4 * beat
n_total = int((a.seconds + 2) * SR)
L = np.zeros(n_total)
R = np.zeros(n_total)


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= n_total:
        return
    sig = sig[: n_total - i] * gain
    L[i:i + len(sig)] += sig * np.sqrt(0.5 * (1 - pan))
    R[i:i + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))


def pluck(f, dur=0.6):
    """Karplus-Strong plucked string: a short noise burst through a damped delay line."""
    n = int(dur * SR)
    period = int(SR / f)
    buf = rng.uniform(-1, 1, period)
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % period]
        buf[i % period] = 0.996 * 0.5 * (buf[i % period] + buf[(i + 1) % period])
    return out * np.linspace(1, 0, n) ** 0.5


def marimba(f, dur=0.5):
    t = np.arange(int(dur * SR)) / SR
    tone = (np.sin(2 * np.pi * f * t) * np.exp(-t * 7)
            + 0.35 * np.sin(2 * np.pi * f * 4.0 * t) * np.exp(-t * 22)
            + 0.12 * np.sin(2 * np.pi * f * 9.9 * t) * np.exp(-t * 45))
    return tone * np.minimum(1, t / 0.002)


def whistle(f, dur):
    t = np.arange(int(dur * SR)) / SR
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.15)
    env = np.minimum(1, t / 0.04) * np.minimum(1, (dur - t) / 0.08)
    return np.sin(2 * np.pi * f * np.cumsum(vib) / SR) * env


def tick(dur=0.04):
    t = np.arange(int(dur * SR)) / SR
    noise = np.diff(rng.uniform(-1, 1, len(t) + 1))  # crude high-pass
    return noise * np.exp(-t * 120)


def kick():
    t = np.arange(int(0.18 * SR)) / SR
    return np.sin(2 * np.pi * (55 + 90 * np.exp(-t * 30)) * t) * np.exp(-t * 18)


# C major: C - Am - F - G | C - Am - Dm - G   (root, chord tones as MIDI notes)
progression = [(48, [60, 64, 67]), (45, [57, 60, 64]), (41, [53, 57, 60]), (43, [55, 59, 62]),
               (48, [60, 64, 67]), (45, [57, 60, 64]), (50, [62, 65, 69]), (43, [55, 59, 62])]
# A whistled tune for every other eight-bar phrase: (bar, beat offset, midi, beats)
tune = [(0, 0, 76, 1), (0, 1, 79, 1), (0, 2, 76, 2), (1, 0, 72, 1.5), (1, 1.5, 74, 0.5), (1, 2, 76, 2),
        (2, 0, 77, 1), (2, 1, 76, 1), (2, 2, 74, 2), (3, 0, 71, 2), (3, 2, 74, 2),
        (4, 0, 76, 1), (4, 1, 79, 1), (4, 2, 84, 2), (5, 0, 81, 1), (5, 1, 79, 1), (5, 2, 76, 2),
        (6, 0, 77, 1.5), (6, 1.5, 76, 0.5), (6, 2, 74, 2), (7, 0, 79, 3)]

n_bars = int(np.ceil(a.seconds / bar))
for b in range(n_bars):
    t_bar = b * bar
    root, chord = progression[b % 8]
    phrase = b // 8
    add(pluck(hz(root), 0.9), t_bar, 0.55)
    add(pluck(hz(root + 7), 0.6), t_bar + 2 * beat, 0.45)
    add(pluck(hz(root + 12), 0.4), t_bar + 3.5 * beat, 0.3)
    add(kick(), t_bar, 0.35)
    # marimba eighth notes, going up then (on odd phrases) up-and-down
    pattern = chord + [chord[0] + 12] + (chord[::-1] + [chord[1]] if phrase % 2 else chord + [chord[2] + 12])
    for k in range(8):
        add(marimba(hz(pattern[k % len(pattern)] + 12)), t_bar + k * beat / 2, 0.22, pan=0.35 if k % 2 else -0.35)
    for k in range(4):
        add(tick(), t_bar + k * beat + beat / 2, 0.08, pan=0.5)
    if phrase % 2 == 1:
        for (tb, off, note, beats) in tune:
            if tb == b % 8:
                add(whistle(hz(note), beats * beat * 0.95), t_bar + off * beat, 0.16, pan=-0.1)

# Fade in and out, normalise to a modest level (the mix ducks it further under the voice).
stereo = np.stack([L, R], axis=1)[: int(a.seconds * SR)]
fade = np.ones(len(stereo))
fi, fo = int(1.5 * SR), int(3.0 * SR)
fade[:fi] = np.linspace(0, 1, fi)
fade[-fo:] = np.linspace(1, 0, fo)
stereo *= fade[:, None]
stereo /= np.max(np.abs(stereo)) + 1e-9
sf.write(a.out, (stereo * 0.8).astype(np.float32), SR)
print(f"wrote {a.out}: {len(stereo) / SR:.1f}s at {a.bpm:.0f} bpm")
