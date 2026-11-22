---
name: office-tea-talks
description: Make and schedule the next Office Tea Talks Short on the Tea Break channel - a 40-60 second, slightly funny Tamil office / IT life lesson told as our own story with invented characters, in the owner's AI voice, our own doodles, Tamil captions and beat, built from what the top Tamil work videos are talking about (their points, never their words), checked for a clear voice, uploaded private and scheduled. Use for "run Office Tea Talks", "make today's office short", or when a scheduled task asks for an Office Tea Talks run.
---

# Office Tea Talks: one run

Tamil office / IT life lessons, posted on the owner's **Tea Break with Manoj** channel in their own playlist (the owner's
choice, 22 Nov 2026: "make it little funny and post in tea break channel"; videos/office/README.md: why, and what is
never done). Each run
makes `config.json` "per_run" Shorts (1): the hottest office theme right now, what the top videos on it are saying,
and a NEW, slightly funny story of ours that carries one of those points as its lesson. The worked example is
`videos/office/example/` ("6 மணிக்கு Layoff Mail 😅", 53 s, https://youtu.be/kP8JfuFd2P0): read its `script_ta.txt`,
`shots.json`, `images.json` first.

**Do not commit or push. Never print a key.** Work in `$WORK=$HOME/office/SLUG/`, outside the repository.

## The rules that are never broken

- Never download, clip, re-upload or quote anyone's video or audio. From other videos we take only their POINTS (what
  viewers care about), never their sentences, never anyone's personal story, never their sponsor or course pitches.
- Our characters are invented (a name, an age, a job) and the story is told as a story ("கார்த்திக்…"), never as the
  owner's own life. Every description says it is a story.
- No company names in a bad light, no real people, no numbers we cannot source (a theme video's statistics are not a
  source). The lesson is practical and kind: savings, skills, visibility, health, dignity; never "quit your job today".

## 1. Ready the container

```bash
for v in YT_CLIENT_ID YT_CLIENT_SECRET YT_REFRESH_TOKEN_ADULT ELEVENLABS_API_KEY HF_TOKEN; do
  [ -n "${!v:-}" ] || echo "missing $v"; done
sudo apt-get install -y -q ffmpeg fluidsynth fluid-soundfont-gm >/dev/null 2>&1 || apt-get install -y -q ffmpeg fluidsynth fluid-soundfont-gm
pip install -q numpy soundfile pillow -r videos/kural/requirements-whisper.txt
```

A missing variable: stop and report it in one line. Check the ElevenLabs balance (GET
https://api.elevenlabs.io/v1/user/subscription): under 3,000 characters left, stop and report.

## 2. When, and what was already told

`python3 videos/office/next.py` gives `publish_at` and the channel's recent titles and themes.

## 3. The theme and its point

1. `python3 videos/office/trends.py --out $WORK/trends.json`: the office themes ranked by median views right now.
2. `videos/office/points.json` is the points bank: what the top Tamil office videos are saying, in our own words, each
   with its theme. (It is refreshed every week in the owner's main session, where the video-transcript tool works; a
   scheduled run cannot read transcripts.)
3. If `videos/office/config.json` "queue" has a point id not yet used (next.py "used_points"), take the first such point
   (the owner's plan). Otherwise choose the highest-ranked theme that was not told in the last 3 days (next.py "recent")
   and has a point not yet used. If the `videos_transcript` tool happens to be available in this run, you may read the top
   2-3 videos of that theme and note a fresher point in `$WORK/points.md` (our words only); otherwise use the bank.
4. Invent a story that carries that point as its lesson. Write the point id in `$WORK/point.txt` (it goes in the
   description, so next.py knows it is used). All points used: invent a fresh angle on the hottest theme from its
   trends.py titles, and say so in the report.

## 4. Script: `$WORK/script_ta.txt`

5 to 7 lines, 80 to 120 words, spoken Tamil the way Chennai office people talk; office words stay English (mail,
manager, appraisal, layoff, skill, meeting). Every line starts with an emotion tag (`[serious]`, `[sad]`, `[warm]`,
`[curious]`, `[funny]`, `[excited]`, `[shocked]`). The shape (videos/SCRIPT_STYLE.md, "Shorts that travel"):

1. The moment, with a concrete detail ("காலை ஆறு மணி. கார்த்திக் போனைப் பார்க்கிறான்…").
2-4. What happened, short sentences, one small surprise or a little humour.
5. The lesson in one line ("பாடம் இதுதான்…").
6. A question for the comments ("உங்க ஆபீஸ்ல இப்படி நடந்திருக்கா? கமெண்ட்ல சொல்லுங்க.").

**A little funny (the owner's wish):** two or three light, relatable office jokes per story, Tea Break style: the office
coffee machine, the canteen, the "quick 5-minute call", the WhatsApp group, the manager's "we are a family", the laptop
that sees you more than your family does. Laugh at office absurdities, never at someone's pain, never at a real person
or company; the lesson line stays sincere. One or two pictures carry a visual joke (the example's smiling coffee machine
that is sad when he leaves). Tag those lines `[funny]`.

Numbers as Tamil words in the script, their digits in `shots.json` `caption_replace.ta`. No "..." (the voice stops).

## 5. Voice

```bash
python3 -I videos/kural/eleven.py $WORK/script_ta.txt $WORK/voice_ta --sections 1,2,... --stability 0.5 --similarity 0.9
```

Check with faster-whisper ("medium", CPU, int8) that every section is heard as Tamil (0.8 or more); otherwise reword or
`--seed 8` and voice that section again.

## 6. Pictures: `$WORK/pics/images.json`

`videos/doodle/imagegen.py $WORK/pics/images.json $WORK/pics --engine auto` (own Space first). 9:16, "style" =
config.json "style", "style_ref": "p01", 8 to 11 pictures (one per 4-5 seconds). The main character is described the
same way in every prompt (the example: "Karthik, a 30-year-old South Indian man with short black hair, a neat
moustache, a light blue formal shirt and a blank ID card on a lanyard"); invent a new one for each story (vary age,
gender, job). Look at every picture (a contact sheet, opened with Read); redo any with text, a logo, extra limbs, a
different-looking main character, or anything that does not match its line.

**The host (the owner's wish, 22 Nov 2026: "use my photo also"):** copy `videos/office/host/*.png` into `$WORK/pics/` and
use them as in the example's `shots.json`: `host_hello` as a short first shot (weight about 0.7) before the story's
first picture, `host_laugh` right after the funniest line (or `host_think` before the twist), and `host_comment` for
the last line, the comments question. He is the host who tells the story, never a character in it
(videos/office/host/README.md).

## 7. The video and the clarity check

`$WORK/shots.json` like the example (one section per script line: mood, pictures, caption_replace), then:

```bash
python3 videos/movies-explained/lore_video.py $WORK ta
python3 videos/doodle/clarity.py $WORK/out/ta/video.mp4      # must say CLEAR, or nothing is uploaded
```

Check frames (Tamil letters joined, captions readable) and the length (35-60 seconds).

## 8. Keep the work files

Upload `$WORK` to the PRIVATE Hugging Face dataset config.json "dataset" under `SLUG/` with HF_TOKEN (create it
private if missing; refuse if not private).

## 9. Upload, private and scheduled

`$WORK/upload.json` for `videos/doodle/upload.py`:

```json
{"defaults": {"refresh_token_env": "YT_REFRESH_TOKEN_ADULT", "client_id_env": "YT_CLIENT_ID",
              "client_secret_env": "YT_CLIENT_SECRET", "made_for_kids": false, "ai_content": true,
              "category_id": 27, "privacy": "private", "language": "ta"},
 "videos": [{"file": "...out/ta/video.mp4", "title": "...", "description": "...", "tags": [...],
             "publish_at": "<publish_at>", "playlists": ["<config.json playlist_id>"]}]}
```

- Title: under 60 characters, the moment as a hook with English office words and an emoji, ending `#shorts`
  ("6 மணிக்கு Layoff Mail 😅 நாம ஒரு Family-யா? #shorts").
- Only the Office Tea Talks playlist (config.json "playlist_id"): never Tea Break's history playlists, which promise
  every word is true.
- Description: two Tamil lines with the lesson; "இது ஒரு கற்பனைக் கதை. கதாபாத்திரங்கள் கற்பனையானவை." (a story,
  invented characters); "குரல்: என் சொந்தக் குரலின் AI நகல். படங்கள் AI மூலம் வரையப்பட்டவை, இசை எங்களுடையது.";
  a line `Theme: <the trends.py theme>` and a line `Point: <the point id>` (next.py reads both); 3 hashtags
  (#officelife #tamil #shorts).
- Tags: config.json "tags_always" plus the theme's words.

`python3 videos/doodle/upload.py $WORK/upload.json`

## 10. Report

A few lines: the theme and the point used, the title, the link and when it goes public (India time), the clarity
numbers, what was redone, anything that failed.
