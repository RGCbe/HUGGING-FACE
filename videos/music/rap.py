"""Crystal-clear vocals on a beat: the owner's ElevenLabs voice raps and shouts each line, and a gang of voices answers,
every line placed on its bar. For songs where re-voicing an AI singer blurs the words (25 Nov 2026: the converted
Tamil rap was not understandable).

    python3 rap.py PLAN.json           # WORK/vocals_lead.wav, WORK/vocals_gang.wav, WORK/rap_mix.wav and .mp3

PLAN.json:
    {"work": "~/.cache/music/SLUG", "instrumental": "take_202.band.wav", "bpm": 100, "first_beat": 0.12,
     "lines": [{"bar": 0, "bars": 2, "who": "lead", "tag": "excited", "text": "..."},
               {"bar": 1.5, "bars": 0.5, "who": "gang", "text": "..."}, ...]}
    who: "lead" (the owner), "gang" (the gang), "all" (both together).  bar: where the line starts (0 = first_beat);
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
GANG = ["Manav - Friendly, Calm and Natural", "Viraj - Deep, Resonant and Lyrical", "Bunty - Warm and Clear"]


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
        self.gang = [(eleven.voice_id(n, self.key), 0.35, 0.8, cfg["model"]) for n in GANG]

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
        if who in ("lead", "all"):
            a = fit(v.say(v.lead, line["text"], tag or "excited", seed=line.get("seed", 7)), room)
            place(lead, a, at)
        if who in ("gang", "all"):
            for k, voice in enumerate(v.gang + [v.lead]):  # the owner shouts with the gang too
                a = fit(v.say(voice, line["text"], "shouting", seed=11 + k), room)
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
