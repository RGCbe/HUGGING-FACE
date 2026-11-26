"""Score a Tamil song's lyrics against SONG_CRAFT.md before any music is made (like hookscore.py for scripts).

    python3 lyrics_check.py SONG.json          # prints the score, every finding, and exits 1 below the pass mark

It reads SONG.json "lyrics" (section tags in square brackets, one sung line per row; "(...)" = the gang's answer) and
"title". What it checks, from the study of Tamil film songs (SONG_CRAFT.md):
- the parts are there and in order: the pallavi (hook) early and back at least twice, a charanam (story), an ending;
- the pallavi is 2-4 lines and its first line carries the title;
- lines are short enough to sing: a sung line <= 14 syllables, a rapped line <= 20 (syllables estimated from the
  Tamil script: a letter with a pulli is not a syllable);
- the sound craft: monai (same first letter), etukai (same second letter) and iyaibu (same ending) between
  neighbouring lines, at least a few of them in the pallavi and charanam;
- the hook word repeats, and the gang has answers to shout;
- no written-Tamil words that read like an essay (a short list of the usual ones), one idea per line (no line with
  more than two commas).
The score is out of 100; the pass mark is 70.
"""
import json
import re
import sys

PART_WORDS = [  # (part, words in a section tag that name it), checked in this order
    ("thogaiyara", ("thogaiyara", "தொகையறா", "intro - free", "free rhythm")),
    ("anupallavi", ("anupallavi", "அனுபல்லவி", "pre-chorus", "pre chorus")),
    ("pallavi", ("pallavi", "பல்லவி", "chorus", "hook")),
    ("interlude", ("interlude", "இடையிசை", "dance break", "break", "drop")),
    ("charanam", ("charanam", "சரணம்", "verse")),
    ("bridge", ("bridge",)),
    ("ending", ("ending", "முடிவு", "outro")),
    ("prelude", ("prelude", "முன்னிசை", "intro")),
]
BOOKISH = ["அவர்கள்", "ஆகிறது", "ஆகும்", "இருக்கின்றன", "இருக்கிறது", "செய்கிறான்", "கொண்டிருக்கிறான்", "என்பது",
           "ஆனால்", "மேலும்", "எனவே", "அதனால்", "விளங்குகிறது", "திகழ்கிறது", "வருகிறான்", "பார்க்கிறான்"]
PULLI = "்"
LETTER = re.compile(r"[அ-ஹ]")


def part_of(tag):
    t = tag.lower()
    for part, words in PART_WORDS:
        if any(w in t for w in words):
            return part
    return "other"


def sections(lyrics):
    out = []
    for raw in lyrics.splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith("["):
            out.append({"tag": s, "part": part_of(s), "lines": []})
        elif out:
            out[-1]["lines"].append(s)
    return out


def sung_text(line):
    return re.sub(r"\([^)]*\)", " ", line).strip()


def letters(word):
    """Tamil letters of a word as (consonant-or-vowel, has_pulli)."""
    out = []
    for i, ch in enumerate(word):
        if LETTER.match(ch):
            out.append((ch, i + 1 < len(word) and word[i + 1] == PULLI))
    return out


def syllables(line):
    n = 0
    for w in sung_text(line).split():
        ls = letters(w)
        if ls:
            n += sum(1 for _, pulli in ls if not pulli)
        elif re.search(r"[A-Za-z]", w):
            n += max(1, len(re.findall(r"[aeiouy]+", w.lower())))
    return n


def first_word(line):
    ws = [w for w in sung_text(line).split() if letters(w)]
    return ws[0] if ws else ""


def monai(a, b):
    la, lb = letters(first_word(a)), letters(first_word(b))
    return bool(la and lb and la[0][0] == lb[0][0])


def etukai(a, b):
    la, lb = letters(first_word(a)), letters(first_word(b))
    return bool(len(la) > 1 and len(lb) > 1 and la[1][0] == lb[1][0])


def ending(line):
    ws = [w for w in re.sub(r"[!?,.…]", " ", sung_text(line)).split() if letters(w)]
    if not ws:
        return ""
    return "".join(c for c, _ in letters(ws[-1])[-2:])


def iyaibu(a, b):
    ea, eb = ending(a), ending(b)
    return bool(ea and ea == eb)


def inline_monai(line):
    ws = [letters(w) for w in sung_text(line).split() if letters(w)]
    return sum(1 for x, y in zip(ws, ws[1:]) if x[0][0] == y[0][0])


def check(song):
    secs = sections(song["lyrics"])
    find, score = [], 100
    parts = [s["part"] for s in secs]
    pal = [s for s in secs if s["part"] == "pallavi"]
    if len(pal) < 2:
        find.append(f"the pallavi (hook) appears {len(pal)} time(s); it should come back at least twice (-20)")
        score -= 20
    if pal and parts.index("pallavi") > 3:
        find.append("the pallavi comes late; put it within the first three parts, about 15-25 s in (-10)")
        score -= 10
    if "charanam" not in parts:
        find.append("no charanam (story verse) (-15)")
        score -= 15
    if "ending" not in parts:
        find.append("no ending part (-5)")
        score -= 5
    if pal:
        p0 = [l for l in pal[0]["lines"]]
        if not 2 <= len(p0) <= 8:
            find.append(f"the first pallavi has {len(p0)} lines; 2-8 sung rows (2-4 lines plus answers) (-10)")
            score -= 10
        title = song.get("title", "").split("(")[0].strip(" !")
        if title and p0 and title.split()[0] not in p0[0]:
            find.append("the pallavi's first line does not carry the title (-10)")
            score -= 10
    long_lines = []
    for s in secs:
        rap = "rap" in s["tag"].lower()
        limit = 20 if rap else 14
        for l in s["lines"]:
            n = syllables(l)
            if n > limit:
                long_lines.append(f"{n} syllables ({'rap' if rap else 'sung'}, max {limit}): {sung_text(l)}")
    if long_lines:
        find.append(f"{len(long_lines)} line(s) too long to sing clearly (-3 each, at most -15):")
        find += ["    " + x for x in long_lines]
        score -= min(15, 3 * len(long_lines))
    craft = {"monai": 0, "etukai": 0, "iyaibu": 0}
    for s in secs:
        if s["part"] not in ("pallavi", "anupallavi", "charanam", "bridge", "thogaiyara"):
            continue
        ls = [l for l in s["lines"] if sung_text(l)]
        for a, b in zip(ls, ls[1:]):
            craft["monai"] += monai(a, b)
            craft["etukai"] += etukai(a, b)
            craft["iyaibu"] += iyaibu(a, b)
        craft["monai"] += sum(inline_monai(l) for l in ls)
    if sum(craft.values()) < 6:
        find.append(f"little sound craft: monai {craft['monai']}, etukai {craft['etukai']}, iyaibu {craft['iyaibu']}; "
                    "aim for 6 or more across the pallavi and charanam (-10)")
        score -= 10
    hook = first_word(pal[0]["lines"][0]) if pal and pal[0]["lines"] else ""
    if hook and song["lyrics"].count(hook) < 4:
        find.append(f"the hook word '{hook}' is heard fewer than 4 times (-5)")
        score -= 5
    if "(" not in song["lyrics"]:
        find.append("no gang answers in brackets; kuthu needs call-and-response (-5)")
        score -= 5
    bookish = sorted({w for w in BOOKISH if w in song["lyrics"]})
    if bookish:
        find.append(f"written-Tamil words that read like an essay, use the spoken form: {', '.join(bookish)} (-3 each)")
        score -= 3 * len(bookish)
    crowded = [sung_text(l) for s in secs for l in s["lines"] if sung_text(l).count(",") > 2]
    if crowded:
        find.append(f"{len(crowded)} line(s) with more than one idea (3+ commas): split them (-2 each)")
        score -= 2 * len(crowded)
    return max(0, score), find, craft, parts


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    song = json.load(open(sys.argv[1]))
    score, find, craft, parts = check(song)
    print(f"lyrics score {score}/100 (pass 70)")
    print("parts: " + " > ".join(parts))
    print(f"sound craft: monai {craft['monai']}, etukai {craft['etukai']}, iyaibu {craft['iyaibu']}")
    for f in find:
        print(("- " if not f.startswith("    ") else "") + f)
    sys.exit(0 if score >= 70 else 1)


if __name__ == "__main__":
    main()
