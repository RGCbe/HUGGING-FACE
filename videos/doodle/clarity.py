"""Is the voice in a finished video clear on a phone speaker? Run on every video before it is uploaded.

    python3 clarity.py VIDEO_OR_AUDIO [...]

The owner's rule (22 Nov 2026: "now onwards my video have good voice and crystal clear"), measured the way we found
the problem on 21 Nov against a Tamil Marvel channel the owner's friend found clearer (theirs: 49% of the sound's
energy in the speech range, 2% bass; ours then: 20% and 16%). Over the loud parts (where the voice is), it measures:
  speech   share of energy at 500-2,000 Hz, where words are understood: at least 35%
  bass     share below 150 Hz, which a phone cannot play and which muddies the voice: at most 10%
  loudness integrated loudness, about -14 LUFS (YouTube's level): between -16 and -12
Prints one line per file and exits 1 if any file fails, so a run stops before uploading a muddy video.
"""
import json
import re
import subprocess
import sys

import numpy as np

SR = 16000
MIN_SPEECH, MAX_BASS, LUFS = 35.0, 10.0, (-16.0, -12.0)


def measure(path):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(SR), "-f",
                          "f32le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32)
    n = 2048
    fr = np.fft.rfftfreq(n, 1 / SR)
    frames = [a[i:i + n] * np.hanning(n) for i in range(0, len(a) - n, n // 2) if np.sqrt(np.mean(a[i:i + n] ** 2)) > 0.01]
    spec = np.mean([np.abs(np.fft.rfft(x)) ** 2 for x in frames], axis=0)
    tot = spec.sum()
    band = lambda lo, hi: 100 * spec[(fr >= lo) & (fr < hi)].sum() / tot
    log = subprocess.run(["ffmpeg", "-nostdin", "-i", path, "-vn", "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", log)
    return {"speech": round(band(500, 2000), 1), "bass": round(band(0, 150), 1), "lufs": float(m[-1]) if m else None}


def main():
    bad = []
    for path in sys.argv[1:]:
        r = measure(path)
        problems = []
        if r["speech"] < MIN_SPEECH:
            problems.append(f"speech range {r['speech']}% < {MIN_SPEECH}% (muddy: voicefx.VOICE_CLEAR missing?)")
        if r["bass"] > MAX_BASS:
            problems.append(f"bass {r['bass']}% > {MAX_BASS}% (boomy)")
        if r["lufs"] is None or not LUFS[0] <= r["lufs"] <= LUFS[1]:
            problems.append(f"loudness {r['lufs']} LUFS outside {LUFS}")
        print(("CLEAR  " if not problems else "UNCLEAR") + f"  {path}: " + json.dumps(r) + ("" if not problems else "  " + "; ".join(problems)))
        if problems:
            bad.append(path)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
