"""Voice pieces in the owner's own ElevenLabs voice clone ("Manoj kumar T"), acted from the script's
emotion tags: "[funny] Rank F. That's the floor." is sent as "[playful] Rank F. That's the floor.", an
audio tag Eleven v3/v4 performs, not says (the listening test, check.py, catches it if it ever is said).

    python3 eleven.py PIECES_FILE OUT_DIR --sections 1,3 [--seed 7] [--voice "Manoj kumar T"]
                      [--model eleven_v4] [--stability 0.35] [--similarity 0.85]

PIECES_FILE has one piece per line (build.py's pieces.txt); piece N becomes OUT_DIR/sec_NN.wav, 24 kHz
mono, like tts.py. --seed picks another take of the same words (build.py tries other seeds when a piece
fails the listening test). Standard library only.

The key is ELEVENLABS_API_KEY from the environment (the cloud environment's settings), or else the
git-ignored .env.local at the repo root that `elevenlabs onboard` writes. It is never printed.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import wave

API = "https://api.elevenlabs.io/v1"
# the script's emotion tags (SCRIPT_STYLE.md) as the audio tags Eleven v3/v4 act on
TAGS = {"excited": "[excited]", "funny": "[playful]", "mysterious": "[mysterious]", "shocked": "[surprised]",
        "serious": "[serious]", "warm": "[warmly]", "sad": "[sad]", "curious": "[curious]"}
TAG = re.compile(r"^\[([a-z]+)\]\s*")


def api_key():
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        local = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env.local")
        if os.path.exists(local):
            for line in open(local):
                name, _, value = line.strip().partition("=")
                if name.strip() == "ELEVENLABS_API_KEY":
                    key = value.strip().strip('"').strip("'")
    if not key:
        sys.exit("ELEVENLABS_API_KEY is not set: add it in the cloud environment's settings (a new session picks it "
                 "up) or after ELEVENLABS_API_KEY= in .env.local. Never paste it into the chat.")
    return key


def call(path, key, body=None, tries=5):
    for k in range(tries):
        req = urllib.request.Request(API + path, data=None if body is None else json.dumps(body).encode(),
                                     headers={"xi-api-key": key, "Content-Type": "application/json"},
                                     method="GET" if body is None else "POST")
        try:
            return urllib.request.urlopen(req, timeout=180).read()
        except urllib.error.HTTPError as e:
            detail = e.read()[:300].decode("utf-8", "replace")
            if e.code in (429, 500, 502, 503, 504) and k < tries - 1:
                time.sleep(2 ** k * 3)
                continue
            raise SystemExit(f"ElevenLabs {path.split('?')[0]}: HTTP {e.code} {detail}")
        except urllib.error.URLError:
            if k < tries - 1:
                time.sleep(2 ** k * 3)
                continue
            raise


def voice_id(name, key):
    voices = json.loads(call("/voices", key))["voices"]
    for v in voices:
        if v["name"].strip().lower() == name.strip().lower() or v["voice_id"] == name:
            return v["voice_id"]
    sys.exit(f"no voice named {name!r} in this ElevenLabs account: {[v['name'] for v in voices if v.get('category') != 'premade']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pieces")
    ap.add_argument("out_dir")
    ap.add_argument("--sections", required=True)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--voice", default="Manoj kumar T")
    ap.add_argument("--model", default="eleven_v4")
    ap.add_argument("--stability", type=float, default=0.35)  # lower lets the voice move more with the emotion
    ap.add_argument("--similarity", type=float, default=0.85)  # how closely it keeps to the owner's clone
    a = ap.parse_args()
    key = api_key()
    vid = voice_id(a.voice, key)
    lines = [l.strip() for l in open(a.pieces, encoding="utf-8") if l.strip()]
    os.makedirs(a.out_dir, exist_ok=True)
    for n in (int(x) for x in a.sections.split(",")):
        text = lines[n - 1]
        tag = TAG.match(text)
        mood = tag.group(1) if tag else ""
        body = TAG.sub("", text)
        if mood in TAGS:
            body = f"{TAGS[mood]} {body}"
        t = time.time()
        pcm = call(f"/text-to-speech/{vid}?output_format=pcm_24000", key,
                   {"text": body, "model_id": a.model, "seed": a.seed,
                    "voice_settings": {"stability": a.stability, "similarity_boost": a.similarity}})
        with wave.open(os.path.join(a.out_dir, f"sec_{n:02d}.wav"), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(24000)
            w.writeframes(pcm)
        print(f"section {n}: {len(pcm) / 48000:.1f}s in {time.time() - t:.0f}s (eleven {a.model}, seed {a.seed}"
              f"{', ' + mood if mood else ''})", flush=True)


if __name__ == "__main__":
    main()
