"""The listening check for a Money Tea Talks script, and the word timings build.py follows.

    $WHISPER_PY videos/money/check_voice.py WORK      # WORK/voice_ta/sec_NN.wav -> WORK/words.json; exit 1 on a fail

faster-whisper "medium" (CPU, int8) listens to every line: it must be heard as Tamil with a language probability of
0.8 or more, and the first and last words must be there (compare the printed text with the script; a soft final
consonant such as the ன் of வாங்கினான் is often dropped by Whisper itself, so judge the sound, not the spelling).
The audio is decoded with ffmpeg first (this faster-whisper's own decoder fails on the pinned PyAV). Local only.
"""
import glob
import json
import os
import subprocess
import sys

import numpy as np
from faster_whisper import WhisperModel


def main():
    work = sys.argv[1]
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    out, failed = {}, []
    for path in sorted(glob.glob(os.path.join(work, "voice_ta", "sec_*.wav"))):
        n = int(os.path.basename(path)[4:6])
        pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        segs, info = model.transcribe(np.frombuffer(pcm, np.float32), word_timestamps=True, beam_size=5)
        words = [(w.word.strip(), round(w.start, 2), round(w.end, 2)) for s in segs for w in s.words]
        out[f"ta{n}"] = {"lang": info.language, "p": round(info.language_probability, 2), "words": words}
        ok = info.language == "ta" and info.language_probability >= 0.8
        if not ok:
            failed.append(n)
        print(f"{'ok  ' if ok else 'FAIL'} line {n}: {info.language} {info.language_probability:.2f} | "
              f"{' '.join(w[0] for w in words)}", flush=True)
    json.dump(out, open(os.path.join(work, "words.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if failed:
        sys.exit(f"lines {failed} were not heard as Tamil: reword them or voice them again with --seed 8")


if __name__ == "__main__":
    main()
