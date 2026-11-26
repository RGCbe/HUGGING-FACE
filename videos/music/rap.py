"""Crystal-clear vocals on a beat: the owner's ElevenLabs voice raps and shouts each line, and a gang of him answers,
every line placed on its bar. For songs where re-voicing an AI singer blurs the words (25 Nov 2026: the converted
Tamil rap was not understandable).

    python3 rap.py PLAN.json           # WORK/vocals_lead.wav, WORK/vocals_gang.wav, WORK/rap_mix.wav and .mp3

PLAN.json:
    {"work": "~/.cache/music/SLUG", "instrumental": "take_202.band.wav", "bpm": 100, "first_beat": 0.12,
     "lines": [{"bar": 0, "bars": 2, "who": "lead", "tag": "excited", "text": "..."},
               {"bar": 1.5, "bars": 0.5, "who": "gang", "text": "..."}, ...]}
    who: "lead" (the owner), "gang" (four other takes of the owner), "all" (both together).
    sing: true = sung, not spoken: the owner's voice asked to sing, then tuned to the plan's "notes" (the beat's key).  bar: where the line starts (0 = first_beat);
    bars: the room it has (a line that is longer is sped up, at most 1.35x, never pitched).

Where data goes: the line texts go only to ElevenLabs' own API with its key; everything else stays on this machine.
"""
import hashlib
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kural"))
import eleven  # noqa: E402

SR = 44100
# the gang is the owner too (26 Nov 2026: "use my voice only"): other takes of his clone, each a little higher or
# lower, so it sounds like a crowd of him
GANG_TAKES = [(11, 0.0), (12, -1.5), (13, 1.2), (14, -0.7)]  # (seed, semitones)


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *args], check=True)


def load(path, mono=True):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1" if mono else "2",
                          "-ar", str(SR), "-"], check=True, capture_output=True).stdout
    a = np.frombuffer(raw, np.float32).copy()
    return a if mono else a.reshape(-1, 2)


def trim(a, thr=0.02):
    """Cut the silence before and after a spoken line, so it lands exactly on its beat."""
    env = np.convolve(np.abs(a), np.ones(441) / 441, mode="same")
    on = np.where(env > thr * env.max())[0]
    if not len(on):
        return a
    return a[max(0, on[0] - SR // 50): on[-1] + SR // 20]


class Voices:
    def __init__(self, cache):
        self.key = eleven.api_key()
        self.cache = cache
        cfg = json.load(open(os.path.join(HERE, "..", "teabreak", "config.json")))["eleven"]
        self.lead = (eleven.voice_id(cfg["voice"], self.key), cfg["stability"], cfg["similarity"], cfg["model"])

    def say(self, voice, text, tag, seed):
        vid, stab, sim, model = voice
        words = f"[{tag}] {text}" if tag else text
        h = hashlib.sha1(f"{vid}|{words}|{seed}|{stab}|{sim}|{model}".encode()).hexdigest()[:16]
        path = os.path.join(self.cache, f"tts_{h}.wav")
        if not os.path.exists(path):
            pcm = eleven.call(f"/text-to-speech/{vid}?output_format=pcm_24000", self.key,
                              {"text": words, "model_id": model, "seed": seed,
                               "voice_settings": {"stability": stab, "similarity_boost": sim}})
            raw = path + ".raw"
            with open(raw, "wb") as f:
                f.write(pcm)
            ffmpeg("-f", "s16le", "-ar", "24000", "-ac", "1", "-i", raw, "-ar", str(SR), path)
            os.remove(raw)
        return trim(load(path))


def pitch(a, semitones):
    """Shift the pitch without changing the length (rubberband), for the gang's doubles."""
    if not semitones:
        return a
    import tempfile
    d = tempfile.mkdtemp()
    i, o = os.path.join(d, "in.wav"), os.path.join(d, "out.wav")
    sf.write(i, a, SR)
    ffmpeg("-i", i, "-af", f"rubberband=pitch={2 ** (semitones / 12):.5f}:formant=preserved", o)
    out = load(o)
    os.remove(i)
    os.remove(o)
    os.rmdir(d)
    return out


NOTE = {n: i for i, n in enumerate("C C# D D# E F F# G G# A A# B".split())}


def autotune(a, notes):
    """Sing in the beat's key: the whole line moves to the key, then every held note (>= 90 ms of steady pitch) is
    pulled to the nearest allowed note (rubberband, formants kept). Glides and consonants are left alone, so the
    words stay as clear as they were."""
    import librosa
    pcs = sorted(NOTE[n] for n in notes)
    hop = 256
    y = librosa.resample(a, orig_sr=SR, target_sr=16000)
    f0, voiced, _ = librosa.pyin(y, fmin=70, fmax=700, sr=16000, frame_length=1024, hop_length=hop)
    midi = librosa.hz_to_midi(np.where(voiced, f0, np.nan))
    # held notes: runs of steady pitch
    runs, start = [], None
    for i in range(len(midi)):
        steady = voiced[i] and i > 0 and voiced[i - 1] and abs(midi[i] - midi[i - 1]) < 0.4
        if steady and start is None:
            start = i - 1
        if (not steady or i == len(midi) - 1) and start is not None:
            if (i - start) * hop / 16000 >= 0.09:
                runs.append((start, i, float(np.nanmedian(midi[start:i]))))
            start = None
    if not runs:
        return a

    def dist(m):
        d = [(m - p) % 12 for p in pcs]
        return min(min(x, 12 - x) for x in d)
    # the whole line moves by the semitones that need the least pulling
    shift = min(range(-6, 6), key=lambda k: sum(dist(m + k) * (e - s0) for s0, e, m in runs))
    out = pitch(a, shift) if shift else a.copy()
    for s0, e, m in runs:
        m = m + shift
        target = min((round(m) + k for k in range(-6, 7) if (round(m) + k) % 12 in pcs), key=lambda t: abs(t - m))
        semis = target - m
        if abs(semis) < 0.15:
            continue
        i0, i1 = int(s0 * hop / 16000 * SR), int(e * hop / 16000 * SR)
        seg = out[i0:i1]
        if len(seg) < SR // 20:
            continue
        moved = pitch(seg, semis)[:len(seg)]
        x = min(len(seg) // 4, SR // 100)  # 10 ms cross-fades
        ramp = np.ones(len(moved), np.float32)
        ramp[:x] = np.linspace(0, 1, x)
        ramp[len(moved) - x:] = np.linspace(1, 0, x)
        out[i0:i0 + len(moved)] = seg[:len(moved)] * (1 - ramp) + moved * ramp
    return out


def fit(a, seconds, most=1.35):
    """Speed a line up (pitch kept) when it is longer than its room."""
    if len(a) <= seconds * SR * 0.97:
        return a
    factor = min(most, len(a) / (seconds * SR * 0.97))
    import tempfile
    d = tempfile.mkdtemp()
    tmp_in, tmp_out = os.path.join(d, "in.wav"), os.path.join(d, "out.wav")
    sf.write(tmp_in, a, SR)
    ffmpeg("-i", tmp_in, "-af", f"atempo={factor:.4f}", tmp_out)
    out = load(tmp_out)
    os.remove(tmp_in)
    os.remove(tmp_out)
    os.rmdir(d)
    return out


def place(track, a, at, gain=1.0):
    i = int(at * SR)
    if i >= len(track):
        return
    n = min(len(a), len(track) - i)
    track[i:i + n] += a[:n] * gain


def main():
    plan = json.load(open(sys.argv[1]))
    work = os.path.expanduser(plan["work"])
    beat = os.path.join(work, plan["instrumental"])
    band = load(beat, mono=False)
    bar = 60.0 / plan["bpm"] * 4
    v = Voices(work)
    lead = np.zeros(len(band), np.float32)
    gang = np.zeros((len(band), 2), np.float32)
    rng = np.random.default_rng(7)
    pans = [(1.0, 0.55), (0.55, 1.0), (0.85, 0.7), (0.7, 0.85)]
    for n, line in enumerate(plan["lines"]):
        at = plan["first_beat"] + line["bar"] * bar
        room = line.get("bars", 1) * bar
        who, tag = line.get("who", "lead"), line.get("tag", "")
        if line.get("sing"):
            # sung: the owner's voice asked to sing, then tuned to the beat's key; an "all" line is doubled from the
            # same take (two delayed copies left and right and one an octave down), so it stays one melody
            a = fit(autotune(v.say(v.lead, "\u266a " + line["text"] + " \u266a", tag or "singing melodically",
                                   seed=line.get("seed", 7)), plan.get("notes", ["E", "F#", "G", "A", "B", "C", "D"])),
                    room)
            place(lead, a, at)
            if who == "all":
                for delay, semis, gl, gr in ((0.022, 0, 0.55, 0.15), (0.037, 0, 0.15, 0.55), (0.0, -12, 0.3, 0.3)):
                    d2 = pitch(a, semis)
                    place(gang[:, 0], d2, at + delay, gl)
                    place(gang[:, 1], d2, at + delay, gr)
            print(f"{n + 1:2d}. bar {line['bar']:>5} {who:4s} sung  {line['text']}", flush=True)
            continue
        if who in ("lead", "all"):
            a = fit(v.say(v.lead, line["text"], tag or "excited", seed=line.get("seed", 7)), room)
            place(lead, a, at)
        if who in ("gang", "all"):
            for k, (seed, semi) in enumerate(GANG_TAKES):
                a = fit(pitch(v.say(v.lead, line["text"], "shouting", seed=seed), semi), room)
                off = at + rng.uniform(0, 0.03)
                place(gang[:, 0], a, off, 0.8 * pans[k][0])
                place(gang[:, 1], a, off, 0.8 * pans[k][1])
        print(f"{n + 1:2d}. bar {line['bar']:>5} {who:4s} {line['text']}", flush=True)
    sf.write(os.path.join(work, "vocals_lead_dry.wav"), lead, SR)
    sf.write(os.path.join(work, "vocals_gang_dry.wav"), gang, SR)
    # a voice that cuts through: low cut, steady level, a little room; the gang wider and further back
    ffmpeg("-i", os.path.join(work, "vocals_lead_dry.wav"), "-af",
           "highpass=f=90,acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2,"
           "equalizer=f=3000:t=q:w=1:g=2,aecho=0.8:0.5:40:0.12", os.path.join(work, "vocals_lead.wav"))
    ffmpeg("-i", os.path.join(work, "vocals_gang_dry.wav"), "-af",
           "highpass=f=150,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,aecho=0.8:0.7:60|120:0.3|0.2",
           os.path.join(work, "vocals_gang.wav"))
    ld, gg = load(os.path.join(work, "vocals_lead.wav")), load(os.path.join(work, "vocals_gang.wav"), mono=False)
    n = min(len(band), len(ld), len(gg))
    band, ld, gg = band[:n], ld[:n], gg[:n]
    # the beat dips 4 dB while a voice is on, so every word is heard
    env = np.convolve(np.abs(ld) + np.abs(gg).mean(1), np.ones(SR // 10) / (SR // 10), mode="same")
    on = np.clip(env / (0.15 * env.max() + 1e-9), 0, 1)
    duck = 1 - 0.37 * np.convolve(on, np.ones(SR // 5) / (SR // 5), mode="same")
    lvl = lambda x: np.sqrt(np.mean(x ** 2)) + 1e-9  # noqa: E731
    ld = ld * (lvl(band) * 1.5 / lvl(ld[np.abs(ld) > 1e-4]) if (np.abs(ld) > 1e-4).any() else 1)
    gg = gg * (lvl(band) * 1.1 / lvl(gg[np.abs(gg) > 1e-4]) if (np.abs(gg) > 1e-4).any() else 1)
    mix = band * duck[:, None] + ld[:, None] + gg
    pre = os.path.join(work, "rap_mix.premaster.wav")
    sf.write(pre, (mix / max(1.0, np.abs(mix).max() / 0.95)).astype(np.float32), SR)
    sys.path.insert(0, HERE)
    import song
    song.master(pre, os.path.join(work, "rap_mix.wav"))
    os.remove(pre)
    ffmpeg("-i", os.path.join(work, "rap_mix.wav"), "-b:a", "256k", os.path.join(work, "rap_mix.mp3"))
    print("mixed:", os.path.join(work, "rap_mix.mp3"))


if __name__ == "__main__":
    main()
