---
name: kural-daily
description: Make and schedule today's Super Kural Shorts - the next Thirukkural as a short doodle story, one video per channel in config.json (a kids' version for Kiddo Corner, an all-ages version for the adult channel), the AI voice checked word by word, original music, uploaded and scheduled. Use for "make today's kural", "run the daily kural", or when a scheduled task asks for the daily Super Kural.
---

# Super Kural, daily

Every day, the next kural for each channel in `videos/kural/config.json` → `channels`. Today
that is only `kids` (Kiddo Corner, made for kids); a channel with `"audience": "all"` would get
an all-ages version, not made for kids. Each channel keeps its own count. Everything lives in `videos/kural/`; read its README
if something here is unclear. Work from the repository root.

**This run makes and uploads one video per channel, no more. Do not commit, push or open pull
requests, and leave the repository's files as they are.** Write each story outside the
repository, at `$KURAL_HOME/stories/CHANNEL-NNNN.json` (if `videos/kural/stories/NNNN.json`
already exists and fits that channel, copy it there and work on the copy).

## 1. Ready the container

```bash
for v in YT_CLIENT_ID YT_CLIENT_SECRET YT_REFRESH_TOKEN HF_TOKEN; do [ -n "${!v:-}" ] || echo "missing $v"; done
bash videos/kural/setup.sh && source ~/.cache/super-kural/env.sh && mkdir -p "$KURAL_HOME/stories"
```

If a variable is missing or setup fails, stop and report exactly that, in one or two lines: the
owner adds it in the cloud environment's settings. Never ask for a key in chat, and never print
one.

## 2. For each channel: which kural

Do steps 2 to 4 for each channel in config.json. Skip a channel, and say why in the report, when:
- `next.py` exits with status 3 (no `channel_id` yet), 2 (the series is finished there) or 4
  (neither the channel's feed nor its pages could be read; never guess a number instead);
- its `refresh_token_env` is not set;
- its audience is `all` and `voice_engine` in config.json is not `qwen` (the all-ages intro is
  recorded only in that voice).

```bash
python3 videos/kural/next.py CHANNEL  # {"kural": N, "publish_at": "...Z" or null, "last_on_channel": M}
python3 videos/kural/show.py N        # the couplet, its chapter, two old English translations
```

`next.py` reads that channel's public feed and its Shorts and Videos pages, so a failed day is
simply retried.

## 3. Write the story: `$KURAL_HOME/stories/CHANNEL-NNNN.json`

Copy the shape of `videos/kural/stories/0003.json`. The two channels get **different stories**
about the same idea, written for their audience (the channel's `audience` in config.json):

- **`kids`: children aged 4 to 10** and the grown-ups watching with them. Kid characters and a
  child's world: home, school, friends, grandparents, animals. The upload is marked made for kids.
- **`all` (the adult channel): adults and families.** Grown-up characters (man, woman, mom, dad,
  grandma, grandpa, teacher) in grown-up situations: work, home, money, neighbours, friendship,
  patience, honesty. A warm, thoughtful tone, not baby talk, and nothing aimed at young children
  (no "little friends", no toys). Still clean enough for a family to watch together. It is
  marked not made for kids, which is honest only if the story really is for everyone.

For both:
- **Meaning first.** Work out what the kural really says from the Tamil and both translations.
  `meaning` is that, in plain English anyone understands: at most 25 words, in one or two short
  sentences. Do not invent a meaning the translations do not support.
- **The hook decides the Short.** Line 1's first sentence is the hook: **9 words or fewer**, said
  in under three seconds, talking to the viewer or asking what they want answered ("Can you
  guess why Grandma never gets angry?"). Never open on a greeting or "today's story". Write three
  hooks in a file, one per line, score them, and use the best:
  `python3 .claude/skills/yt-script/hookscore.py hooks.txt`. It must score **40 or more** (flat
  openers score about 30). Line 1 is 16 words at most.
- **Loop back.** The `lesson` repeats a word from the hook, so the end leads into the replay
  ("...and you will smile like Grandma").
- **A tiny story** that shows the meaning: 4 or 5 `lines`, each one or two short sentences
  (at most 40 words). Simple, everyday English. 80 to 150 words for all lines, the meaning and
  the lesson together. `make.py` checks the hook length, its score, the loop and the meaning
  length, and says what to fix.
- **Clear words only.** The voice is checked word by word, so avoid rare words, Tamil words and
  hard names. Names that pass the check: Meena, Ravi, Arun, Priya, Anu, Kavin, Divya. List
  the names you use in `names`. Use Grandma, Grandpa, Mom, Dad, Teacher (not Paati, Thatha, Amma,
  Appa). Do not say "Kural" or "Thiruvalluvar" in your lines: the fixed intro, "Now listen to what
  the great poet Thiruvalluvar says." and the goodbye are added for you, already approved.
- **Family-safe always.** Kurals about war, rulers, spies, wealth or vice still get a gentle story
  about the same value (fairness, honesty, staying away from bad company). No violence, fear,
  romance, alcohol or gambling on screen. Chapter 92 and the whole book of Love (from kural 1081)
  are not for these channels: `last_kural` in config.json stops the series at 1080.
- **Respectful.** Chapter 1 praises God; keep it simple and not tied to one religion.
- `lesson` (spoken, at most 20 words) and `lesson_short` (on screen, at most 44 characters).
- `title`: under 45 characters, a question or promise a viewer would tap ("Why Is Grandma Always
  Smiling?" for kids, "The Boss Who Never Got Angry" for all ages). No clickbait, no emoji.

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
- `kid` (top level) is the main character on the intro, kural and lesson boards: a child for
  `kids`, an adult (usually `man` or `woman`) for `all`. `lesson_draw` is the drawing over the lesson.

## 4. Make, check, upload

```bash
cd videos/kural && python3 make.py "$KURAL_HOME/stories/CHANNEL-NNNN.json" --channel CHANNEL \
  --publish-at PUBLISH_AT   # or --public when publish_at is null
```

`make.py` checks the spec, voices each line and listens to it with Whisper **without the script**,
so a word that is not crystal clear fails. It tries six voices per line. If it stops with "NOT
CLEAR", reword the lines it names (simpler or more common words, shorter sentences) and run the
same command again; lines that already passed are kept. After three rewordings, stop that
channel and report. The finished mix is listened to again, with the music turned down if it
hides any word.

Then look at the stills it saved (`$KURAL_WORK/CHANNEL/NNNN/still_*.png`; open them with the Read
tool). If a drawing covers words or sits off the board, move it in the spec and run again. When
they look right, upload:

```bash
python3 ../doodle/upload.py "$KURAL_OUT/super_kural_CHANNEL_NNNN.upload.json"
```

It goes up with that channel's key, marked as AI voice, made for kids only for `kids`, and
private until `publish_at` (17:30 India time), so the owner can watch it in YouTube Studio first.
A run after about 16:30 has no `publish_at` and uses `--public`: the video goes public straight
away, so the next morning's run finds it on the channel instead of making the same kural again.

## 5. Report

A few lines per channel: kural number and title, the YouTube link, when it goes public, anything
you had to reword, or why the channel was skipped. If an upload failed, the error and what the
owner needs to do.
