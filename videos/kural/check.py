"""Strict listening test: is every word of every section clear enough to be understood?

    python check.py TEXT_FILE WAV_PATTERN OUT_JSON [--names Meena,Ravi] [--model medium]

TEXT_FILE has one section per line, spelled the way it should be understood (not respelled for
the voice). WAV_PATTERN contains "{n:02d}". Whisper transcribes each section WITHOUT seeing the
script, so it cannot guess words the voice did not say clearly; then the two are compared word by
word. Allowed: spelling of numbers ("3" / "three"), words run together or split ("goodnight"),
and close spellings of the names in --names ("Mina" for Meena). Anything else - a wrong, missing
or extra word - fails the section.

OUT_JSON: {"ok": bool, "sections": [{"n", "ok", "heard", "problems": [...]}]}
"""
import argparse
import difflib
import json
import re
import subprocess

import numpy as np
from faster_whisper import WhisperModel

ap = argparse.ArgumentParser()
ap.add_argument("text")
ap.add_argument("pattern")
ap.add_argument("out")
ap.add_argument("--names", default="")
ap.add_argument("--model", default="medium")
ap.add_argument("--sections")
a = ap.parse_args()

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def spell(n):
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ("" if n % 10 == 0 else ONES[n % 10])
    if n < 1000:
        return ONES[n // 100] + "hundred" + ("" if n % 100 == 0 else "and" + spell(n % 100))
    return spell(n // 1000) + "thousand" + ("" if n % 1000 == 0 else spell(n % 1000))


def tokens(text):
    out = []
    for w in re.findall(r"[A-Za-z0-9']+", text.replace("-", " ")):
        w = w.lower().replace("'", "")
        out.append(spell(int(w)) if w.isdigit() and int(w) < 10000 else w)
    return [w for w in out if w]


NAMES = [n.lower() for n in a.names.split(",") if n]


def close(script_words, heard_words):
    s, h = "".join(script_words), "".join(heard_words)
    if s == h:
        return True
    if any(n in s for n in NAMES):
        return difflib.SequenceMatcher(a=s, b=h).ratio() >= 0.8
    return False


lines = [l.strip() for l in open(a.text, encoding="utf-8") if l.strip()]
todo = [int(x) for x in a.sections.split(",")] if a.sections else range(1, len(lines) + 1)
model = WhisperModel(a.model, device="cpu", compute_type="int8")
report = []
for n in todo:
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", a.pattern.format(n=n), "-f", "s16le", "-ac", "1",
                          "-ar", "16000", "-"], check=True, capture_output=True).stdout
    audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
    segs, _ = model.transcribe(audio, language="en", beam_size=5, condition_on_previous_text=False)
    heard_text = " ".join(s.text.strip() for s in segs)
    want, got = tokens(lines[n - 1]), tokens(heard_text)
    problems = []
    for op, a0, a1, b0, b1 in difflib.SequenceMatcher(a=want, b=got, autojunk=False).get_opcodes():
        if op == "equal" or close(want[a0:a1], got[b0:b1]):
            continue
        said = " ".join(want[a0:a1]) or "(nothing)"
        heard = " ".join(got[b0:b1]) or "(nothing)"
        problems.append(f'"{said}" was heard as "{heard}"')
    report.append({"n": n, "ok": not problems, "heard": heard_text, "problems": problems})
    print(f"section {n}: {'clear' if not problems else 'NOT CLEAR - ' + '; '.join(problems)}", flush=True)

json.dump({"ok": all(r["ok"] for r in report), "sections": report}, open(a.out, "w"), indent=1)
