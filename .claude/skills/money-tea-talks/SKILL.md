---
name: money-tea-talks
description: Make and schedule the next Money Tea Talks Short on the Tea Break channel - a 45-60 second Tamil money lesson (saving, credit cards, EMIs, salary, scams) told as a story with two invented people and the numbers worked out on screen, in the owner's AI voice, flat vector style with the owner's flat host, every number computed by code and every fact sourced, education only (never advice), uploaded private and scheduled for the next Tuesday or Friday 13:00 India time, with YouTube's automatic English dub. Use for "run Money Tea Talks", "make the next finance Short", or when a scheduled task asks for a Money Tea Talks run.
---

# Money Tea Talks: one run

Finance Shorts on the owner's **Tea Break with Manoj** channel, in their own playlist "Money Tea Talks | பணக்
கதைகள்" (the owner, 27 Nov 2026: "now add finance genre", "not doodle style", "new playlist", "lets upload in
tamil and use the multi language option", "KEEP AUTODUB"). Read `videos/money/README.md` first. The worked example is
`videos/money/example/`: `script_ta.txt`, `spec.json` and `upload_text.json` are the SHAPE of what you write, never
its sentences. Its Short: https://youtu.be/fGHpCb6ufds.

**Do not commit or push in a scheduled run. Never print a key.** Work in `$WORK=$HOME/money/SLUG/`, outside the
repository.

## The rules that are never broken

- **Education, never advice** (SEBI limits unregistered creators to investor education): no stock, fund, app, bank
  or broker names; no "buy", "invest in", "best plan"; no live prices; no promised returns; no promotions. Every rate
  is said and shown as an example ("12% ஒரு உதாரணம், உத்தரவாதம் இல்லை").
- **Every number is computed by Python** in `$WORK/numbers.py` (printed, kept with the work). The script, the spec
  and the description use exactly those numbers, rounded the same way everywhere.
- **Every fact is sourced** in two good sources (RBI, NPCI, SEBI, a bank's own schedule of charges, a government
  page) before the script is written: the topic's `facts` in `videos/money/topics.json`. Keep them in
  `$WORK/sources.json` and list them in the description. A fact you cannot source is cut, never guessed.
- The two people are invented (a name, an age, a job) and the description says it is a story. A little funny, never
  mocking the one who chose badly; the lesson is kind and practical.
- Never download, clip or quote anyone's video or audio.
- Everything on screen stays inside the Shorts clear band (`build.py` checks it and stops otherwise).

## 1. Ready the container

```bash
for v in YT_CLIENT_ID YT_CLIENT_SECRET YT_REFRESH_TOKEN_ADULT ELEVENLABS_API_KEY HF_TOKEN; do
  [ -n "${!v:-}" ] || echo "missing $v"; done
sudo apt-get install -y -q ffmpeg >/dev/null 2>&1 || apt-get install -y -q ffmpeg
pip install -q numpy soundfile pillow huggingface_hub -r videos/kural/requirements-whisper.txt -r videos/doodle/requirements-motion.txt
```

## 2. The slot and the topic

`python3 videos/money/next.py`. If `too_far_ahead` is true, enough is scheduled: stop and report one line (the next
Short's date). Otherwise `publish_at` is this Short's time and `topic` its topic (`slug`, the 4 steps, the facts).
If `topic` is null, every topic is used: stop and tell the owner the list needs new topics.

Check the ElevenLabs balance (GET https://api.elevenlabs.io/v1/user/subscription): if fewer than config.json
`eleven_min_chars` characters are left, stop and report.

## 3. Facts and numbers

1. Source each of the topic's `facts` (web search, then read the page itself; two sources that agree). Write
   `$WORK/sources.json`: `[{"fact", "value", "sources": [url, url]}]`.
2. Write `$WORK/numbers.py`: every figure the Short says or shows (amounts, months, differences), from the sourced
   facts and the example rates, printed. Run it. Indian style: ₹ with lakh and crore ("₹38 லட்சம்", "₹1.30 கோடி").

## 4. The script: `$WORK/script_ta.txt`

One line per scene, said by one voice, 7 to 9 lines, about 110 to 150 words in all:

1. **Hook** (over the result: the finished chart or the punchline card): the surprising number and the question.
   Never the host in the first shot.
2. **The host asks** (host, think pose): a short line, "என்ன வித்தியாசம் தெரியுமா?" style.
3. **Story** (2 or 3 picture lines): each person's choice, in everyday spoken Tamil. Invent new names each time.
4. **Proof** (one bars, cards or rule line): name the example rate, then the result as it lands.
5. **Punchline** (cards): the one difference that matters.
6. **Lesson + question** (host, comment pose): the lesson in one line, then a question for the comments.

Spoken Tamil the way people talk (videos/SCRIPT_STYLE.md), numbers as Tamil words ("ரெண்டாயிரம்"), an emotion tag
where it helps (`[curious]`, `[funny]`, `[warm]`, `[excited]`, `[serious]`). No "..." (the voice stops).

In `$WORK/spec.json` also write `lines` (each line as a caption, with digits and ₹) and `en` (the same lines in
plain English, for the English subtitles).

## 5. Voice and the listening check

```bash
python3 -I videos/kural/eleven.py $WORK/script_ta.txt $WORK/voice_ta --sections 1,2,...,N --stability 0.5 --similarity 0.9
python3 videos/money/check_voice.py $WORK     # every line Tamil (p >= 0.8); writes $WORK/words.json
```

Read the printed text against the script: the first and last words must be there. A line that fails: reword it or
voice it again with `--seed 8` (two tries, then stop and report).

## 6. Pictures: `$WORK/pics/images.json`

`videos/doodle/imagegen.py $WORK/pics/images.json $WORK/pics --engine auto`, 9:16, `"style"` = config.json `style`,
one picture per story line (3 or 4). Describe each person the same way in every prompt (age, hair, clothes; the older
version of a person is made with `"edit"` from the younger one). Money is Indian rupee notes (lavender ₹100, never
green dollars). No text, logos or real people. Look at every picture (a contact sheet, opened with Read); fix a small
thing with `videos/doodle/patch_edit.py`, remake anything else.

For each person who appears in a bars scene, note the centre and radius of their face in their picture
(`"face": [cx, cy, r]`) for the round avatar.

## 7. The spec and the build

`$WORK/spec.json` like the example: one scene per script line, in order. Scene kinds and their fields are in the
docstring of `videos/money/build.py`: `bars` (two people saving the same amount from different ages), `cards` (the
punchline numbers, counting up to the word that says them), `rule` (a rule card that builds up), `picture`, `host`.
Times can be `"word:XYZ"` (when the line says its first word starting with XYZ, from words.json; use the spelling
Whisper printed). A topic whose proof none of the kinds fits uses `cards` or `rule`; a new kind is added to build.py
only in a session with the owner, never in a scheduled run.

```bash
python3 videos/money/build.py $WORK                  # $WORK/out/video.mp4, subs_ta.srt, subs_en.srt
python3 videos/doodle/clarity.py $WORK/out/video.mp4  # CLEAR, or nothing is uploaded
```

Make a contact sheet of one frame per scene (and the moment each number lands) and look at it with Read: the
numbers on screen equal numbers.py's, the Tamil letters are joined, nothing overlaps. The length is 40 to 60 seconds.

## 8. Keep the work files

Upload `$WORK` (not `out/*.png`) to the PRIVATE dataset config.json `dataset` under `money/SLUG/` with HF_TOKEN
(refuse if the dataset is not private).

## 9. Upload, private and scheduled

`$WORK/upload.json` for `videos/doodle/upload.py`, like `example/upload_text.json`:

```json
{"defaults": {"meta": "tea-break", "privacy": "private", "made_for_kids": false, "ai_content": true,
              "category_id": 27, "language": "ta", "refresh_token_env": "YT_REFRESH_TOKEN_ADULT"},
 "videos": [{"file": "$WORK/out/video.mp4", "title": "<Tamil title, 40-70 characters, ends with #shorts>",
             "description": "<as the example>", "tags": ["<config tags_always + 3 topic tags>"],
             "publish_at": "<next.py publish_at>", "playlists": ["<videos/teabreak/config.json playlists.money.id>"],
             "localizations": {"en": {"title": "<English title, #shorts>", "description": "<English description>"}}}]}
```

The description, in this order: the story in two lines with its numbers; "பாடம்: ..."; "கணக்கு: ..." (the maths,
the example rate marked); "ஆதாரம்: ..." (the sources, if any facts); the line
`Money Tea Talks: பணம் பற்றிய பாடங்கள், சின்னக் கதைகளா, சரியான கணக்கோட.`; the line `Topic: SLUG` (next.py reads
it); "இது ஒரு கற்பனைக் கதை, கதாபாத்திரங்கள் கற்பனையானவை. கல்வி மட்டும், முதலீட்டு ஆலோசனை இல்லை."; the voice and
pictures note. The English description says the same.

`python3 videos/doodle/upload.py $WORK/upload.json` (with "meta" it also queues the Short for Facebook and
Instagram; the owner's VPS posts it at the same time). Then the subtitles:

```bash
python3 videos/money/subtitles.py VIDEO_ID $WORK/out
```

YouTube makes the English audio by itself (automatic dubbing, on for the channel).

## 10. Report

Topic, title, YouTube link, when it goes public (India time), the key numbers and their sources, what was redone
and why, and anything that failed.
