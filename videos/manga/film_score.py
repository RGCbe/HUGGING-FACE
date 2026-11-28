"""A film score and scene ambience for a movie-version episode, made with ElevenLabs (Eleven Music for the score,
sound generation for the background sound; both licensed for commercial use on the paid plan).

    python3 film_score.py SHOTS.json [--only-ambience] [--only-score]

Writes EPISODE/out/score/score.wav (music cues placed at their shots, cross-faded, silent where the story wants
silence) and EPISODE/out/score/ambience.wav (one looping background bed per scene, kept low). edit.py uses them when
they exist: the score replaces the synthesized music (the stings stay), the ambience goes under the effects.
Each cue and bed is cached in out/score/parts/ by its prompt and length, so a rerun only makes what changed.
The key is ELEVENLABS_API_KEY from the environment; it is never printed.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100
# cue: the shot it starts at -> what it sounds like (None = silence, the story wants the music gone there)
CUES = {
    "S01": "Dark cinematic suspense, low tremolo strings, deep pulsing synth bass, ominous build in a cave, ending on a huge impact hit",
    "S03": "Epic heroic main title theme, full orchestra and choir, big taiko drums, a soaring Indian bansuri flute melody, blockbuster opening",
    "S05": "Wide aerial cinematic theme over a city at dusk, hopeful and mysterious, warm strings, soft choir, light tabla, sense of wonder",
    "S08": "Warm playful Indian street-life underscore, tabla, sitar and light pizzicato strings, charming and gently comedic",
    "S13": "Cocky swaggering hero entrance music, punchy brass and drums with tabla, confident and fun",
    "S15": "Light sneaky comedic underscore, plucked strings, soft bassoon and tabla, teasing and playful",
    "S24": None,
    "S25": "Mysterious magical portal atmosphere, low drones, shimmering harp and celesta, quiet suspense",
    "S27": "Intense action horror music, pounding drums, aggressive low brass, fast strings, monsters attacking",
    "S31": "Rising power-up build, heartbeat drums, swelling strings and choir, golden light awakening, about to explode",
    "S33": "Triumphant heroic action anthem, full orchestra and choir, fast drums, an unstoppable hero montage",
    "S39": "Dark epic boss battle music, heavy drums, deep male choir, menacing brass",
    "S42": None,
    "S45": "Frantic comedic chase music, fast strings and brass stabs, panicked cartoonish urgency",
    "S47": "Sad comedic aftermath, a slow solo cello, defeated but a little funny",
    "S49": None,
    "S51": "Light cheeky pizzicato strings and tabla, playful",
    "S53": "Warm gentle night theme, soft bansuri flute over strings, hopeful with a little mystery",
    "S55": "Dark ominous low drones and distant choir, something ancient awakens",
    "S56": "Short epic cliffhanger ending hit into the main theme, orchestra and choir",
}
# scene number -> its background sound
AMBIENCE = {
    1: "eerie stone cave ambience, distant water drips, torches crackling, low rumble, no music",
    2: "wind high above a big coastal city at dusk, distant traffic hum, faint sea waves, no music",
    3: "busy Indian street market at evening, crowd chatter, distant scooters and horns, vendors calling, no music",
    4: "small Indian street tea stall at evening, chai bubbling, glasses clinking, light crowd chatter, distant traffic, no music",
    5: "excited crowd murmuring on a busy Indian street at evening, distant horns, footsteps, no music",
    6: "deep humming magical portal, swirling wind, low energy drone, no music",
    7: "huge dark cave ambience, deep echoes, water drips, distant growls, no music",
    8: "dark dungeon tunnel ambience, echoing drips, distant rumble, no music",
    9: "huge stone throne room, crackling fire braziers, deep rumble, ominous, no music",
    10: "Indian city square at night, distant traffic, crickets, quiet voices, no music",
    11: "small tea stall at night, kettle simmering, crickets, distant dog barking, light traffic, no music",
    12: "empty city square late at night, soft wind, distant traffic, crickets, no music",
    13: "low magical portal hum at night, soft wind, eerie, no music",
}


def key():
    return os.environ.get("ELEVENLABS_API_KEY", "").strip() or sys.exit("ELEVENLABS_API_KEY is not set")


def post(url, body, timeout=300):
    for k in range(4):
        req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                     headers={"xi-api-key": key(), "Content-Type": "application/json"})
        try:
            return urllib.request.urlopen(req, timeout=timeout).read()
        except urllib.error.HTTPError as e:
            msg = e.read()[:300].decode("utf-8", "replace")
            if e.code in (429, 500, 502, 503) and k < 3:
                time.sleep(10 * (k + 1))
                continue
            raise RuntimeError(f"ElevenLabs {e.code}: {msg}") from None


def cached(kind, prompt, seconds, make):
    parts = os.path.join(BASE, "out", "score", "parts")
    os.makedirs(parts, exist_ok=True)
    h = hashlib.sha1(f"{kind}|{prompt}|{seconds:.1f}".encode()).hexdigest()[:12]
    path = os.path.join(parts, f"{kind}_{h}.mp3")
    if not os.path.exists(path):
        open(path, "wb").write(make())
        print(f"  made {kind} {seconds:.1f}s: {prompt[:70]}", flush=True)
    return path


def load(path):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def write(path, a):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", "-", path],
                   input=a.astype(np.float32).tobytes(), check=True)


def fades(x, fin, fout):
    fin, fout = min(len(x), int(fin * SR)), min(len(x), int(fout * SR))
    if fin:
        x[:fin] *= np.linspace(0, 1, fin)[:, None]
    if fout:
        x[len(x) - fout:] *= np.linspace(1, 0, fout)[:, None]
    return x


def rms_to(x, db):
    r = np.sqrt(np.mean(x ** 2)) + 1e-9
    return x * (10 ** (db / 20) / r)


def main():
    global BASE
    ap = argparse.ArgumentParser()
    ap.add_argument("shots")
    ap.add_argument("--only-score", action="store_true")
    ap.add_argument("--only-ambience", action="store_true")
    a = ap.parse_args()
    BASE = os.path.dirname(os.path.abspath(a.shots))
    sys.path.insert(0, HERE)
    import edit  # noqa: E402  (the same shot timing as the edit)
    timeline, total = edit.plan(json.load(open(a.shots))["shots"], BASE)
    by = {s["id"]: s for s in timeline}
    n = int(total * SR) + SR
    out_dir = os.path.join(BASE, "out", "score")
    if not a.only_ambience:
        score = np.zeros((n, 2), np.float32)
        starts = sorted((by[k]["start"], k) for k in CUES)
        for i, (t0, k) in enumerate(starts):
            t1 = starts[i + 1][0] if i + 1 < len(starts) else total
            prompt = CUES[k]
            if not prompt:
                continue
            span = t1 - t0
            length = max(10.0, span + 1.5)  # a little longer, for the cross-fade into the next cue
            path = cached("cue", prompt, length, lambda: post(
                "https://api.elevenlabs.io/v1/music",
                {"prompt": prompt + ", instrumental, no vocals", "music_length_ms": int(length * 1000)}))
            x = load(path)[: int((span + 1.0) * SR)]
            x = rms_to(fades(x, 0.4, 1.0), -18)
            j = int(t0 * SR)
            score[j:j + len(x)] += x[: n - j]
        write(os.path.join(out_dir, "score.wav"), score)
        print(f"score.wav: {total:.1f}s, {sum(1 for v in CUES.values() if v)} cues")
    if not a.only_score:
        amb = np.zeros((n, 2), np.float32)
        scenes = {}
        for s in timeline:
            sc = s.get("scene")
            if sc in AMBIENCE:
                lo, hi = scenes.get(sc, (s["start"], s["start"] + s["dur"]))
                scenes[sc] = (min(lo, s["start"]), max(hi, s["start"] + s["dur"]))
        for sc, (t0, t1) in sorted(scenes.items(), key=lambda kv: kv[1][0]):
            text = AMBIENCE[sc]
            path = cached("amb", text, 20.0, lambda: post(
                "https://api.elevenlabs.io/v1/sound-generation",
                {"text": text, "duration_seconds": 20.0, "prompt_influence": 0.4}))
            bed = load(path)
            need = int((t1 - t0 + 0.6) * SR)
            reps = []  # loop the bed with a short cross-fade until it covers the scene
            while sum(len(r) for r in reps) < need:
                reps.append(fades(bed.copy(), 0.5, 0.5))
            x = np.concatenate(reps)[:need]
            x = rms_to(fades(x, 0.6, 0.8), -33)
            j = int(t0 * SR)
            amb[j:j + len(x)] += x[: n - j]
        write(os.path.join(out_dir, "ambience.wav"), amb)
        print(f"ambience.wav: {len(scenes)} scenes")


if __name__ == "__main__":
    main()
