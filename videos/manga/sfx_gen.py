"""Sound effects for a movie-version episode, made to order with ElevenLabs sound generation (licensed for commercial
use on the paid plan): one effect per shot, from the shot's "sfx" note and where the scene happens.

    python3 sfx_gen.py SHOTS.json OUT_DIR [--only S07,S27]

Each shot with an "sfx" note gets OUT_DIR/SNN.mp3, as long as the shot. A file that exists is kept (delete it to
make it again). The key is ELEVENLABS_API_KEY from the environment; it is never printed. Not in git.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

PLACE = {
    1: "inside a dark stone cave", 7: "inside a huge dark cave", 8: "in a dark dungeon tunnel", 9: "in a huge stone throne room with fire",
    2: "over a big city at dusk", 3: "in a busy Indian street market at evening", 4: "at a small street tea stall in an Indian city at evening",
    5: "in a busy Indian street at evening", 6: "at a glowing magic portal", 10: "in an Indian city square at night",
    11: "at a small street tea stall at night", 12: "in an empty city square late at night", 13: "under a glowing portal at night",
}
# the shot's note -> what to ask for (clearer words for the sound model); anything else is used as written
CLEAR = {
    "UI blip": "a short clean digital interface blip, like a game menu",
    "title sting": "an epic cinematic movie title hit: a deep boom with a rising shimmer",
    "end sting": "a short dramatic cinematic ending hit with a low boom and a fading echo",
    "clock tick": "a single loud clock tick, then a soft whoosh",
    "alarm beep": "a digital alarm beeping three times, urgent",
    "music drops out": "a soft low wind and the quiet hum of a city at night",
    "one beat of silence": "very quiet night ambience with a faint steam hiss",
}


def generate(text, seconds, key):
    body = json.dumps({"text": text, "duration_seconds": max(0.6, min(22.0, seconds)), "prompt_influence": 0.45}).encode()
    for k in range(4):
        req = urllib.request.Request("https://api.elevenlabs.io/v1/sound-generation", data=body, method="POST",
                                     headers={"xi-api-key": key, "Content-Type": "application/json"})
        try:
            return urllib.request.urlopen(req, timeout=180).read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and k < 3:
                time.sleep(5 * (k + 1))
                continue
            sys.exit(f"ElevenLabs sound generation: HTTP {e.code} {e.read()[:300].decode('utf-8', 'replace')}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shots")
    ap.add_argument("out_dir")
    ap.add_argument("--only")
    a = ap.parse_args()
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip() or sys.exit("ELEVENLABS_API_KEY is not set")
    os.makedirs(a.out_dir, exist_ok=True)
    only = set(a.only.split(",")) if a.only else None
    for s in json.load(open(a.shots))["shots"]:
        note = (s.get("sfx") or "").strip()
        out = os.path.join(a.out_dir, f"{s['id']}.mp3")
        if not note or (only and s["id"] not in only) or (os.path.exists(out) and not only):
            continue
        text = CLEAR.get(note) or f"{note}, {PLACE.get(s['scene'], '')}, realistic cinematic movie sound effect, no music, no speech"
        open(out, "wb").write(generate(text, s["seconds"] + 0.5, key))
        print(f"{s['id']}: {text[:90]}", flush=True)


if __name__ == "__main__":
    main()
