"""Turn voiced pieces into the owner's voice: Chatterbox's voice conversion (MIT) keeps a piece's
performance (its words, rhythm, pauses and the rise and fall of the voice) and swaps the sound of the
voice for the owner's, taken from TARGET_WAV (the owner talking naturally; Chatterbox uses its first 10 s).

    python vc.py TARGET_WAV SRC_DIR OUT_DIR --sections 1,3

SRC_DIR/sec_NN.wav (tts.py --engine design) becomes OUT_DIR/sec_NN.wav, 24 kHz mono. Runs in the
Chatterbox environment (build.py's CHATTERBOX_PY).
"""
import argparse
import os
import time

import torch
import torchaudio as ta
from chatterbox.vc import ChatterboxVC

ap = argparse.ArgumentParser()
ap.add_argument("target")
ap.add_argument("src_dir")
ap.add_argument("out_dir")
ap.add_argument("--sections", required=True)
a = ap.parse_args()
torch.set_num_threads(os.cpu_count() or 4)
vc = ChatterboxVC.from_pretrained(device="cpu")
vc.set_target_voice(a.target)  # once: it uses the first 10 s of the target
os.makedirs(a.out_dir, exist_ok=True)
for n in (int(x) for x in a.sections.split(",")):
    t = time.time()
    wav = vc.generate(os.path.join(a.src_dir, f"sec_{n:02d}.wav"))
    if vc.sr != 24000:
        wav = ta.functional.resample(wav, vc.sr, 24000)
    ta.save(os.path.join(a.out_dir, f"sec_{n:02d}.wav"), wav.float(), 24000)
    print(f"section {n}: in the owner's voice in {time.time() - t:.0f}s", flush=True)
