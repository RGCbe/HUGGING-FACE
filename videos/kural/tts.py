"""Voice sections of a script in a reference speaker's voice.

    python tts.py REF_WAV TEXT_FILE OUT_DIR [--ref-text REF_TXT] [--sections 1,3] [--seed 7]
                  [--temperature T] [--engine qwen|chatterbox|design] [--refs REFS_JSON] [--voice-only]
                  [--instruct TEXT]

TEXT_FILE has one section per line; each is saved as OUT_DIR/sec_NN.wav (24 kHz mono), and
--sections regenerates only those sections.

A line may start with an emotion tag, "[excited] Wait, wait, wait!". With --refs, a JSON object
{"excited": [WAV, TXT], ...} of samples of the same speaker saying something in that emotion, the
qwen engine speaks the line from that sample, and so in its mood (it carries on from the sample's
voice and delivery). A line without a tag, or with a tag --refs lacks, uses REF_WAV. Tags are never
read out.

--engine qwen (the default) is Qwen3-TTS-12Hz-0.6B-Base: closest to the speaker's voice. It needs
--ref-text, the exact words of REF_WAV (see ref_prep.py), and a sample that ends on a whole word.
--engine chatterbox is Chatterbox-Turbo, the earlier engine: quicker, but less like the speaker.
--engine design is Qwen3-TTS-12Hz-1.7B-VoiceDesign: no sample at all, a voice actor described by
--instruct, and an emotion tag adds how that line is said (MOODS). It is the first half of the "actor"
voice (build.py): this performance is then turned into the owner's voice by vc.py. REF is unused.

--voice-only (qwen) takes only the sound of REF_WAV's voice (its speaker embedding), not its
delivery: the model speaks in its own rhythm instead of carrying on the sample's. With a flat sample
(the Tea Break one is a bank announcement) this is far livelier: on one test line the pitch moved
6.5 semitones instead of 2.7, at 153 words a minute instead of 196, with real pauses, and it still
matched the owner's voice (0.94 against 0.95). --refs emotion samples still carry their delivery.
"""
import argparse
import json
import os
import re
import time

import numpy as np
import soundfile as sf
import torch

ap = argparse.ArgumentParser()
ap.add_argument("ref")
ap.add_argument("text")
ap.add_argument("out_dir")
ap.add_argument("--ref-text")
ap.add_argument("--sections")
ap.add_argument("--seed", type=int, default=7)
ap.add_argument("--temperature", type=float)
ap.add_argument("--engine", default="qwen", choices=["qwen", "chatterbox", "design"])
ap.add_argument("--refs")
ap.add_argument("--voice-only", action="store_true")
ap.add_argument("--instruct", default="A warm, friendly Indian man in his thirties telling a story to a friend over tea. "
                "Relaxed and expressive, natural rhythm, real pauses. He is talking, not reading.")
a = ap.parse_args()
TAG = re.compile(r"^\[([a-z]+)\]\s*")

lines = [l.strip() for l in open(a.text, encoding="utf-8") if l.strip()]
todo = [int(x) for x in a.sections.split(",")] if a.sections else list(range(1, len(lines) + 1))
os.makedirs(a.out_dir, exist_ok=True)
torch.manual_seed(a.seed)
torch.set_num_threads(os.cpu_count() or 4)
SR = 24000

if a.engine == "qwen":
    from qwen_tts import Qwen3TTSModel

    model = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-0.6B-Base", device_map="cpu", dtype=torch.float32,
                                          attn_implementation="sdpa")
    base = (dict(ref_audio=a.ref, x_vector_only_mode=True) if a.voice_only
            else dict(ref_audio=a.ref, ref_text=open(a.ref_text).read().strip()))
    prompts = {None: model.create_voice_clone_prompt(**base)}
    for mood, (wav, txt) in (json.load(open(a.refs)) if a.refs else {}).items():
        prompts[mood] = model.create_voice_clone_prompt(ref_audio=wav, ref_text=open(txt).read().strip())
    extra = {"temperature": a.temperature} if a.temperature else {}

    def say(text):
        tag = TAG.match(text)
        prompt = prompts.get(tag.group(1) if tag else None, prompts[None])
        text = re.sub(r"\[[a-z]+\]\s*", "", text)
        wavs, sr = model.generate_voice_clone(text=text, language="English", voice_clone_prompt=prompt, **extra)
        assert sr == SR, sr
        return wavs[0].astype(np.float32)
elif a.engine == "design":
    from qwen_tts import Qwen3TTSModel

    MOODS = {"excited": "This line is excited and fast, he can't wait to tell it.",
             "funny": "This line is funny: a smile in the voice, deadpan on the last words.",
             "mysterious": "This line is quiet and slow, a little mysterious.",
             "shocked": "This line is surprised, as if he can't believe it.",
             "serious": "This line is low, steady and serious, no smile.",
             "warm": "This line is warm and friendly, like greeting a friend."}
    model = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", device_map="cpu", dtype=torch.float32,
                                          attn_implementation="sdpa")
    extra = {"temperature": a.temperature} if a.temperature else {}

    def say(text):
        tag = TAG.match(text)
        instruct = a.instruct + (" " + MOODS[tag.group(1)] if tag and tag.group(1) in MOODS else "")
        wavs, sr = model.generate_voice_design(text=TAG.sub("", text), instruct=instruct, language="English", **extra)
        assert sr == SR, sr
        return wavs[0].astype(np.float32)
else:
    from chatterbox.tts_turbo import ChatterboxTurboTTS

    model = ChatterboxTurboTTS.from_pretrained(device="cpu")
    model.prepare_conditionals(a.ref)
    gap = np.zeros(int(0.25 * SR), dtype=np.float32)

    def say(text):
        text = TAG.sub("", text)
        parts, cur = [], ""
        for s in re.split(r"(?<=[.?!])\s+", text):  # a few sentences at a time
            if cur and len(cur) + len(s) + 1 > 220:
                parts.append(cur)
                cur = s
            else:
                cur = f"{cur} {s}".strip()
        wavs = [model.generate(p, temperature=a.temperature or 0.5).squeeze(0).numpy().astype(np.float32)
                for p in parts + [cur] if p]
        return np.concatenate([x for w in wavs for x in (w, gap)][:-1])

for n in todo:
    t = time.time()
    wav = say(lines[n - 1])
    sf.write(os.path.join(a.out_dir, f"sec_{n:02d}.wav"), wav, SR)
    tag = TAG.match(lines[n - 1])
    mood = f", {tag.group(1)}" if tag else ""
    print(f"section {n}: {len(wav) / SR:.1f}s in {time.time() - t:.0f}s ({a.engine}, seed {a.seed}{mood})", flush=True)
