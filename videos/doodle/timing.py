"""Word timings for a sectioned voiceover, aligned to the script text.

    python timing.py VOICEOVER_TXT SECTION_WAV_PATTERN GAP_SECONDS OUT_JSON

VOICEOVER_TXT has one section per line (the text the TTS read). SECTION_WAV_PATTERN contains
"{n:02d}", e.g. "tts/full_en_{n:02d}.wav". Sections were joined with GAP_SECONDS of silence
between them. Whisper transcribes each section with word timestamps; the script's own words are
then aligned to Whisper's, so the output carries the script's spelling (Whisper mishears names)
with Whisper's timing. Needs faster-whisper and ffmpeg.
"""
import difflib
import json
import re
import subprocess
import sys

import numpy as np
from faster_whisper import WhisperModel

text_file, pattern, gap, out_json = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
lines = [l.strip() for l in open(text_file, encoding="utf-8") if l.strip()]
model = WhisperModel("medium", device="cpu", compute_type="int8")


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def load(path):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-f", "s16le", "-ac", "1",
                          "-ar", "16000", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


sections, offset = [], 0.0
for n, line in enumerate(lines, 1):
    audio = load(pattern.format(n=n))
    duration = len(audio) / 16000
    segs, _ = model.transcribe(audio, language="en", word_timestamps=True, beam_size=5,
                               initial_prompt=line)
    heard = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words if norm(w.word)]
    script = [w for w in re.sub(r"\[[a-z]+\]", "", line).split() if norm(w)]

    times = [None] * len(script)
    sm = difflib.SequenceMatcher(a=[norm(w) for w in script], b=[norm(h[0]) for h in heard],
                                 autojunk=False)
    for op, a0, a1, b0, b1 in sm.get_opcodes():
        if op == "equal":
            for k in range(a1 - a0):
                times[a0 + k] = heard[b0 + k][1:]
        elif op == "replace":
            t0, t1 = heard[b0][1], heard[b1 - 1][2]
            step = (t1 - t0) / (a1 - a0)
            for k in range(a1 - a0):
                times[a0 + k] = (t0 + k * step, t0 + (k + 1) * step)
    # Words Whisper missed entirely: spread them between their neighbours.
    for i, t in enumerate(times):
        if t is None:
            prev = next((times[j][1] for j in range(i - 1, -1, -1) if times[j]), 0.0)
            nxt = next((times[j][0] for j in range(i + 1, len(times)) if times[j]), duration)
            times[i] = (prev, max(prev, nxt))

    words = [{"w": w, "t0": round(offset + a, 3), "t1": round(offset + b, 3)}
             for w, (a, b) in zip(script, times)]
    matched = sum(b1 - b0 for op, a0, a1, b0, b1 in sm.get_opcodes() if op == "equal")
    print(f"section {n}: {len(script)} words, {matched} matched exactly, {duration:.2f}s", flush=True)
    sections.append({"n": n, "offset": round(offset, 3), "duration": round(duration, 3), "words": words})
    offset += duration + gap

json.dump({"total": round(offset - gap, 3), "sections": sections}, open(out_json, "w"), indent=1)
print("wrote", out_json)
