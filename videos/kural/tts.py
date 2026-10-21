"""Voice sections of a script with Chatterbox-Turbo in a reference speaker's voice.

    python tts.py REF_WAV TEXT_FILE OUT_DIR [--sections 1,3] [--seed 7] [--temperature 0.8]

TEXT_FILE has one section per line. Each section is generated in chunks of a few sentences and
saved as OUT_DIR/sec_NN.wav (24 kHz mono). --sections regenerates only those sections.
"""
import argparse
import os
import re
import time

import numpy as np
import soundfile as sf
import torch

from chatterbox.tts_turbo import ChatterboxTurboTTS

ap = argparse.ArgumentParser()
ap.add_argument("ref")
ap.add_argument("text")
ap.add_argument("out_dir")
ap.add_argument("--sections")
ap.add_argument("--seed", type=int, default=7)
ap.add_argument("--temperature", type=float, default=0.8)
a = ap.parse_args()

lines = [l.strip() for l in open(a.text, encoding="utf-8") if l.strip()]
todo = [int(x) for x in a.sections.split(",")] if a.sections else list(range(1, len(lines) + 1))
os.makedirs(a.out_dir, exist_ok=True)
torch.manual_seed(a.seed)
torch.set_num_threads(os.cpu_count() or 4)

model = ChatterboxTurboTTS.from_pretrained(device="cpu")
model.prepare_conditionals(a.ref)


def chunks(text, limit=220):
    out, cur = [], ""
    for s in re.split(r"(?<=[.?!])\s+", text):
        if cur and len(cur) + len(s) + 1 > limit:
            out.append(cur)
            cur = s
        else:
            cur = f"{cur} {s}".strip()
    return out + [cur] if cur else out


gap = np.zeros(int(0.25 * model.sr), dtype=np.float32)
for n in todo:
    t = time.time()
    parts = []
    for c in chunks(lines[n - 1]):
        parts += [model.generate(c, temperature=a.temperature).squeeze(0).numpy().astype(np.float32), gap]
    wav = np.concatenate(parts[:-1])
    sf.write(os.path.join(a.out_dir, f"sec_{n:02d}.wav"), wav, model.sr)
    print(f"section {n}: {len(wav) / model.sr:.1f}s in {time.time() - t:.0f}s (seed {a.seed}, temperature {a.temperature})", flush=True)
