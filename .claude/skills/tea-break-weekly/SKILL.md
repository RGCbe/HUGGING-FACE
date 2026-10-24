---
name: tea-break-weekly
description: Make and schedule this week's Tea Break with Manoj videos - the next funny true history story from the topic list as a 3-5 minute illustrated doodle video plus two vertical Shorts, in Manoj's AI voice checked word by word, with original music and sound effects, uploaded private and scheduled. Use for "make this week's Tea Break video", "run the weekly Tea Break", or when a scheduled task asks for the weekly Tea Break run.
---

# Tea Break with Manoj, weekly

Every week, one long video (3 to 5 minutes) and two Shorts about the next story in
`videos/teabreak/topics.json`, for the channel in `videos/teabreak/config.json`. The long video
goes public on Saturday at 18:00 India time and the Shorts on the Monday and Wednesday after it.
The finished example to copy is The Pig War: its files are in `videos/teabreak/example/`
(`voiceover_en.txt`, `hooks.txt`, `images.json`, `scenes.js`, `thumbnail.js`, `shorts.json`,
`meta.json`, `caption_replace.json`). Work from the repository root.

**This run makes and uploads three videos, no more. Do not commit, push or open pull requests,
and leave the repository's files as they are.** Everything you write goes in
`$KURAL_WORK/SLUG/`, outside the repository.

## Who it is for, and how Manoj talks

- One person: a busy working adult watching in English on a phone, in a tea break or on the
  commute. Not a history expert. They want a true story that makes them laugh and that they can
  retell at work tomorrow.
- Simple, clear English only, no Tamil or Tanglish. Funny and casual, like telling a friend a
  story over tea. Short sentences, everyday words. The jokes come from the story; add one or two
  everyday comparisons ("just like a plan from your manager in a Monday meeting").
- The greeting is exactly "Hello friends, I'm Manoj." and it comes AFTER the hook, never first.
- Never "dive in", "game-changer", "unlock", "let's get into it", or other stiff phrases.
- **Every fact has a source you can name.** No made-up numbers, dates or quotes. Where the two
  sources give different numbers, use a number both allow ("about sixty-five soldiers" for 64 and
  66) or leave it out. A legend or a doubtful detail is called a legend, or left out.

## 1. Ready the container

```bash
for v in YT_CLIENT_ID YT_CLIENT_SECRET YT_REFRESH_TOKEN_ADULT HF_TOKEN CF_ACCOUNT_ID CF_API_TOKEN; do
  [ -n "${!v:-}" ] || echo "missing $v"; done
KURAL_HOME=$HOME/.cache/tea-break VOICE_ENGINE=qwen FIXED_CLIPS=0 bash videos/kural/setup.sh
source ~/.cache/tea-break/env.sh
```

(Use `voice_engine` from config.json for VOICE_ENGINE.) If a variable is missing or setup fails,
stop and report exactly that in one or two lines: the owner adds it in the cloud environment's
settings. Never ask for a key in chat, and never print one.

## 2. Which story

```bash
python3 videos/teabreak/next.py   # {"slug", "topic", "wikipedia", "more", "long_at", "shorts_at": [..], "uploaded"}
```

It reads every upload on the channel, scheduled and private ones too, and picks the first topic
not yet there, so a week that failed is simply made again. Exit status 2 means every topic is done:
stop and report that the owner should approve more topics. `mkdir -p "$KURAL_WORK/SLUG"`.

## 3. Research

Read the `wikipedia` page and a second reliable source: the topic's `more` page if it has one,
otherwise a museum, park service, university or encyclopaedia page found with WebSearch (WebFetch
both). Write `sources.md` in the video folder: every fact you will use, with where it came from.
Note where they disagree.

## 4. Write the script: `voiceover_en.txt`

One section per line, 14 to 16 lines, 25 to 65 words each, 550 to 650 words in all (about four
minutes). Spell every number as it is said ("eighteen fifty-nine", "two thousand one hundred and
forty"). No sound tags like [laugh]: the voice reads them out.

1. **Hook.** Write four or five hooks in a scratch file and score them:
   `python3 .claude/skills/yt-script/hookscore.py hooks.txt`. Use the best, at least 60
   (WORKABLE). What scores: "you" early, a date or number, a stake ("dead", "lose", "never"),
   and an open question at the end ("But how?"). The Pig War's: "Before you laugh, this is real
   history. In eighteen fifty-nine, one dead pig almost started a war between America and
   Britain. But how?" (69).
2. "Hello friends, I'm Manoj. In this video, I'll tell you how ..., what happened next, and who
   won in the end. Every word is true, and the sources are in the description."
3. The story in order, with 4 or 5 **punchlines**: a short line after a pause that makes the
   viewer laugh ("Over a pig.", "Happy anniversary.", "It was the alcohol.").
4. Answer the hook's question near the end ("So who won? ...").
5. Last line: "Do you know a funny true story like this, from your town or your family? Tell me in
   the comments. It could be my next video."

Also write:
- `hooks.txt`: two hook lines, one for each Short, each scored 55 or more, each about its Short's
  part of the story.
- `names.txt`: the names in the script, one per line (people, places), so the listening test
  accepts other spellings of them.
- `caption_replace.json`: `[["eighteen fifty-nine", "1859"], ["ten dollars", "$10"], ...]` so the
  captions show numbers as digits. Phrases must match the script's words exactly.

## 5. Voice

```bash
python3 videos/teabreak/build.py voice "$KURAL_WORK/SLUG"
```

It voices each line and listens to it with Whisper without the script; any word that is not
clear fails the line, and it tries six seeds. If it stops with "NOT CLEAR", reword the lines it
names (simpler, more common words; shorter sentences; a hard name said once less) and run it
again; pieces that passed are kept. After three rewordings, stop and report. About 30-50 minutes.
Run nothing else heavy while it works (another voice job, a video render): two such jobs on the
container's 4 cores each run about ten times slower.

## 6. Pictures: `images.json`, then `build.py images`

`{"characters": "...", "images": [{"name": "p01", "seed": 11, "prompt": "..."}, ...]}`, about
one picture per 10 seconds of voice (20 to 24). `characters` says exactly how each person,
animal and thing looks (clothes, hair, colours), so every picture draws them the same way. The
channel style (cream paper, ink outlines, the top third left empty for words, no text) is added
by build.py. Each prompt: who is where (left / middle / right), what they are doing, their faces;
whoever is described in `characters` tends to appear in every picture, so end each prompt with
"No pig, no animals." (or "No people", "no farmers") for anyone who must not be there, such as an
animal after it has died. No flags, no blood, no gore: a shot
or a battle is shown before or after, never the wound. The last picture is the tea table with a
cup and phone; `end.png` (the channel's end card) is added for you.

```bash
python3 videos/teabreak/build.py images "$KURAL_WORK/SLUG"
```

Look at every picture (make contact sheets with ffmpeg and open them with Read). Redo any with
extra limbs or doubled objects, a missing main subject, writing, a character who should not be
there, or anything that contradicts the story: delete the png, change its seed or sharpen its
prompt, and run the step again (finished pictures are kept). Cloudflare's free allowance is
10,000 neurons a day, about 70 pictures (a picture the safety filter blocks costs too, and is
retried with another seed). If the step stops with "the free daily quota is used up", run it
again every 10 minutes: pictures made the day before stop counting about 24 hours after they
were made.

## 7. Boards: `scenes.js`, then `build.py stills`

Copy the example's `scenes.js` and change the boards. One `scene(time, 'pNN', () => {...})` per
picture, timed with `c(section, 'words')` (the words must be in that line of the script).
Handwriting, stamps and calendars go in the empty top third (y up to about 300; the board is
1920x1080). `D.punch(c(n, 'words'))` before each punchline's big words: the music stops just
before it and comes back after. Keep `D.tail = 3` and the end card scene.

```bash
python3 videos/teabreak/build.py stills "$KURAL_WORK/SLUG"
```

Open every `stills/sheet_N.png`. Fix words that cover faces or each other, run off the board, or
are hard to read, and run it again until they are clean.

## 8. Video, thumbnail and Shorts

`thumbnail.js`: the funniest picture, at most four big words, and the year in a stamp (see the
example). Then:

```bash
python3 videos/teabreak/build.py video "$KURAL_WORK/SLUG"
```

`shorts.json`: two Shorts, each 35 to 55 seconds of the long video that makes sense on its own
(a setup and its punchline), found in `timing.json` (section offsets plus word times):

```json
[{"title": "THE PIG WAR (1859)", "subtitle": "One pig, two countries", "hook": 1,
  "segments": [{"from": 41.2, "to": 79.9}]}, ...]
```

`from` starts on a word's `t0` and `to` ends just after a word's `t1` (a punchline). Then:

```bash
python3 videos/teabreak/build.py shorts "$KURAL_WORK/SLUG"
```

Then the whole story as one vertical video for TikTok (TikTok pays only for videos over a
minute), from `meta.json`'s `tiktok` (write it now, see step 9):

```bash
python3 videos/teabreak/build.py tiktok "$KURAL_WORK/SLUG"
```

Watch for problems: open a few frames of each output (`ffmpeg -ss T -i out/X.mp4 -frames:v 1
f.png`) and check the lengths with ffprobe (long video 3-5 minutes; Shorts under 60 seconds).

## 9. Upload

`meta.json`:
- `title`: under 60 characters, the story's name people search for, then the hook ("The Pig War:
  When One Pig Nearly Started a War (1859)"). Score options with
  `python3 .claude/skills/yt-package/title.py titles.txt`.
- `description`: two sentences saying what happened, then `Sources:` (both links), `Chapters:`
  (from `timing.json` section offsets: the first at 0:00, at least 3, each at least 10 seconds
  long), a short paragraph of the story with the main names and numbers, and "Do you know a funny
  true story like this? Tell me in the comments." (build.py adds the AI note.)
- `tags`: 10 to 12, from what people search ("pig war", "pig war 1859", "funny history", ...).
- `long_at`, `shorts_at`: from next.py.
- `shorts`: a title (under 60 characters, ending in "#shorts") and a two-line description for each.
- `tiktok`: `title` (the story and year in capitals, "THE PIG WAR (1859)"), `subtitle` (at most
  five words, "One pig. Two countries."), and `caption`: one or two sentences that tease the story,
  an emoji, and 5 or 6 hashtags (#history #funnyhistory #truestory, the story's own, #learnontiktok).

```bash
python3 videos/teabreak/build.py upload "$KURAL_WORK/SLUG"
python3 videos/doodle/upload.py "$KURAL_WORK/SLUG/upload.json"
```

Everything goes up private, with YouTube's AI-content label, and goes public by itself at its
time, so the owner can watch it in YouTube Studio first. A custom thumbnail fails with 403 until
the channel's phone number is verified; that is not an error to fix, just report it.

## 10. Report

Send the owner the TikTok video (`out/SLUG_tiktok.mp4`) with SendUserFile, and the two Shorts
too, which they may also post on TikTok a few days later. Then a few lines: the story, the three
titles with their YouTube links and when each goes public (India time), the TikTok caption in a
block to copy (and a reminder to switch on "AI-generated content" under More options when
posting), anything you had to reword or redo, and anything that failed with what the owner needs
to do.
