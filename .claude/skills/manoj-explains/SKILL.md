---
name: manoj-explains
description: Make and schedule the next Manoj Explains videos - Marvel and movie lore questions as 2-3 minute vertical videos in English and Tamil, narrated by Manoj's 3D anime self, with only our own pictures, music and voice (no film clips, stills, posters, comic panels, logos or AI pictures of Marvel characters), checked, uploaded private and scheduled on the Manoj Explains channel. Use for "make this week's Manoj Explains videos", "run Manoj Explains", or when a scheduled task asks for a Manoj Explains run.
---

# Manoj Explains: one run

Each run makes the next `topics_per_run` questions (`videos/movies-explained/config.json`: 1, one a day, Manoj's choice) from
`videos/movies-explained/topics.json`. Every question becomes TWO videos: English and Tamil, 2-3 minutes, 1080x1920,
uploaded private and scheduled (English 7 pm, Tamil 8 pm India time) on the channel Manoj Explains
(@manoj-d-explains). The finished example is "Who is Doctor Doom?": `videos/movies-explained/videos/01-doctor-doom/`
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
for v in YT_CLIENT_ID_MOVIES YT_CLIENT_SECRET_MOVIES YT_REFRESH_TOKEN_MOVIES ELEVENLABS_API_KEY CF_ACCOUNT_ID CF_API_TOKEN; do
  [ -n "${!v:-}" ] || echo "missing $v"; done
sudo apt-get install -y -q ffmpeg fluidsynth fluid-soundfont-gm >/dev/null 2>&1 || apt-get install -y -q ffmpeg fluidsynth fluid-soundfont-gm
pip install -q numpy soundfile pillow -r videos/kural/requirements-whisper.txt
```

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

- `script_en.txt`: 7 to 9 lines, 300 to 400 words in all, each line starting with an emotion tag (`[curious]`,
  `[mysterious]`, `[excited]`, `[serious]`, `[shocked]`, `[sad]`, `[warm]`). Shape: the question first ("You think
  ...? ... But how?"), "here's the thing", three points (or three theories, the best last), the answer, and a last
  line asking the viewers something for the comments. Write numbers as digits only where a person reads them that way
  (years: 2015). No greeting; Manoj's anime self says it all.
- Score the first line: `python3 .claude/skills/yt-script/hookscore.py hooks.txt` with 3-4 tries; use one scoring
  60 or more. Never start two videos the same way.
- `script_ta.txt`: the same lines in spoken Tamil (like the Doctor Doom example), same tags, numbers written as
  words; their digits go in `shots.json` `caption_replace.ta`.

## 5. Voice and the listening check

```bash
python3 -I videos/kural/eleven.py $WORK/script_en.txt $WORK/voice_en --sections 1,2,...
python3 -I videos/kural/eleven.py $WORK/script_ta.txt $WORK/voice_ta --sections 1,2,...
```

Check with faster-whisper ("small", CPU, int8): every English section's words against the script (only spelling of
numbers and names may differ; anything else: reword or `--seed 8` and voice that section again); every Tamil section
must be heard as Tamil (probability 0.8 or more). The English video should come out 1:45 to 2:45.

## 6. Pictures

`$WORK/pics/images.json` for `videos/doodle/imagegen.py --engine cloudflare` (9:16), one picture per 4-6 seconds
(about 20-24), style string exactly as in `$WORK`'s Doctor Doom example: "3D anime style, like a high-end 3D anime
series or anime game cinematic: cel-shaded 3D render, ... No text, no letters, no logos, no symbols, no recognisable
people, no superhero costumes, no armour." Use the topic's `look` ideas. Manoj's anime self opens and closes every
video: `k_intro` and `k_outro` made with `"edit": "videos/movies-explained/narrator/kavi_1.jpg"` and
`"also": ["videos/movies-explained/narrator/kavi_face.png"]` (outfit 1 for questions, 2 for theories, 3 for news and
timelines, 4 for cosmic lore; see `narrator/README.md`).

Look at every picture (contact sheets with ffmpeg, open with Read). Redo (delete, new seed, sharper prompt) any with
text, a copied Marvel design, extra limbs, wrong counts (the model cannot count objects: never let the script depend
on a number of things in a picture), or anything that contradicts the script.

## 7. The videos

Write `$WORK/shots.json` like the example (one section per script line: mood, items, cards ONE/TWO/THREE, name
cards with Tamil names, caption replacements), copy the scripts into `$WORK`, then:

```bash
python3 videos/movies-explained/lore_video.py $WORK en
python3 videos/movies-explained/lore_video.py $WORK ta
```

Check: frames at every card and name card (Tamil letters must be joined correctly), loudness about -14 LUFS, length.

## 8. Keep the work files

Upload `$WORK` (pictures, voices, shots.json, scripts, out/*/video.mp4) to the PRIVATE Hugging Face dataset
`Rggroups/manoj-explains-work` under `SLUG/` with HF_TOKEN (create it private if missing; refuse if not private).

## 9. Upload, private and scheduled

`$WORK/upload.json` for `videos/doodle/upload.py`:

```json
{"defaults": {"refresh_token_env": "YT_REFRESH_TOKEN_MOVIES", "client_id_env": "YT_CLIENT_ID_MOVIES",
              "client_secret_env": "YT_CLIENT_SECRET_MOVIES", "made_for_kids": false, "ai_content": true,
              "category_id": 24, "privacy": "private"},
 "videos": [{"file": "...out/en/video.mp4", "title": "...", "description": "...", "tags": [...], "language": "en",
             "publish_at": "<en_at>", "playlists": [...]},
            {"file": "...out/ta/video.mp4", "title": "...", "description": "...", "tags": [...], "language": "ta",
             "publish_at": "<ta_at>", "playlists": [...]}]}
```

- Titles: the question, under 60 characters, checked with `.claude/skills/yt-package/title.py`; must contain the
  topic's `match` words (that is how the next run knows it is done); end with `#shorts`. Tamil title: Tamil question
  plus the English `match` words.
- Description: two lines on what the video answers; "Sources:" and the sources; "Pictures, music and voice made with
  AI tools. Fan channel: not made by, linked to or endorsed by Marvel, Disney or any studio."; 3 hashtags.
- Tags: config.json `tags_always` (`tags_always_ta` for Tamil) plus the topic's names.
- Playlists: config.json `playlists` ids for `en`/`ta` and the topic's `playlists` names (skip empty ids).

`python3 videos/doodle/upload.py $WORK/upload.json`

## 10. Report

One message with send_message to session_01CysHuPAVRvMwaMX52ZGwXv: the questions made, the video links and when
each goes public, the hook scores, anything redone and why, anything that failed. Then stop.
