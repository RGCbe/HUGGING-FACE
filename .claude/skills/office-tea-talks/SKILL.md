---
name: office-tea-talks
description: Make and schedule the next Office Tea Talks Short - a 40-60 second Tamil office / IT life lesson told as our own story with invented characters, in the owner's AI voice, our own doodles, Tamil captions and beat, built from what the top Tamil work videos are talking about (their points, never their words), checked for a clear voice, uploaded private and scheduled. Use for "run Office Tea Talks", "make today's office short", or when a scheduled task asks for an Office Tea Talks run.
---

# Office Tea Talks: one run

The owner's channel of Tamil office / IT life lessons (videos/office/README.md: why, and what is never done). Each run
makes `config.json` "per_run" Shorts (1): the hottest office theme right now, what the top videos on it are saying,
and a NEW story of ours that carries one of those points as its lesson. The worked example is `videos/office/example/`
("காலை 6 மணி layoff mail", 43 s): read its `script_ta.txt`, `shots.json`, `images.json` first.

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
for v in YT_CLIENT_ID_MOVIES YT_CLIENT_SECRET_MOVIES YT_REFRESH_TOKEN_OFFICE YT_CLIENT_ID YT_CLIENT_SECRET YT_REFRESH_TOKEN_ADULT ELEVENLABS_API_KEY HF_TOKEN; do
  [ -n "${!v:-}" ] || echo "missing $v"; done
sudo apt-get install -y -q ffmpeg fluidsynth fluid-soundfont-gm >/dev/null 2>&1 || apt-get install -y -q ffmpeg fluidsynth fluid-soundfont-gm
pip install -q numpy soundfile pillow -r videos/kural/requirements-whisper.txt
```

A missing variable: stop and report it in one line. Check the ElevenLabs balance (GET
https://api.elevenlabs.io/v1/user/subscription): under 3,000 characters left, stop and report.

## 2. When, and what was already told

`python3 videos/office/next.py` gives `publish_at` and the channel's recent titles and themes.

## 3. The theme and its points

1. `python3 videos/office/trends.py --out $WORK/trends.json`: themes ranked by median views, each with its top videos.
2. Take the highest theme not told in the last 3 days (next.py "recent").
3. Read the spoken text of its top 3 to 5 videos with the video-transcript connector (the `videos_transcript` tool; the
   cloud machine cannot download from YouTube itself). Write `$WORK/points.md`: 4 to 6 POINTS in your own words (what
   worries or helps viewers), each with the video it came from. No quotes. If the connector is not there, use the
   titles alone and say so in the report.
4. Pick ONE point that has not been a lesson on the channel yet (next.py titles) and invent a story for it.

## 4. Script: `$WORK/script_ta.txt`

5 to 7 lines, 80 to 120 words, spoken Tamil the way Chennai office people talk; office words stay English (mail,
manager, appraisal, layoff, skill, meeting). Every line starts with an emotion tag (`[serious]`, `[sad]`, `[warm]`,
`[curious]`, `[funny]`, `[excited]`, `[shocked]`). The shape (videos/SCRIPT_STYLE.md, "Shorts that travel"):

1. The moment, with a concrete detail ("காலை ஆறு மணி. கார்த்திக் போனைப் பார்க்கிறான்…").
2-4. What happened, short sentences, one small surprise or a little humour.
5. The lesson in one line ("பாடம் இதுதான்…").
6. A question for the comments ("உங்க ஆபீஸ்ல இப்படி நடந்திருக்கா? கமெண்ட்ல சொல்லுங்க.").

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
{"defaults": {"refresh_token_env": "YT_REFRESH_TOKEN_OFFICE", "client_id_env": "YT_CLIENT_ID_MOVIES",
              "client_secret_env": "YT_CLIENT_SECRET_MOVIES", "made_for_kids": false, "ai_content": true,
              "category_id": 22, "privacy": "private", "language": "ta"},
 "videos": [{"file": "...out/ta/video.mp4", "title": "...", "description": "...", "tags": [...],
             "publish_at": "<publish_at>"}]}
```

- Title: under 60 characters, the moment as a hook with English office words, an emoji first is fine, ending
  `#shorts` ("6 AM Layoff Mail 😨 கார்த்திக் என்ன பண்ணான்? #shorts").
- Description: two Tamil lines with the lesson; "இது ஒரு கற்பனைக் கதை. கதாபாத்திரங்கள் கற்பனையானவை." (a story,
  invented characters); "குரல்: என் சொந்தக் குரலின் AI நகல். படங்கள் AI மூலம் வரையப்பட்டவை, இசை எங்களுடையது.";
  a line `Theme: <the trends.py theme>` (next.py reads it); 3 hashtags (#officelife #tamil #shorts).
- Tags: config.json "tags_always" plus the theme's words.

`python3 videos/doodle/upload.py $WORK/upload.json`

## 10. Report

A few lines: the theme and the point used, the title, the link and when it goes public (India time), the clarity
numbers, what was redone, anything that failed.
