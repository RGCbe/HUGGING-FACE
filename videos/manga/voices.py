"""The character voices of a movie-version episode, made with ElevenLabs (each character a different voice).

    python3 voices.py add                              add the cast's library voices to the ElevenLabs account
    python3 voices.py casting OUT.wav                  one test file: each candidate voice says two of its lines
    python3 voices.py lines SHOTS.json OUT_DIR [--only S08,S20] [--seed 7] [--cast cast/voices.json]
                                                       every spoken line of the shot list -> OUT_DIR/SNN.wav

The voices of a series are saved in its cast/voices.json (voice, voice id, model, stability, similarity, speed,
style per character), so every episode uses the same voices; CAST below is only the starting point.

A line in shots.json is ["who", "text"]; "(quietly)" or "(thinking)" at the start becomes an ElevenLabs audio tag
that is performed, not said. A shot may add "tag": "[laughs]" for how the line is acted. 24 kHz mono WAV.
The key is ELEVENLABS_API_KEY from the environment; it is never printed. Audio files stay out of git.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import wave

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kural"))
from eleven import api_key, call  # noqa: E402

# character -> voice name in the account; library voices are added by `add` (name, voice id prefix)
CAST = {
    "narrator": {"voice": "Manoj kumar T", "stability": 0.3, "similarity": 0.9},
    "arjun": {"voice": "Bunty - Warm and Clear", "stability": 0.45, "similarity": 0.8},
    "meera": {"voice": "Tara - Conversational and Expressive", "stability": 0.4, "similarity": 0.8},
    "viktor": {"voice": "Liam - Energetic, Social Media Creator", "stability": 0.3, "similarity": 0.8},
    "raghu": {"voice": "Viraj - Deep, Resonant and Lyrical", "stability": 0.4, "similarity": 0.8},
}
LIBRARY = {"Bunty - Warm and Clear": "omLr0bN17l", "Tara - Conversational and Expressive": "P7vsEyTOpZ",
           "Viraj - Deep, Resonant and Lyrical": "tSVwqkJGEK", "Manav - Friendly, Calm and Natural": "2BsEFcU7jU",
           "Anika - Sweet and Lively": "ecp3DWciuU"}
CASTING = [
    ("arjun", "Bunty - Warm and Clear", ["Tea, sir? Good for the nerves before a dungeon.", "...Cardamom."]),
    ("arjun", "Manav - Friendly, Calm and Natural", ["Tea, sir? Good for the nerves before a dungeon.", "...Cardamom."]),
    ("meera", "Tara - Conversational and Expressive", ["Viktor, be nice. Three teas, please.", "Can I get one to go?"]),
    ("meera", "Anika - Sweet and Lively", ["Viktor, be nice. Three teas, please.", "Can I get one to go?"]),
    ("viktor", "Liam - Energetic, Social Media Creator", ["[laughs] Ha! Look, everyone! It's the F-Rank tea boy!",
                                                          "[shouting] YOU! What did you put in that tea?!"]),
    ("raghu", "Viraj - Deep, Resonant and Lyrical", ["[grunts] Ghhk...!"]),
]
SR = 24000
MODEL = "eleven_v4"  # the model of the channel's narration (videos/teabreak/config.json)
MODES = {"quietly": "[whispers]", "thinking": "[thoughtfully]"}


def voices(key):
    return {v["name"]: v["voice_id"] for v in json.loads(call("/voices", key))["voices"]}


def add(key):
    have = voices(key)
    for name, prefix in LIBRARY.items():
        if name in have:
            print(f"have {name}")
            continue
        q = urllib.parse.quote(name.split(" - ")[0])
        found = json.loads(call(f"/shared-voices?page_size=50&search={q}&language=en", key))["voices"]
        match = [v for v in found if v["voice_id"].startswith(prefix)]
        if not match:
            sys.exit(f"{name}: not found in the voice library")
        v = match[0]
        call(f"/voices/add/{v['public_owner_id']}/{v['voice_id']}", key, {"new_name": name})
        print(f"added {name}")


def speak(key, vid, text, cfg, seed=7):
    settings = {"stability": cfg["stability"], "similarity_boost": cfg["similarity"]}
    for k in ("speed", "style"):  # the small adjustments saved per character in the series voice file
        if k in cfg:
            settings[k] = cfg[k]
    return call(f"/text-to-speech/{vid}?output_format=pcm_{SR}", key,
                {"text": text, "model_id": cfg.get("model", MODEL), "seed": seed, "voice_settings": settings})


def series_cast(shots_file, cast_file=None):
    """The series' saved voices (cast/voices.json next to the episodes), so every episode sounds the same."""
    path = cast_file or os.path.join(os.path.dirname(os.path.abspath(shots_file)), "..", "..", "cast", "voices.json")
    if os.path.exists(path):
        return json.load(open(path))["cast"], path
    return CAST, "voices.py defaults"


def write(path, pcm):
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm)


def tempo(pcm, factor):
    """Slow down (factor < 1) or speed up a line without changing the voice's pitch (ffmpeg atempo).
    ElevenLabs' own "speed" setting is ignored by the Eleven v4 model, so the pace is set here."""
    if not factor or abs(factor - 1) < 0.001:
        return pcm
    import subprocess
    return subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-",
                           "-af", f"atempo={factor}", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-"],
                          input=pcm, capture_output=True, check=True).stdout


def acted(text, tag=""):
    m = re.match(r"^\((\w+)\)\s*", text)
    if m:
        text = MODES.get(m.group(1), "") + " " + text[m.end():]
    return (tag + " " + text).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["add", "casting", "lines"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--only")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--cast", help="the series voice file (default: cast/voices.json of the episode's series)")
    a = ap.parse_args()
    key = api_key()
    if a.cmd == "add":
        return add(key)
    have = voices(key)
    if a.cmd == "casting":
        out, pcm = a.args[0], b""
        gap = b"\x00\x00" * int(SR * 0.8)
        for who, name, lines in CASTING:
            cfg = dict(CAST[who], voice=name)
            for line in lines:
                pcm += speak(key, have[name], line, cfg) + gap
            print(f"{who}: {name}")
            pcm += gap
        write(out, pcm)
        print(f"{len(pcm) / 2 / SR:.0f} s -> {out}")
        return
    shots, out_dir = json.load(open(a.args[0]))["shots"], a.args[1]
    cast, where = series_cast(a.args[0], a.cast)
    print(f"voices from {where}")
    os.makedirs(out_dir, exist_ok=True)
    only = set(a.only.split(",")) if a.only else None
    for s in shots:
        if not s.get("line") or (only and s["id"] not in only):
            continue
        who, text = s["line"]
        cfg = cast[who]
        t = time.time()
        pcm = speak(key, cfg.get("voice_id") or have[cfg["voice"]], acted(text, s.get("tag", "")), cfg, a.seed)
        pcm = tempo(pcm, cfg.get("tempo", 1.0))
        write(os.path.join(out_dir, f"{s['id']}.wav"), pcm)
        print(f"{s['id']} {who}: {len(pcm) / 2 / SR:.1f} s ({time.time() - t:.0f} s) {text[:50]}", flush=True)


if __name__ == "__main__":
    main()
