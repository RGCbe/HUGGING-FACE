---
name: manoj-explains
description: Make and schedule the next Manoj Explains videos - Marvel and movie lore questions as vertical Tamil Shorts (English viewers get YouTube's automatic dub and translated titles), narrated by Manoj's 3D anime self, with only our own pictures, music and voice (no film clips, stills, posters, comic panels, logos or AI pictures of Marvel characters), checked, uploaded private and scheduled on the Manoj Explains channel. Use for "make this week's Manoj Explains videos", "run Manoj Explains", or when a scheduled task asks for a Manoj Explains run.
---

# Manoj Explains: one run

Each run makes the next `topics_per_run` questions (`videos/movies-explained/config.json`: 1, one a day, Manoj's choice) from
`videos/movies-explained/topics.json`. Every question becomes ONE Tamil video, a 30-60 second Short, 1080x1920, uploaded
private and scheduled at 8 pm India time (next_topic.py's `ta_at`) on the channel Manoj Explains (@manoj-d-explains).
**Tamil only** (the owner, 27 Nov 2026: "Both channel stop English"): no English video is voiced, made or uploaded;
the Tamil upload carries an English title and description plus the other `localize_to` languages, and YouTube's
automatic dubbing gives English viewers an English track. Until 27 Nov each question was also an English Short. The finished example is "Who is Doctor Doom?": `videos/movies-explained/videos/01-doctor-doom/`
(`script_en.txt`, `script_ta.txt`, `shots.json`, `sources.md`). Read `videos/movies-explained/PLAN.md` and
`PROCESS.md` once.

**Do not commit or push. Never print a key.** Work in `$WORK=$HOME/manoj-explains/SLUG/`, outside the repository.

## The rules that are never broken

- No film or trailer clips, stills, posters, comic panels, Marvel/Disney logos or title fonts, film music, actors'
  photos or faces, and no AI pictures of Marvel characters, their costumes, masks, shields or weapons. Characters
  appear only as a name card (the name as text) and as plain silhouettes, places and objects of our own design.
- Every fact has a source written in `sources.md` (official Marvel/Disney pages, Wikipedia, Variety, The Hollywood
  Reporter, Deadline). A theory is called a theory. Spoilers only once the plot is published, with "(spoilers)" in
  the title.
- Every description says: the pictures, music and voice are made with AI tools; this is a fan channel, not made by,
  linked to or endorsed by Marvel, Disney or any studio; and lists the sources.

## 1. Ready the container

```bash
for v in YT_CLIENT_ID_MOVIES YT_CLIENT_SECRET_MOVIES YT_REFRESH_TOKEN_MOVIES ELEVENLABS_API_KEY HF_TOKEN CF_ACCOUNT_ID CF_API_TOKEN; do
  [ -n "${!v:-}" ] || echo "missing $v"; done
sudo apt-get install -y -q ffmpeg fluidsynth fluid-soundfont-gm >/dev/null 2>&1 || apt-get install -y -q ffmpeg fluidsynth fluid-soundfont-gm
pip install -q numpy soundfile pillow -r videos/kural/requirements-whisper.txt -r videos/doodle/requirements-motion.txt
```

The pictures move in 3D (`videos/doodle/depthmove.py`, the owner's "ok", 23 Nov 2026): `lore_video.py` does this by
default when the libraries in `videos/doodle/requirements-motion.txt` are installed (line above). Otherwise it falls
back to plain zooms: say so in the report.

A missing variable: stop and report it in one line (Manoj adds it in the environment settings).

## 2. Which questions, and when

```bash
python3 videos/movies-explained/next_topic.py      # {"topics": [{slug, question, look, playlists, en_at, ta_at}], "uploaded": [...]}
```

Exit status 2: every topic is done; report that more topics are needed and stop. For a topic with `"made"` (already
made, like Doctor Doom), use its folder's files and the work files in the private dataset (step 8) instead of making
it again.

## 3. Research: `sources.md`

Read the topic's Wikipedia page(s) and one official or trade-press page (WebFetch, or the web-fetch agent;
Wikipedia's API may refuse direct requests from this machine). Write every fact you will use with its source.

## 4. Script

- **The format (the owner's choice, 21 Nov 2026, after studying the Tamil Marvel Shorts channels Tharamana Talks,
  583,000 subscribers, and Comic Kathai, 83,500, whose Shorts get about 200,000 views each at 30 to 60 seconds):**
  ONE sharp Why/How question about something viewers remember, answered in 30 to 50 seconds. Not a lore lecture.
  Read "Shorts that travel" in `videos/SCRIPT_STYLE.md` first.
- Plan the lines in English first in `script_en.txt` (never voiced now: it is the outline the Tamil script follows and
  the source of the English title and description): 4 to 6 lines, 80 to 120 words in all, each line starting with an emotion tag (`[curious]`,
  `[mysterious]`, `[excited]`, `[serious]`, `[shocked]`, `[sad]`, `[warm]`). Line 1: the question turned into a
  claim with a concrete detail (a number, a name, a scene everyone remembers), so the first 3 seconds promise the
  answer. Then the answer in 2 or 3 short beats, each with a fact from `sources.md` (a theory is called a theory).
  The last line: an open question with two answers, for the comments ("Worthy? Or did Thor let him? Tell me.").
  Short sentences. No greeting, no "in this video", no channel name: Manoj's anime self says it all. Write numbers
  as digits only where a person reads them that way (years: 2015).
- Score the first line: `python3 .claude/skills/yt-script/hookscore.py hooks.txt` with 3-4 tries; use one scoring
  60 or more. Never start two videos the same way.
- `script_ta.txt`: the same lines in spoken Tamil, the way Tamil Marvel fans talk, same tags. Clear to the ear
  (21 Nov 2026: the owner's friend found a Tamil Marvel channel's audio easier to follow, and it talks like this):
  Marvel words stay English ("power", "suit", "multiverse", "time travel", "revenge"); short numbers ("number 3",
  "5 second", "60 நிமிஷம்"); never a long Tamil year such as "ஆயிரத்துத் தொள்ளாயிரத்து அறுபத்திரெண்டுல": say "நைன்டீன்
  சிக்ஸ்டி டூல" or leave the year out. Numbers in words in the script, their digits in `shots.json`
  `caption_replace.ta`. No "..." (each one makes the voice stop).

## 5. Voice and the listening check

```bash
python3 -I videos/kural/eleven.py $WORK/script_ta.txt $WORK/voice_ta --sections 1,2,... --stability 0.5 --similarity 0.9
```

Check with faster-whisper ("small", CPU, int8): every section must be heard as Tamil (probability 0.8 or more), with
its first and last words there; otherwise reword or `--seed 8` and voice that section again. The video should come out
30 to 60 seconds.

## 6. Pictures

`$WORK/pics/images.json` for `videos/doodle/imagegen.py --engine auto` (9:16), one picture per 3-4 seconds
(about 9-12), style string exactly as in `$WORK`'s Doctor Doom example: "3D anime style, like a high-end 3D anime
series or anime game cinematic: cel-shaded 3D render, ... No text, no letters, no logos, no symbols, no recognisable
people, no superhero costumes, no armour." Use the topic's `look` ideas. Manoj's anime self opens and closes every
video: `k_intro` and `k_outro` made with `"edit": "videos/movies-explained/narrator/kavi_1.jpg"` and
`"also": ["videos/movies-explained/narrator/kavi_face.png"]` (outfit 1 for questions, 2 for theories, 3 for news and
timelines, 4 for cosmic lore; see `narrator/README.md`).

`--engine auto` makes the pictures on Manoj's own private Hugging Face Space `Rggroups/pictures` (FLUX.2 [klein]
4B, the same model as Cloudflare, on his PRO account's ZeroGPU time: about 7 seconds a picture, 40 GPU minutes a
day, so a topic's 25 pictures use about 3) and switches to Cloudflare by itself only if that Space is down or its
GPU time is used up. The first picture may wait a few minutes while the Space wakes up. HF_TOKEN goes only to
Manoj's own Spaces and private datasets, never to anyone else's Space.

Look at every picture (contact sheets with ffmpeg, open with Read). Redo (delete, new seed, sharper prompt) any with
text, a copied Marvel design, extra limbs, wrong counts (the model cannot count objects: never let the script depend
on a number of things in a picture), or anything that contradicts the script.

## 7. The videos

Write `$WORK/shots.json` like the example (one section per script line: mood, items, cards ONE/TWO/THREE, name
cards with Tamil names, caption replacements), copy the scripts into `$WORK`, then:

```bash
python3 videos/movies-explained/lore_video.py $WORK ta
```

Check: frames at every card and name card (Tamil letters must be joined correctly), loudness about -14 LUFS, length,
and the voice: `python3 videos/doodle/clarity.py $WORK/out/ta/video.mp4` must say CLEAR (the owner's rule, 22 Nov 2026: "my video have good voice and crystal clear"); UNCLEAR stops the run before upload.
The sound is set by `lore_video.py` and `config.json` (the owner's pick, 21 Nov 2026): the voice made clear for phone
speakers (`doodle/voicefx.py`: less boom, more speech range, pauses over 0.32 s cut to 0.22 s) and, with
`"music_style": "beat"`, our own steady beat with no tune under the whole Short, from the first second to the last.

## 8. Keep the work files

Upload `$WORK` (pictures, voices, shots.json, scripts, out/*/video.mp4) to the PRIVATE Hugging Face dataset
`Rggroups/manoj-explains-work` under `SLUG/` with HF_TOKEN (create it private if missing; refuse if not private).

## 9. Upload, private and scheduled

`$WORK/upload.json` for `videos/doodle/upload.py`:

```json
{"defaults": {"refresh_token_env": "YT_REFRESH_TOKEN_MOVIES", "client_id_env": "YT_CLIENT_ID_MOVIES",
              "client_secret_env": "YT_CLIENT_SECRET_MOVIES", "made_for_kids": false, "ai_content": true,
              "category_id": 24, "privacy": "private"},
 "videos": [{"file": "...out/ta/video.mp4", "title": "...", "description": "...", "tags": [...], "language": "ta",
             "publish_at": "<ta_at>", "playlists": [...],
             "localizations": {"en": {"title": "...", "description": "..."}, "es": {...}, "...": {...}}}]}
```

- Titles: the question, under 60 characters, checked with `.claude/skills/yt-package/title.py`; must contain the
  topic's `match` words (that is how the next run knows it is done); end with `#shorts`. Tamil title: Tamil question
  plus the English `match` words.
- Description: two lines on what the video answers; "Sources:" and the sources; "Pictures, music and voice made with
  AI tools. Fan channel: not made by, linked to or endorsed by Marvel, Disney or any studio."; 3 hashtags.
- Tags: config.json `tags_always` (`tags_always_ta` for Tamil) plus the topic's names.
- Playlists: find their ids with playlists.list (part=snippet, mine=true) by title: "Marvel Lore Explained" for
  English, "Marvel Lore in Tamil | மார்வெல் கதைகள் தமிழில்" for Tamil, and "Before Avengers: Doomsday" when the
  topic's `playlists` has "doomsday" (both languages).

- `"localizations"` on the Tamil video: `"en"` (the English title, under 100 characters with `#shorts`, and the
  English description with global hashtags #Marvel #MCU and the topic's), and a translated title and description for
  every language in config.json `localize_to` (Spanish, Portuguese, Hindi, Indonesian, Arabic, French, German), so
  viewers abroad see it in their own language and hear YouTube's automatic English dub.
- Time: `ta_at` from next_topic.py (8 pm India time). `en_at` is no longer used.
- Playlists: the Tamil one (and "Before Avengers: Doomsday" when the topic has it); no English video goes in "Marvel
  Lore Explained" any more.

`python3 videos/doodle/upload.py $WORK/upload.json`

## 10. Report

One message with send_message to session_01CysHuPAVRvMwaMX52ZGwXv: the questions made, the Tamil video's link and when
it goes public, the hook scores, anything redone and why, anything that failed. Then stop.
