"""Safety checks for the private studio.

Every prompt, every generated image and every generated text passes through
these checks. They are deliberately strict: when a check is unsure, it blocks.

Two rules are enforced:
1. Only clearly adult characters. Anything that describes or hints at a minor
   is blocked.
2. Only fictional characters. Prompts that point at real people (celebrities,
   people from the user's life, social media handles) are blocked.
"""

import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class Verdict:
    allowed: bool
    reason: str = ""


ALLOWED = Verdict(True)

# Words that describe or imply a minor. Blocked in prompts and in generated text.
MINOR_TERMS = frozenset({
    "child", "children", "childs", "childlike", "kid", "kids", "kiddie", "kiddo",
    "underage", "infant", "infants", "toddler", "toddlers",
    "teen", "teens", "teenage", "teenager", "teenagers", "teeny", "preteen", "preteens",
    "tween", "tweens", "adolescent", "adolescents", "juvenile", "juveniles",
    "pubescent", "prepubescent", "loli", "lolis", "lolita", "lolicon",
    "shota", "shotas", "shotacon", "jailbait", "schoolgirl", "schoolgirls",
    "schoolboy", "schoolboys", "kindergarten", "kindergartner",
})

# Words that often describe minors but also have everyday adult uses. Blocked
# in prompts (with a suggestion of what to write instead). Generated text is
# only checked against MINOR_TERMS, phrases and ages, so a story can still
# say "a minor detail".
AMBIGUOUS_TERMS = frozenset({
    "minor", "minors", "girl", "girls", "boy", "boys", "young", "younger",
    "youthful", "youth", "baby", "babies", "daughter", "daughters", "son", "sons",
    "stepdaughter", "stepson", "niece", "nephew", "granddaughter", "grandson",
})

MINOR_PHRASES = (
    "child like", "little girl", "little boy", "little one", "school uniform",
    "high school", "highschool", "middle school", "elementary school", "grade school",
    "junior high", "barely legal", "barely 18", "barely eighteen", "just turned 18",
    "just turned eighteen", "young looking", "looks young", "looking young",
)

REAL_PERSON_TERMS = frozenset({
    "celebrity", "celebrities", "celeb", "celebs", "famous", "lookalike",
    "lookalikes", "deepfake", "deepfakes", "doppelganger",
})

REAL_PERSON_PHRASES = (
    "look alike", "deep fake", "real person", "real people", "real life person",
    "in the likeness of",
)

# "my ex", "my coworker" and so on point at someone in the user's own life.
_MY_RELATION = re.compile(
    r"\bmy\s+(?:ex|girlfriend|boyfriend|wife|husband|partner|crush|coworker|co worker|"
    r"colleague|classmate|neighbou?r|boss|teacher|student|friend|sister|brother|cousin|"
    r"aunt|uncle|mom|mum|mother|dad|father|step\w*)\b"
)
_EX_PARTNER = re.compile(r"\bex\s+(?:girlfriend|boyfriend|wife|husband|partner)\b")
_HANDLE = re.compile(r"@[a-z0-9_.]{2,}")
_URL = re.compile(r"https?://|www\.")

_NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
}
_AGE = r"\b(\d{1,2}|" + "|".join(_NUMBER_WORDS) + r")"
_NOT_A_TIME = r"(?!\s*(?:am|pm|o'?clock|percent|minutes?|hours?|days?|weeks?|months?|times|out|of)\b)"
_AGE_PATTERNS = (
    re.compile(_AGE + r"\s*(?:years?|yrs?)\s*old\b"),
    re.compile(_AGE + r"\s*(?:yo|y o)\b"),
    re.compile(_AGE + r"\s?[fm]\b"),
    re.compile(r"\b(?:age|aged|ages|turned|turning)\s+" + _AGE[2:] + r"\b"),
    re.compile(r"\b(?:is|was|being|she's|he's|i'm|im)\s+" + _AGE[2:] + r"\b" + _NOT_A_TIME),
    re.compile(_AGE + r"(?:st|nd|rd|th)?\s+birthday\b"),
)
_GRADE = re.compile(
    r"\b(?:\d{1,2}(?:st|nd|rd|th)|first|second|third|fourth|fifth|sixth|seventh|"
    r"eighth|ninth|tenth|eleventh|twelfth)\s+grade\b|\bgrade\s+\d{1,2}\b"
)

_LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"})
_SINGLE_LETTER_RUN = re.compile(r"\b[a-z](?: [a-z]\b)+")
_INVISIBLE = re.compile(r"[​-‏⁠﻿­]")

# Added to every image prompt, and used as the negative prompt.
ADULT_SUFFIX = " Every person shown is a clearly adult woman or man."
NEGATIVE_PROMPT = (
    "child, children, kid, teenager, minor, underage, young-looking, childlike, "
    "school uniform, low quality, ugly, unfinished, out of focus, deformed, "
    "disfigured, blurry, smudged"
)

# Asked about every generated image. Only a clear "NO" lets the image through.
AGE_CHECK_QUESTION = (
    "Look carefully at this image. Does any person in it look younger than 18 years old? "
    "Judge by the face, body proportions, clothing and setting. "
    "If there are no people in the image, answer NO. "
    "Answer with exactly one word: YES or NO."
)

WRITER_SYSTEM_PROMPT = (
    "You are a writing assistant for an adults-only (18+) creator. "
    "All characters are fictional adults aged 21 or older; call them women and men. "
    "Never write about minors, real people, or non-consensual acts. "
    "If a request asks for any of those, reply only: I can't write that."
)


def _normalize(text):
    """Lowercase, strip accents and invisible characters, and turn punctuation into spaces."""
    text = unicodedata.normalize("NFKC", text)
    text = _INVISIBLE.sub("", text)
    text = "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))
    text = text.lower().replace("’", "'")
    return re.sub(r"[^a-z0-9@$']+", " ", text).strip()


def _deobfuscate(text):
    """Undo number-for-letter tricks such as 't33n'."""
    return text.translate(_LEET)


def _words(text):
    """Every word, plus words spelled out letter by letter ('t.e.e.n' is normalized to 't e e n')."""
    words = set(re.findall(r"[a-z]+", text))
    for run in _SINGLE_LETTER_RUN.finditer(text):
        letters = run.group(0).split()
        words.update("".join(letters[i:j]) for i in range(len(letters)) for j in range(i + 2, len(letters) + 1))
    return words


def _has_phrase(text, phrases):
    padded = f" {text} "
    return next((p for p in phrases if f" {p} " in padded), None)


def _minor_age(text):
    for pattern in _AGE_PATTERNS:
        for match in pattern.finditer(text):
            value = match.group(1)
            age = int(value) if value.isdigit() else _NUMBER_WORDS[value]
            if age < 18:
                return match.group(0).strip()
    grade = _GRADE.search(text)
    return grade.group(0) if grade else None


def _blocked_minor(term):
    return Verdict(False, f"Blocked: the text mentions \"{term}\". Only clearly adult characters are allowed.")


def _check_minors(plain, cleaned, strict_only):
    age = _minor_age(plain)
    if age:
        return _blocked_minor(age)
    words = _words(plain) | _words(cleaned)
    hit = min(words & MINOR_TERMS, default=None)
    hit = hit or _has_phrase(plain, MINOR_PHRASES) or _has_phrase(cleaned, MINOR_PHRASES)
    if hit:
        return _blocked_minor(hit)
    if not strict_only:
        hit = min(words & AMBIGUOUS_TERMS, default=None)
        if hit:
            return Verdict(
                False,
                f"Blocked: \"{hit}\" can describe a minor. Describe characters as adults instead, "
                "for example \"woman in her thirties\" or \"man\".",
            )
    return ALLOWED


def _check_real_people(raw_lower, plain, cleaned):
    if _HANDLE.search(raw_lower) or _URL.search(raw_lower):
        return Verdict(False, "Blocked: the prompt contains a social media handle or link. Only fictional characters are allowed.")
    hit = min((_words(plain) | _words(cleaned)) & REAL_PERSON_TERMS, default=None)
    hit = hit or _has_phrase(plain, REAL_PERSON_PHRASES)
    match = _MY_RELATION.search(plain) or _EX_PARTNER.search(plain)
    hit = hit or (match.group(0) if match else None)
    if hit:
        return Verdict(False, f"Blocked: \"{hit}\" points at a real person. Only fictional characters are allowed.")
    return ALLOWED


def check_prompt(text):
    """Check an image prompt or a writing request before anything is generated."""
    if not text or not text.strip():
        return Verdict(False, "Please type a prompt first.")
    plain = _normalize(text)
    cleaned = _deobfuscate(plain)
    verdict = _check_minors(plain, cleaned, strict_only=False)
    if not verdict.allowed:
        return verdict
    return _check_real_people(unicodedata.normalize("NFKC", text).lower(), plain, cleaned)


def check_generated_text(text):
    """Check text the model wrote, using only the unambiguous minor terms, phrases and ages."""
    plain = _normalize(text)
    verdict = _check_minors(plain, _deobfuscate(plain), strict_only=True)
    if not verdict.allowed:
        return Verdict(False, "Blocked: the generated text referred to a minor, so it was discarded. Try rewording your request.")
    return ALLOWED


def image_passes_age_check(answer):
    """True only when the age-check answer is a clear NO. Anything else blocks the image."""
    words = re.findall(r"[a-z]+", (answer or "").lower())
    return bool(words) and words[0] == "no"
