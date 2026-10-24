"""Strict listening test: is every word of every section clear enough to be understood?

    python check.py TEXT_FILE WAV_PATTERN OUT_JSON [--names Meena,Ravi] [--model medium]

TEXT_FILE has one section per line, spelled the way it should be understood (not respelled for
the voice). WAV_PATTERN contains "{n:02d}". Whisper transcribes each section WITHOUT seeing the
script, so it cannot guess words the voice did not say clearly; then the two are compared word by
word. Allowed: spelling of numbers ("3" / "three", "1859" / "eighteen fifty-nine", "15th" / "fifteenth",
"$10" / "ten dollars"), words run together or split ("goodnight"), British and American spelling
("neighbours" / "neighbors"), and other spellings of the same sound for the names in --names
("Mina" for Meena, "Cutler" for Cutlar). A name can also list how it may be heard, after "=":
"San Juan=sun one|san wan". Anything else - a wrong, missing or extra word - fails the section.

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


ORDINAL = {"one": "first", "two": "second", "three": "third", "five": "fifth", "eight": "eighth", "nine": "ninth",
           "twelve": "twelfth"}


def ordinal(n):
    """21 -> twentyfirst, 15 -> fifteenth, 30 -> thirtieth."""
    w = spell(n)
    for end, form in ORDINAL.items():
        if w.endswith(end):
            return w[: -len(end)] + form
    return w[:-1] + "ieth" if w.endswith("y") else w + "th"


def british(w):
    """One spelling for British and American words: neighbour/neighbor, centre/center, realise/realize."""
    w = re.sub(r"^(\w{2,})our(s|ed|ing|ite|ites|hood|ly|able)?$", r"\1or\2", w)
    w = re.sub(r"^(\w{2,}[^aeiou])re(s)?$", r"\1er\2", w)
    return re.sub(r"^(\w{2,})is(e|es|ed|ing|ation|ations)$", r"\1iz\2", w)


def year(n):
    """How a year is said: 1859 -> eighteen fifty nine, 1905 -> nineteen oh five, 1900 -> nineteen hundred."""
    hi, lo = divmod(n, 100)
    return spell(hi) + ("hundred" if lo == 0 else "oh" + spell(lo) if lo < 10 else spell(lo))


# Contractions and their full forms are the same words (Whisper often writes "I'm" as "I am").
CONTRACTIONS = {"i'm": "i am", "you're": "you are", "we're": "we are", "they're": "they are", "it's": "it is",
                "that's": "that is", "there's": "there is", "what's": "what is", "he's": "he is", "she's": "she is",
                "let's": "let us", "don't": "do not", "doesn't": "does not", "didn't": "did not", "can't": "can not",
                "cannot": "can not", "won't": "will not", "isn't": "is not", "aren't": "are not", "wasn't": "was not",
                "weren't": "were not", "i'll": "i will", "you'll": "you will", "we'll": "we will", "they'll": "they will",
                "i've": "i have", "you've": "you have", "we've": "we have", "they've": "they have", "i'd": "i would",
                "here's": "here is", "who's": "who is", "how's": "how is", "where's": "where is", "he'd": "he would",
                "she'd": "she would", "we'd": "we would", "they'd": "they would", "you'd": "you would",
                "it'll": "it will", "that'll": "that will", "he'll": "he will", "she'll": "she will",
                "couldn't": "could not", "wouldn't": "would not", "shouldn't": "should not", "hasn't": "has not",
                "haven't": "have not", "hadn't": "had not", "mustn't": "must not"}
# A ruler's number is written as a Roman numeral: "Wilhelm I" is "Wilhelm the first".
ROMAN = {"I": "first", "II": "second", "III": "third", "IV": "fourth", "V": "fifth", "VI": "sixth", "VII": "seventh",
         "VIII": "eighth"}


def tokens(text):
    out = []
    text = re.sub(r"(?<=\d),(?=\d{3}\b)", "", text.replace("’", "'"))  # 9,860 is one number
    text = re.sub(r"\$(\d+)", r"\1 dollars", text)
    text = re.sub(r"\b([A-Z][a-z]+) (I|II|III|IV|V|VI|VII|VIII)\b(?! [a-z])", lambda m: f"{m.group(1)} the {ROMAN[m.group(2)]}", text)
    text = re.sub(r"[A-Za-z]+'[A-Za-z]+|cannot", lambda m: CONTRACTIONS.get(m.group(0).lower(), m.group(0)), text, flags=re.I)
    for w in re.findall(r"[A-Za-z0-9']+", text.replace("-", " ")):
        w = british(w.lower().replace("'", ""))
        nth = re.fullmatch(r"(\d+)(st|nd|rd|th)", w)
        if nth and int(nth.group(1)) < 10000:
            out.append(ordinal(int(nth.group(1))))
        elif w.isdigit() and int(w) < 10000:
            out.append("§" + w)  # "27" may be read "twenty seven" or (a date) "twenty seventh": readings() has both
        else:
            out.append(w)
    return [w for w in out if w]


def said(n):
    """How a number written in digits may be read: as a number, an ordinal (dates) or a year."""
    return {spell(n), ordinal(n)} | ({year(n)} if 1100 <= n < 2100 else set())


def readings(words):
    """Every way the words can be said (a number in digits in each of its readings)."""
    options = [""]
    for w in words:
        alts = said(int(w[1:])) if w.startswith("§") else [w]
        options = [o + x for o in options for x in alts]
    return set(options)


NAMES, HEARD_AS = [], {}
for entry in filter(None, a.names.split(",")):
    name, _, alts = entry.partition("=")
    key = re.sub(r"[^a-z]", "", name.lower())
    NAMES.append(key)
    HEARD_AS[key] = [re.sub(r"[^a-z]", "", x.lower()) for x in alts.split("|") if x.strip()]


def sound(w):
    """A rough sound key, so spellings of one name match: meena / mina, preethi / priti."""
    for a_, b_ in (("ee", "i"), ("ea", "i"), ("ie", "i"), ("oo", "u"), ("ou", "u"), ("ph", "f"),
                   ("th", "t"), ("dh", "d"), ("bh", "b"), ("kh", "k"), ("sh", "s"), ("w", "v"), ("y", "i")):
        w = w.replace(a_, b_)
    return re.sub(r"(.)\1+", r"\1", w)


def consonants(w):
    """The consonants of a name, in order: unstressed vowels are heard many ways (cutlar / cutler)."""
    return w[:1] + re.sub(r"[aeiouy]", "", sound(w)[1:])


def close(script_words, heard_words):
    if readings(script_words) & readings(heard_words):
        return True
    s, h = "".join(script_words), "".join(heard_words)
    for n in NAMES:
        if n not in s:
            continue
        if any(s.replace(n, alt) == h for alt in HEARD_AS[n]):
            return True
        rest = s.replace(n, "")
        if h.endswith(rest) or h.startswith(rest):  # the name with the words around it
            heard = h[: len(h) - len(rest)] if h.endswith(rest) else h[len(rest):]
            if consonants(heard) == consonants(n):
                return True
        if difflib.SequenceMatcher(a=sound(s), b=sound(h)).ratio() >= 0.85:
            return True
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
        said = " ".join(want[a0:a1]).replace("§", "") or "(nothing)"
        heard = " ".join(got[b0:b1]).replace("§", "") or "(nothing)"
        problems.append(f'"{said}" was heard as "{heard}"')
    report.append({"n": n, "ok": not problems, "heard": heard_text, "problems": problems})
    print(f"section {n}: {'clear' if not problems else 'NOT CLEAR - ' + '; '.join(problems)}", flush=True)

json.dump({"ok": all(r["ok"] for r in report), "sections": report}, open(a.out, "w"), indent=1)
