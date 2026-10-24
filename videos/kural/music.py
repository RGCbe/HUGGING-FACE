"""Background music for Super Kural: a gentle Indian-style tune, synthesised so it is all original.

    python3 music.py OUT_WAV SECONDS [--seed 1] [--bpm 88]

A tanpura drone (Pa Sa Sa Sa) runs underneath. A bansuri-like flute plays in raga Mohanam
(S R2 G3 P D2, the five notes many Tamil children's songs use): the same short theme opens every
video, then the seed picks new phrases, with rests between them so the voice has room. Soft tabla
strokes keep an 8-beat keherwa and small bells ring on each bar. Ends on Sa with the drone ringing out.
"""
import argparse

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("seconds", type=float)
ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--bpm", type=float, default=88)
a = ap.parse_args()

SR = 44100
rng = np.random.default_rng(a.seed)
beat = 60.0 / a.bpm
bar = 8 * beat  # one keherwa cycle
total = a.seconds
n = int((total + 3) * SR)
left = np.zeros(n)
right = np.zeros(n)
SA = 146.83  # D3
SCALE = [0, 2, 4, 7, 9]  # Mohanam


def hz(semis, octave=0):
    return SA * 2 ** (semis / 12 + octave)


def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= n:
        return
    sig = sig[: n - i] * gain
    left[i:i + len(sig)] += sig * np.sqrt(0.5 * (1 - pan))
    right[i:i + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))


def tanpura(f, dur=4.5):
    # Many harmonics that bloom and fade one after another, like the jawari bridge's buzz.
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    for k in range(1, 16):
        bloom = 1 - np.exp(-t / (0.05 + 0.06 * k))
        out += np.sin(2 * np.pi * f * k * t + rng.uniform(0, 6.28)) * (0.9 ** k) * bloom * np.exp(-t * (0.5 + 0.08 * k))
    out *= np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.5)
    return out / 4


def flute(f, dur, glide_from=None):
    t = np.arange(int(dur * SR)) / SR
    pitch = np.full_like(t, f)
    if glide_from:  # a little meend from the previous note
        g = np.minimum(1, t / 0.09)
        pitch = glide_from + (f - glide_from) * (g * g * (3 - 2 * g))
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, np.maximum(0, t - 0.25) / 0.3)
    phase = 2 * np.cumsum(np.pi * pitch * vib) / SR
    tone = np.sin(phase) + 0.18 * np.sin(2 * phase) + 0.06 * np.sin(3 * phase)
    breath = np.convolve(rng.standard_normal(len(t)), np.hanning(40) / 20, mode="same") * 0.05
    env = np.minimum(1, t / 0.06) * np.minimum(1, (dur - t) / 0.12) * (1 - 0.15 * t / dur)
    return (tone + breath) * env * 0.5


def drum(f0, f1, dur, ring=0.0, noise=0.0):
    t = np.arange(int(dur * SR)) / SR
    pitch = f1 + (f0 - f1) * np.exp(-t / 0.04)
    body = np.sin(2 * np.pi * np.cumsum(pitch) / SR) * np.exp(-t / (0.12 + ring))
    hiss = np.convolve(rng.standard_normal(len(t)), np.hanning(12) / 6, mode="same") * np.exp(-t / 0.008) * noise
    return (body + hiss) * np.minimum(1, t / 0.002)


def bell(dur=1.2):
    t = np.arange(int(dur * SR)) / SR
    out = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) * g for f, d, g in
              [(2960, 4.0, 1.0), (4170, 5.5, 0.6), (5530, 7.0, 0.4), (7400, 9.0, 0.25)])
    return out * np.minimum(1, t / 0.001) * 0.12


# Drone: Pa, Sa, Sa, low Sa, round and round.
t = 0.0
cycle = [hz(-5), hz(0), hz(0), hz(0, -1)]
k = 0
while t < total + 1.5:
    add(tanpura(cycle[k % 4]), t, 0.22, -0.3 + 0.2 * (k % 2))
    t += bar / 4
    k += 1

# Tabla: keherwa  dha ge na ti | na ka dhi na  (dha/dhi = bass + treble, ge = bass, na/ti/ka = treble)
strokes = ["dha", "ge", "na", "ti", "na", "ka", "dhi", "na"]
t = bar  # the tune starts alone for one cycle
while t < total - beat:
    for i, s in enumerate(strokes):
        when = t + i * beat
        if when >= total - beat:
            break
        if s in ("dha", "dhi", "ge"):
            add(drum(120, 70, 0.5, ring=0.15), when, 0.36 if i == 0 else 0.24, -0.1)
        if s in ("dha", "dhi", "na"):
            add(drum(560, 520, 0.35, ring=0.1, noise=0.08), when, 0.16, 0.15)
        if s in ("ti", "ka"):
            add(drum(820, 780, 0.12, noise=0.12), when, 0.07, 0.2)
    add(bell(), t, 1.0, 0.4)
    t += bar

# Flute: the series theme first, then seeded phrases in Mohanam with room between them.
deg = lambda d: (SCALE[d % 5], d // 5)  # scale degree -> (semitones, octave), degree 5 = upper Sa
THEME = [(5, 1), (6, 0.5), (7, 0.5), (8, 1), (7, 1), (6, 0.5), (5, 0.5), (4, 2), (3, 0.5), (4, 0.5), (5, 3)]


def phrase():
    notes, d, beats = [], int(rng.choice([5, 7, 8])), 0
    while beats < 6:
        d = int(np.clip(d + rng.choice([-2, -1, -1, 1, 1, 2]), 3, 10))
        length = float(rng.choice([0.5, 0.5, 1, 1, 1.5, 2]))
        notes.append((d, length))
        beats += length
    notes.append((int(rng.choice([5, 7, 10])), 2.0))  # rest on Sa, Pa or upper Sa
    return notes


t, prev = 0.0, None
plan = [THEME]
while sum(sum(l for _, l in p) for p in plan) * beat + len(plan) * 4 * beat < total - bar:
    plan.append(phrase())
for p in plan:
    for d, length in p:
        semis, octave = deg(d)
        f = hz(semis, octave + 1)
        dur = length * beat
        if t + dur > total - 0.5:
            break
        add(flute(f, dur * 0.98, glide_from=prev if prev and rng.random() < 0.3 else None), t, 0.32, 0.05)
        prev = f
        t += dur
    t += 4 * beat  # breathe
add(flute(hz(0, 1), 2.5), max(0, total - 2.6), 0.3, 0.05)  # final Sa

# A little room: a short decaying-noise reverb.
ir_t = np.arange(int(1.1 * SR)) / SR
ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t / 0.28)
ir[0] = 0
ir /= np.abs(ir).sum() / 6


def reverb(x):
    m = 1 << int(np.ceil(np.log2(len(x) + len(ir))))
    return np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[: len(x)]


left = left + 0.18 * reverb(left)
right = right + 0.18 * reverb(right)
fade = np.ones(n)
end = int(total * SR)
fade[end - int(1.5 * SR):end] = np.linspace(1, 0, int(1.5 * SR))
fade[end:] = 0
stereo = np.stack([left, right], 1)[: end] * fade[:end, None]
stereo *= 0.8 / max(1e-9, np.abs(stereo).max())

import wave  # noqa: E402  (standard library writer keeps this script dependency-light)

with wave.open(a.out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((stereo * 32767).astype("<i2").tobytes())
print(f"wrote {a.out}: {total:.1f}s, raga Mohanam at {a.bpm:.0f} bpm, seed {a.seed}")
