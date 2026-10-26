"""Original background music that follows the story's moods, like a film score.

    python3 score.py OUT_WAV SECONDS --events EVENTS.json [--seed 1] [--sf2 FILE]

EVENTS.json is render.mjs --events output. Its mood events (scenes.js: D.mood(t, 'suspense'))
split the video into stretches, and each stretch gets its own piece in that mood: composed here
note by note (chords, bass, a melody made up fresh for every phrase, drums), played on the
FluidR3 General MIDI orchestra (MIT licence) with fluidsynth, levelled, and cross-faded into the
next. Its sting events (D.sting(t, 'rimshot')) go to OUT_WAV's sibling *_stings.wav, which mix.py
lays over the voice without ducking, so a punchline can land on a drum hit or a sad trombone.
Without mood events the whole video is "playful". Everything is generated, so there is nothing
for a copyright claim to match. Needs fluidsynth, the FluidR3_GM sound font, numpy and soundfile.

Moods: playful, curious, sneaky, suspense, dramatic, triumphant, sad, warm, silence.
Stings: rimshot, wahwah, tada, hit.
"""
import argparse
import json
import math
import os
import subprocess
import tempfile

import numpy as np
import soundfile as sf

SR = 44100
FADE = 1.2  # seconds each side of a mood change
SHORTEST = 3.0  # a mood that would last less than this is folded into the one before
MOODS = ["playful", "curious", "sneaky", "suspense", "dramatic", "triumphant", "sad", "warm", "silence"]
STINGS = ["rimshot", "wahwah", "tada", "hit"]

# ---- a minimal MIDI file writer ------------------------------------------------------------------


def vlq(n):
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append(0x80 | (n & 0x7F))
        n >>= 7
    return bytes(reversed(out))


class Midi:
    TPB = 480

    def __init__(self, bpm):
        self.bpm = bpm
        self.events = [(0, 0, b"\xff\x51\x03" + int(60e6 / bpm).to_bytes(3, "big"))]

    def program(self, ch, prog, volume=100):
        self.events += [(0, 1, bytes([0xC0 | ch, prog])), (0, 1, bytes([0xB0 | ch, 7, volume]))]

    def note(self, ch, beat, dur, pitch, vel):
        if not 0 <= pitch < 128 or dur <= 0:
            return
        on, off = int(beat * self.TPB), int((beat + dur) * self.TPB)
        self.events.append((on, 3, bytes([0x90 | ch, pitch, max(1, min(127, int(vel)))])))
        self.events.append((off, 2, bytes([0x80 | ch, pitch, 0])))

    def write(self, path):
        data, last = b"", 0
        for tick, _, msg in sorted(self.events, key=lambda e: (e[0], e[1])):
            data += vlq(tick - last) + msg
            last = tick
        data += b"\x00\xff\x2f\x00"
        head = b"MThd" + (6).to_bytes(4, "big") + (0).to_bytes(2, "big") + (1).to_bytes(2, "big") + self.TPB.to_bytes(2, "big")
        open(path, "wb").write(head + b"MTrk" + len(data).to_bytes(4, "big") + data)


# ---- harmony -------------------------------------------------------------------------------------

QUALITY = {"maj": [0, 4, 7], "min": [0, 3, 7], "dim": [0, 3, 6], "7": [0, 4, 7, 10], "m7": [0, 3, 7, 10]}
SCALE = {"major": [0, 2, 4, 5, 7, 9, 11], "minor": [0, 2, 3, 5, 7, 8, 10], "dorian": [0, 2, 3, 5, 7, 9, 10]}
DRUMS = 9
KICK, SNARE, HAT, CRASH, TRIANGLE, WOOD_HI, WOOD_LO, SHAKER, TOM_HI, TOM_LO = 36, 38, 42, 49, 81, 76, 77, 82, 50, 45


def chord(key, root, quality, octave=0):
    return [key + root + 12 * octave + i for i in QUALITY[quality]]


def in_scale(key, scale, lo, hi):
    return [p for p in range(lo, hi + 1) if (p - key) % 12 in SCALE[scale]]


def melody(m, ch, rng, key, scale, prog, bars, lo, hi, vel, rhythms, staccato=1.0):
    """A tune: one rhythm motif per four-bar phrase, notes walking between chord tones, each
    phrase ending on the chord's root."""
    notes = in_scale(key, scale, lo, hi)
    pitch = notes[len(notes) // 2]
    for phrase in range(0, bars, 4):
        motif = rhythms[rng.integers(len(rhythms))]
        for b in range(phrase, min(phrase + 4, bars)):
            root, quality = prog[b % len(prog)]
            tones = [p for p in notes if (p - key - root) % 12 in [i % 12 for i in QUALITY[quality]]]
            last_bar = b % 4 == 3
            for k, (beat, dur) in enumerate(motif if not last_bar else [(0, 3)]):
                if last_bar:
                    target = min((p for p in tones if (p - key - root) % 12 == 0), key=lambda p: abs(p - pitch), default=pitch)
                else:
                    pool = tones if k == 0 or rng.random() < 0.6 else notes
                    near = sorted(pool, key=lambda p: abs(p - pitch))[:4]
                    target = near[rng.integers(len(near))]
                pitch = target
                m.note(ch, b * 4 + beat, dur * staccato, pitch, vel + rng.integers(-8, 8))


# ---- moods ---------------------------------------------------------------------------------------
# Each composes `bars` bars into m with its own instruments (General MIDI programs).


def playful(m, bars, rng):
    key, prog = 60, [(0, "maj"), (9, "min"), (5, "maj"), (7, "maj"), (0, "maj"), (9, "min"), (2, "min"), (7, "7")]
    for ch, p, v in ((0, 45, 100), (1, 70, 110), (2, 12, 80)):  # pizzicato, bassoon, marimba
        m.program(ch, p, v)
    for b in range(bars):
        root, q = prog[b % 8]
        c = chord(key, root, q, -1)
        m.note(0, b * 4, 0.4, c[0] - 12, 90)
        m.note(0, b * 4 + 2, 0.4, c[2] - 12, 80)
        for off in (0.5, 1.5, 2.5, 3.5):
            for p in chord(key, root, q, 1)[:3]:
                m.note(2, b * 4 + off, 0.2, p, 45)
        m.note(DRUMS, b * 4, 0.1, WOOD_LO, 55)
        m.note(DRUMS, b * 4 + 2, 0.1, WOOD_HI, 50)
    melody(m, 1, rng, key, "major", prog, bars, 48, 67, 78,
           [[(0, .5), (.5, .5), (1, .5), (2, .5), (2.5, .5), (3, 1)], [(0, 1), (1, .5), (1.5, .5), (2, 1), (3, .5)],
            [(0, .5), (1, .5), (1.5, .5), (2, .5), (3, .5), (3.5, .5)]], staccato=0.6)
    return 112


def curious(m, bars, rng):
    key, prog = 62, [(0, "min"), (10, "maj"), (5, "maj"), (0, "min")]
    for ch, p, v in ((0, 45, 90), (1, 73, 95), (2, 8, 85)):  # pizzicato, flute, celesta
        m.program(ch, p, v)
    for b in range(bars):
        root, q = prog[b % 4]
        c = chord(key, root, q, 0)
        m.note(0, b * 4, 1.5, c[0] - 24, 75)
        m.note(0, b * 4 + 2, 1.5, c[2] - 24, 65)
        arp = c + [c[0] + 12, c[1] + 12]
        for i in range(8):
            m.note(2, b * 4 + i * 0.5, 0.45, arp[[0, 1, 2, 3, 4, 3, 2, 1][i]] + 12, 42)
        if b % 2 == 0:
            m.note(DRUMS, b * 4, 0.5, TRIANGLE, 38)
    melody(m, 1, rng, key, "dorian", prog, bars, 69, 86, 62,
           [[(0, 2), (2, 1), (3, 1)], [(0, 1), (1, 3)], [(0, 1.5), (1.5, .5), (2, 2)]])
    return 96


def sneaky(m, bars, rng):
    key, prog = 52, [(0, "min"), (0, "min"), (5, "min"), (7, "7")]
    for ch, p, v in ((0, 45, 105), (1, 71, 100)):  # pizzicato, clarinet
        m.program(ch, p, v)
    for b in range(bars):
        root, q = prog[b % 4]
        nxt = prog[(b + 1) % 4][0]
        walk = [key + root - 12, key + root - 5, key + root - 12, key + nxt - 13]  # tiptoe, with a creep up
        for i, p in enumerate(walk):
            m.note(0, b * 4 + i, 0.35, p, 88 if i % 2 == 0 else 72)
        m.note(DRUMS, b * 4 + 1, 0.1, HAT, 45)
        m.note(DRUMS, b * 4 + 3, 0.1, HAT, 50)
    melody(m, 1, rng, key, "minor", prog, bars, 64, 79, 70,
           [[(0.5, .5), (1, .5), (2.5, .5), (3, .5)], [(0, .5), (.5, .5), (2, .5), (3.5, .5)]], staccato=0.5)
    return 104


def suspense(m, bars, rng):
    key, prog = 57, [(0, "min"), (0, "min"), (-4, "maj"), (-5, "maj")]
    for ch, p, v in ((0, 44, 95), (1, 43, 110), (2, 0, 70), (3, 47, 100)):  # tremolo strings, contrabass, piano, timpani
        m.program(ch, p, v)
    for b in range(bars):
        root, q = prog[b % 4]
        c = chord(key, root, q, -1)
        for p in (c[0], c[2]):
            m.note(0, b * 4, 4, p, 58)
        for beat in (0, 0.75):  # a heartbeat
            m.note(1, b * 4 + beat, 0.4, c[0] - 12, 92)
        m.note(3, b * 4, 0.6, c[0] - 12, 75)
        tick = [key + root + 24, key + root + 25]
        for i in range(8):
            m.note(2, b * 4 + i * 0.5, 0.15, tick[i % 2], 30 + (b % 4) * 4)
    return 84


def dramatic(m, bars, rng):
    key, prog = 62, [(0, "min"), (-4, "maj"), (5, "min"), (7, "maj")]
    for ch, p, v in ((0, 48, 100), (1, 60, 110), (2, 47, 110), (3, 116, 90)):  # strings, horn, timpani, taiko
        m.program(ch, p, v)
    for b in range(bars):
        root, q = prog[b % 4]
        for p in chord(key, root, q, -1):
            m.note(0, b * 4, 4, p, 72)
        m.note(2, b * 4, 0.8, key + root - 24, 100)
        m.note(2, b * 4 + 2, 0.8, key + root - 24, 85)
        for i, accent in enumerate([1, 0, 0, 1, 0, 0, 1, 0]):
            m.note(3, b * 4 + i * 0.5, 0.3, 45, 90 if accent else 55)
        if b % 4 == 0:
            m.note(DRUMS, b * 4, 1, CRASH, 75)
        if b % 4 == 3:
            for i in range(8):  # a timpani roll into the next phrase
                m.note(2, b * 4 + 2 + i * 0.25, 0.25, key + root - 24, 60 + i * 6)
    melody(m, 1, rng, key, "minor", prog, bars, 55, 72, 92,
           [[(0, 2), (2, 1), (3, 1)], [(0, 1.5), (1.5, .5), (2, 2)], [(0, 3), (3, 1)]])
    return 100


def triumphant(m, bars, rng):
    key, prog = 60, [(0, "maj"), (5, "maj"), (7, "maj"), (0, "maj")]
    for ch, p, v in ((0, 48, 95), (1, 61, 115), (2, 47, 105)):  # strings, brass, timpani
        m.program(ch, p, v)
    for b in range(bars):
        root, q = prog[b % 4]
        for p in chord(key, root, q, -1):
            m.note(0, b * 4, 4, p, 70)
        m.note(2, b * 4, 0.8, key + root - 24, 95)
        for beat, v in ((0, 75), (1, 60), (1.5, 55), (2, 70), (3, 60), (3.25, 50), (3.5, 58)):  # a march
            m.note(DRUMS, b * 4 + beat, 0.1, SNARE, v)
        if b % 4 == 0:
            m.note(DRUMS, b * 4, 1, CRASH, 80)
    melody(m, 1, rng, key, "major", prog, bars, 60, 79, 98,
           [[(0, 1.5), (1.5, .5), (2, 2)], [(0, .75), (.75, .25), (1, 1), (2, 2)], [(0, 1), (1, 1), (2, 1), (3, 1)]])
    return 108


def sad(m, bars, rng):
    key, prog = 57, [(0, "min"), (-4, "maj"), (3, "maj"), (-2, "maj")]
    for ch, p, v in ((0, 0, 90), (1, 42, 105), (2, 49, 70)):  # piano, cello, slow strings
        m.program(ch, p, v)
    for b in range(bars):
        root, q = prog[b % 4]
        c = chord(key, root, q, -1)
        arp = [c[0] - 12, c[2] - 12, c[1], c[2], c[0] + 12, c[2], c[1], c[2] - 12]
        for i, p in enumerate(arp):
            m.note(0, b * 4 + i * 0.5, 0.9, p, 50)
        for p in chord(key, root, q, 0):
            m.note(2, b * 4, 4, p, 38)
    melody(m, 1, rng, key, "minor", prog, bars, 48, 64, 72,
           [[(0, 2), (2, 2)], [(0, 3), (3, 1)], [(0, 1), (1, 3)]])
    return 66


def warm(m, bars, rng):
    key, prog = 55, [(0, "maj"), (9, "min"), (5, "maj"), (7, "maj")]
    for ch, p, v in ((0, 24, 100), (1, 73, 90), (2, 49, 60)):  # nylon guitar, flute, slow strings
        m.program(ch, p, v)
    for b in range(bars):
        root, q = prog[b % 4]
        c = chord(key, root, q, 0)
        pick = [c[0] - 12, c[2] - 12, c[1], c[2], c[0] + 12, c[2], c[1], c[2] - 12]
        for i, p in enumerate(pick):
            m.note(0, b * 4 + i * 0.5, 1.0, p, 58 if i % 4 == 0 else 46)
        for p in c:
            m.note(2, b * 4, 4, p + 12, 32)
        for i in range(8):
            m.note(DRUMS, b * 4 + i * 0.5, 0.1, SHAKER, 28 if i % 2 else 36)
    melody(m, 1, rng, key, "major", prog, bars, 67, 84, 60,
           [[(0, 1), (1, 1), (2, 2)], [(0, 2), (2, 1), (3, 1)], [(1, 1), (2, 1), (3, 1)]])
    return 92


def silence(m, bars, rng):
    m.program(0, 0)
    return 90


COMPOSERS = {name: globals()[name] for name in MOODS}


def sting(m, name):
    if name == "rimshot":  # ba-dum-tss
        for beat, notes in ((0, [TOM_HI, KICK]), (0.35, [TOM_LO]), (0.8, [CRASH, KICK, SNARE])):
            for p in notes:
                m.note(DRUMS, beat, 0.3, p, 110)
    elif name == "wahwah":  # the sad trombone
        m.program(0, 57, 120)
        for i, p in enumerate([55, 54, 53]):
            m.note(0, i * 0.6, 0.55, p, 100)
        m.note(0, 1.8, 2.0, 52, 100)
    elif name == "tada":
        m.program(0, 61, 120)
        for p in (60, 64, 67, 72):
            m.note(0, 0, 0.25, p, 105)
            m.note(0, 0.33, 1.6, p, 115)
        m.note(DRUMS, 0.33, 1, CRASH, 100)
    elif name == "hit":
        m.program(0, 55, 120)
        m.program(1, 47, 120)
        for p in (50, 57, 62):
            m.note(0, 0, 1.0, p, 115)
        m.note(1, 0, 1.0, 38, 120)
        m.note(DRUMS, 0, 1, CRASH, 110)


# ---- rendering -----------------------------------------------------------------------------------


def play(m, path, sf2, tmp):
    mid = os.path.join(tmp, "x.mid")
    m.write(mid)
    subprocess.run(["fluidsynth", "-ni", "-q", "-g", "0.7", "-r", str(SR), "-F", path, sf2, mid],
                   check=True, capture_output=True)
    audio, sr = sf.read(path, always_2d=True)
    assert sr == SR, sr
    return audio


def level(audio, rms_db=-20.0):
    loud = np.abs(audio).max(axis=1) > 1e-3
    if not loud.any():
        return audio
    rms = np.sqrt((audio[loud] ** 2).mean())
    return audio * (10 ** (rms_db / 20) / max(rms, 1e-9))


def stretches(events, seconds):
    """[(start, end, mood)]: mood changes, a too-short mood folded into the one before."""
    cues = [(e["t"], e["mood"]) for e in events if e["kind"] == "mood"]
    if not cues or cues[0][0] > 0.01:
        cues.insert(0, (0.0, cues[0][1] if cues else "playful"))
    out = []
    for i, (t, mood) in enumerate(cues):
        end = cues[i + 1][0] if i + 1 < len(cues) else seconds
        if out and (end - t < SHORTEST or out[-1][2] == mood):
            out[-1] = (out[-1][0], end, out[-1][2])
        else:
            out.append((t, end, mood))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("seconds", type=float)
    ap.add_argument("--events")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--sf2", default="/usr/share/sounds/sf2/FluidR3_GM.sf2")
    a = ap.parse_args()
    events = json.load(open(a.events)) if a.events else []
    unknown = {e.get("mood") for e in events if e["kind"] == "mood"} - set(MOODS)
    unknown |= {e.get("name") for e in events if e["kind"] == "sting"} - set(STINGS)
    if unknown:
        raise SystemExit(f"unknown moods or stings: {sorted(unknown)}; use {MOODS} and {STINGS}")
    n = int((a.seconds + 1) * SR)
    music = np.zeros((n, 2))
    with tempfile.TemporaryDirectory() as tmp:
        for k, (t0, t1, mood) in enumerate(stretches(events, a.seconds)):
            start = max(0.0, t0 - FADE)
            stop = min(a.seconds + 1, t1 + FADE)
            m = Midi(100)
            bpm = COMPOSERS[mood](m, 1, np.random.default_rng(0))  # find the tempo
            bars = math.ceil((stop - start) / (240 / bpm)) + 1
            m = Midi(bpm)
            COMPOSERS[mood](m, bars, np.random.default_rng(a.seed * 100 + k))
            piece = level(play(m, os.path.join(tmp, f"{k}.wav"), a.sf2, tmp)) if mood != "silence" else np.zeros((1, 2))
            piece = np.pad(piece, ((0, max(0, int((stop - start) * SR) - len(piece))), (0, 0)))[: int((stop - start) * SR)]
            env = np.ones(len(piece))
            if t0 > 0:  # fade in across the change, equal power
                f = min(len(env), int(2 * FADE * SR) if t0 >= FADE else int(t0 * 2 * SR))
                env[:f] = np.sin(np.linspace(0, np.pi / 2, f))
            if t1 < a.seconds:
                f = min(len(env), int(2 * FADE * SR))
                env[-f:] *= np.cos(np.linspace(0, np.pi / 2, f))
            i = int(start * SR)
            music[i:i + len(piece)] += piece[: n - i] * env[: n - i, None]
            print(f"  {t0:6.1f}-{t1:6.1f}s {mood} at {bpm} bpm", flush=True)
        music /= max(1.0, np.abs(music).max() / 0.9)
        sf.write(a.out, music, SR)
        hits = [e for e in events if e["kind"] == "sting"]
        if hits:
            track = np.zeros((n, 2))
            for e in hits:
                m = Midi(120)
                sting(m, e["name"])
                s = level(play(m, os.path.join(tmp, "sting.wav"), a.sf2, tmp), -18.0)
                s /= max(1.0, np.abs(s).max() / 0.9)  # each sting as loud as the others, without clipping
                i = int(e["t"] * SR)
                track[i:i + len(s)] += s[: max(0, n - i)]
            track = np.clip(track, -0.95, 0.95)
            sf.write(os.path.splitext(a.out)[0] + "_stings.wav", track, SR)
    print(f"wrote {a.out}" + (" and its stings" if hits else ""))


if __name__ == "__main__":
    main()
