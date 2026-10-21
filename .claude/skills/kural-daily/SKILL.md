---
name: kural-daily
description: Make and schedule today's Super Kural Short for the Kiddo Corner channel - the next Thirukkural as a short doodle story, the AI voice checked word by word, original music, uploaded and scheduled. Use for "make today's kural", "run the daily kural", or when a scheduled task asks for the daily Super Kural.
---

# Super Kural, daily

One Short a day, one kural at a time, in order. Everything lives in `videos/kural/`; read its
README if something here is unclear. Work from the repository root.

**This run makes and uploads one video. Do not commit, push or open pull requests, and leave the
repository's files as they are.** Write the day's story outside the repository, at
`$KURAL_HOME/stories/NNNN.json` (if `videos/kural/stories/NNNN.json` already exists, copy it there
and work on the copy).

## 1. Ready the container

```bash
for v in YT_CLIENT_ID YT_CLIENT_SECRET YT_REFRESH_TOKEN HF_TOKEN; do [ -n "${!v:-}" ] || echo "missing $v"; done
bash videos/kural/setup.sh && source ~/.cache/super-kural/env.sh
```

If a variable is missing or setup fails, stop and report exactly that, in one or two lines: the
owner adds it in the cloud environment's settings. Never ask for a key in chat, and never print
one.

## 2. Which kural

```bash
python3 videos/kural/next.py          # {"kural": N, "publish_at": "...Z" or null, "last_on_channel": M}
python3 videos/kural/show.py N        # the couplet, its chapter, two old English translations
```

`next.py` reads the channel's public feed, so a failed day is simply retried. Exit status 2 means
the series is finished: report that and stop.

## 3. Write the story: `$KURAL_HOME/stories/NNNN.json`

Copy the shape of `videos/kural/stories/0003.json`. Who it is for depends on `audience` in
`videos/kural/config.json`:

- **`"all"`: adults and families.** Grown-up characters (man, woman, mom, dad, grandma, grandpa,
  teacher) in grown-up situations: work, home, money, neighbours, friendship, patience, honesty.
  A warm, thoughtful tone for anyone, not baby talk, and nothing aimed at young children (no
  "little friends", no toys or cartoons-for-toddlers framing). Still clean enough for a family
  to watch together. The upload is marked not made for kids, which is honest only if the story
  really is for everyone. Set `kid` (below) to an adult, usually `man` or `woman`.
- **`"kids"`: children aged 4 to 10** and the grown-ups watching with them. Kid characters and a
  child's world. The upload is marked made for kids.

- **Meaning first.** Work out what the kural really says from the Tamil and both translations.
  `meaning` is that, in plain English anyone understands, at most 30 words. Do not invent a
  meaning the translations do not support.
- **A tiny story** that shows the meaning: 4 or 5 `lines`, each one or two short sentences
  (at most 40 words). Line 1 is the hook: a question or a surprise the viewer wants answered.
  Simple, everyday English. 80 to 150 words for all lines, the meaning and the lesson together.
- **Clear words only.** The voice is checked word by word, so avoid rare words, Tamil words and
  hard names. Names that pass the check: Meena, Ravi, Arun, Priya, Anu, Kavin, Divya. List
  the names you use in `names`. Use Grandma, Grandpa, Mom, Dad, Teacher (not Paati, Thatha, Amma,
  Appa). Do not say "Kural" or "Thiruvalluvar" in your lines: the fixed intro, "Now listen to what
  the great poet Thiruvalluvar says." and the goodbye are added for you, already approved.
- **Family-safe always.** Kurals about war, rulers, spies, wealth or vice still get a gentle story
  about the same value (fairness, honesty, staying away from bad company). No violence, fear,
  romance, alcohol or gambling on screen. Chapter 92 and the whole book of Love (from kural 1081)
  are not for this channel: `last_kural` in config.json stops the series at 1080.
- **Respectful.** Chapter 1 praises God; keep it simple and not tied to one religion.
- `lesson` (spoken, at most 20 words) and `lesson_short` (on screen, at most 44 characters).
- `title`: under 45 characters, a question or promise a viewer would tap, e.g. "Why Is Grandma
  Always Smiling?" or "The Boss Who Never Got Angry". No clickbait, no emoji.

**Boards.** Each line has a `board`: 1 to 5 items, drawn as the words are spoken.

| Item | Fields |
| --- | --- |
| `{"draw": NAME, "at": PLACE}` | `mood`, `arms`, `color`, `flip` (face left), `scale`, `cue`; `tree` takes `fruit`, `mango` takes `ripe: false`, `cloud` takes `rain: true` |
| `{"text": "...", "at": PLACE}` | `color`, `size`, `cue` (a few words; it is handwritten) |
| `{"bubble": "...", "at": PLACE}` | a speech bubble above the person at PLACE, at most 4 words |
| `{"stamp": "...", "at": PLACE}` | `color`; one or two words, e.g. "YES!", "KIND" |
| `{"arrow": [PLACE, PLACE]}` | `color` |

- People: kid, boy, girl, grandma, grandpa, mom, dad, teacher, man, woman, sage.
- Things: tree, mango, flower, lotus, sun, moon, star, cloud, river, hill, bird, dog, cat, cow,
  fish, elephant, peacock, house, school, temple, shop, well, book, palmleaf, lamp, ball, kite,
  bag, pencil, plate, leaf, pot, gift, heart, clock, phone, bicycle, boat, bench, money, bulb,
  coin, trophy, medal, check, cross, burst, face.
- Places: left, center, right stand on the ground (use them for people and big things);
  top-left, top, top-right, middle-left, middle, middle-right, bottom float.
- Moods: happy, sad, angry, surprised, laugh, calm, worried. Arms: down, up, wave, point, give,
  hips, pray. Colors: red, blue, green, orange, yellow, brown, grey, pink, purple, black.
- `cue` is a word or phrase from that line; the item appears when it is spoken. Do not cue the
  last two or three words of a line: the board moves on right after them. One drawing per place
  per board. A person at left and right with something in the middle reads best.
- `kid` (top level) is the main character who appears on the intro, kural and lesson boards (any
  person: an adult for `"all"`, a child for `"kids"`); `lesson_draw` is the drawing over the lesson.

## 4. Make, check, upload

```bash
mkdir -p "$KURAL_HOME/stories"
cd videos/kural && python3 make.py "$KURAL_HOME/stories/NNNN.json" --publish-at PUBLISH_AT   # or --public when publish_at is null
```

`make.py` checks the spec, voices each line and listens to it with Whisper **without the script**,
so a word that is not crystal clear fails. It tries six voices per line. If it stops with "NOT
CLEAR", reword the lines it names (simpler or more common words, shorter sentences) and run the
same command again; lines that already passed are kept. After three rewordings, stop and report.
The finished mix is listened to again, with the music turned down if it hides any word.

Then look at the stills it saved (`$KURAL_WORK/NNNN/still_*.png`; open them with the Read tool).
If a drawing covers words or sits off the board, move it in the spec and run again. When they
look right, upload:

```bash
python3 ../doodle/upload.py "$KURAL_OUT/super_kural_NNNN.upload.json"
```

It goes up marked as AI voice, made for kids or not as config.json `audience` says, and private
until `publish_at` (17:30 India time),
so the owner can watch it in YouTube Studio first. A run after about 16:30 has no `publish_at`
and uses `--public`: the video goes public straight away, so the next morning's run finds it on
the channel instead of making the same kural again.

## 5. Report

A few lines: kural number and title, the YouTube link, when it goes public, anything you had to
reword. If the upload failed, the error and what the owner needs to do.
