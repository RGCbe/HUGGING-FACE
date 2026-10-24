"""Trim a voice sample to end on a whole word, and write down exactly what it says.

    python ref_prep.py IN_AUDIO OUT_WAV OUT_TXT [--max 12]

Qwen3-TTS clones a voice by carrying on from the sample, so a sample that stops in the middle of
a word or sentence leaks into the next line ("And why does..."). This cuts the sample just after
the last word (not a joining word like "and") that ends before --max seconds and saves Whisper's
transcript of what is left.
Needs faster-whisper and ffmpeg.
"""
import argparse
import subprocess

import numpy as np
from faster_whisper import WhisperModel

ap = argparse.ArgumentParser()
ap.add_argument("audio")
ap.add_argument("out_wav")
ap.add_argument("out_txt")
ap.add_argument("--max", type=float, default=12.0)
a = ap.parse_args()

raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", a.audio, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                     check=True, capture_output=True).stdout
audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
model = WhisperModel("medium", device="cpu", compute_type="int8")
segs, _ = model.transcribe(audio, language="en", beam_size=5, word_timestamps=True)
words = [w for s in segs for w in s.words]
keep = [w for w in words if w.end <= a.max - 0.1]
# and not on a little joining word, which sounds like the sentence goes on
JOINERS = {"and", "or", "but", "so", "the", "a", "an", "of", "to", "in", "on", "at", "for", "with", "that", "is"}
while keep and keep[-1].word.strip(" ,.").lower() in JOINERS:
    keep.pop()
if len(keep) < 5:
    raise SystemExit("the voice sample is too short: it needs at least a few seconds of clear speech")
end = keep[-1].end + 0.05
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", a.audio, "-t", f"{end:.2f}", "-af",
                f"afade=t=out:st={end - 0.08:.2f}:d=0.08", "-ar", "24000", "-ac", "1", a.out_wav], check=True)
open(a.out_txt, "w").write("".join(w.word for w in keep).strip())
print(f"voice sample: {end:.1f}s, {len(keep)} words, ends with \"{keep[-1].word.strip()}\"")
