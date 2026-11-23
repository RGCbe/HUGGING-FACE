---
name: office-tea-talks
description: Make and schedule the next Office Tea Talks Short on the Tea Break channel - a 40-60 second, slightly funny office / IT life lesson in Tamil AND in English (the same story, two Shorts the same day), told as our own story with invented characters, in the owner's AI voice, our own doodles, captions and beat, built from what the top Tamil work videos are talking about (their points, never their words), checked for a clear voice, uploaded private and scheduled. Use for "run Office Tea Talks", "make today's office short", or when a scheduled task asks for an Office Tea Talks run.
---

# Office Tea Talks: one run

Tamil office / IT life lessons, posted on the owner's **Tea Break with Manoj** channel in their own playlist (the owner's
choice, 22 Nov 2026: "make it little funny and post in tea break channel"; videos/office/README.md: why, and what is
never done). Each run
makes `config.json` "per_run" Shorts (1): the hottest office theme right now, what the top videos on it are saying,
and a NEW, slightly funny story of ours that carries one of those points as its lesson, **in Tamil and in English**
(the owner, 22 Nov 2026: "We use both English and Tamil also"): two Shorts from one story, one set of pictures, Tamil
at config.json "publish_time" and English at "publish_time_en" the same day. The worked example is
`videos/office/example/`: read its `script_ta.txt`, `script_en.txt`, `shots.json` and `images.json` first. The English
Short made from it: "Fired by Email at 6 AM. Why Wasn't He Scared?", 55 s, https://youtu.be/t1B3j_aoA6s (with the 3D moves and the talking host).

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
pip install -q numpy soundfile pillow -r videos/kural/requirements-whisper.txt -r videos/doodle/requirements-motion.txt
```

The pictures move in 3D, and the host talks: `lore_video.py` does this by default when the motion libraries are
installed (`videos/doodle/requirements-motion.txt`, line above; the owner's "ok", 23 Nov 2026). Copy the host's
`*.open.png` and `*.closed.png` pictures too (`cp videos/office/host/*.png`), so his mouth opens and closes with the
voice on `host_think` and `host_comment`. If the libraries are missing, the video falls back to plain zooms: say so in
the report.

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

1. **The shock and an open question, all in line 1**, because viewers decide to swipe in the first two seconds. Start on
   the shock itself, with a concrete detail and what it costs, then ask the question that the rest of the video answers.
   Example: "காலை ஆறு மணிக்கு ஒரு மெயில்: இன்று முதல் உங்கள் access நிறுத்தப்படுகிறது. ஏழு வருஷ வேலை, ஒரே மெயில்ல
   போச்சு. ஆனா கார்த்திக் பயப்படல. ஏன்?" Don't warm up first ("காலை ஆறு மணி. கார்த்திக் போனைப் பார்க்கிறான்." held the shock
   back to second five, and scored WEAK).
2-4. What happened, in short sentences, built on one running joke (below). The answer to line 1's question comes as
   the turn ("ஏன்னா, …").
5. The lesson as one short line someone could quote, in two halves, not a lecture. The example: "வேலை கம்பெனியோடது.
   ஆனா ஸ்கில்லும், சேமிப்பும், உங்களோடது." Don't open it with "பாடம் இதுதான்".
6. A question about the viewer's own office, with a one-word reply to type. The example: "…சொல்லியிருந்தா, கமெண்ட்ல
   ஃபேமிலின்னு ஒரு வார்த்தை போடுங்க." Or let viewers sort themselves into one of three kinds.

**Check the hook before voicing.** Write line 1 in plain English and score it:
`python3 -I .claude/skills/yt-script/hookscore.py --hook "..."`. It must be 60 or more. The scorer reads English only,
so treat the score as a warning, not proof. Then read the script once for logic: every callback must agree with what was
already said. Example: someone who already had savings can't "open a savings account" as if for the first time.

**Funny the way Tamil office videos are funny (the owner's wish; studied 22 Nov 2026 in videos/SCRIPT_STYLE.md, "Office
humour that lands"):**

- **One running joke, not scattered gags.** Pick one office phrase or word everyone knows and keep coming back to it.
  - The 4.9-million-view sketch did this with "சொம்பு". The example does it with the manager's "நாம ஒரு ஃபேமிலி".
  - Use it at least three times: the setup, a twist, and a callback at the end, where the new manager says it on day one.
- **Use at least two of these:**
  - **A list of three that escalates.** "பர்த்டேக்கு கேக், தீபாவளிக்கு ஸ்வீட் பாக்ஸ், சண்டே கூட மீட்டிங் கால்."
  - **Take the office phrase literally.** "Access stopped" read as "you can't come into the house": "எந்த ஃபேமிலியில…
    இனிமே நீ வீட்டுக்குள்ள வரக்கூடாதுன்னு மெயில் அனுப்புவாங்க?"
  - **The same line in a rhythm three or four times, then a flip.**
  - **A real price or brand.** For example ₹20,000, a food app, or a famous song.
- **Picture jokes.** Each funny line gets a picture that shows the joke. In the example, Karthik swipes his office ID at
  his own front door and it glows red.
- **What not to laugh at.** Laugh at office absurdities. Never laugh at someone's pain, a real person or a real company.
  The lesson line stays sincere.
- **Tags.** Tag the funny lines `[funny]`.

Numbers as Tamil words in the script, their digits in `shots.json` `caption_replace.ta`. No "..." (the voice stops).

**The English script, `$WORK/script_en.txt`:**
- **Shape.** The same story, the same number of lines and the same emotion tags, so each line sits on the same
  pictures. Aim for 110 to 140 words.
- **Language.** Simple Indian office English, the way IT people talk ("revoked, effective today", "auto-debit",
  "work calls on Sunday"). Write it again, not word for word: the running phrase ("We're one big family") and the jokes
  have to work in English.
- **Hook check.** Score line 1 as the captions show it (digits) with hookscore.py. It must be 60 or more.
- **Numbers.** Write them as words, and put their digits in `caption_replace.en`.

## 5. Voice

```bash
python3 -I videos/kural/eleven.py $WORK/script_ta.txt $WORK/voice_ta --sections 1,2,... --stability 0.5 --similarity 0.9
```

Then the same for `script_en.txt` into `$WORK/voice_en`.

Check with faster-whisper ("medium", CPU, int8):
- every Tamil section is heard as Tamil, and every English section as English, with a language probability of 0.8 or
  more;
- each section's first and last words are there (for example, the English example's "His manager…" first came back
  without "His").

If a check fails, reword or use `--seed 8`, and voice that section again.

## 6. Pictures: `$WORK/pics/images.json`

`videos/doodle/imagegen.py $WORK/pics/images.json $WORK/pics --engine auto` (own Space first). 9:16, "style" =
config.json "style", "style_ref": "p01", 8 to 11 pictures (one per 4-5 seconds). The main character is described the
same way in every prompt (the example: "Karthik, a 30-year-old South Indian man with short black hair, a neat
moustache, a light blue formal shirt and a blank ID card on a lanyard"); invent a new one for each story (vary age,
gender, job). Look at every picture (a contact sheet, opened with Read); redo any with text, a logo, extra limbs, a
different-looking main character, or anything that does not match its line.

**The host (the owner's wish, 22 Nov 2026: "use my photo also"):** copy `videos/office/host/*.png` into `$WORK/pics/` and
use them as in the example's `shots.json`:

- **First shot:** always the story's most shocking picture (the example opens on the locked laptop), never the host. A
  hello wave in the first second reads as a greeting, and viewers swipe.
- **`host_think`:** on line 1's question, weight about 0.7.
- **`host_laugh`:** right after the funniest line.
- **`host_comment`:** the last line, the comments question.

Don't use `host_hello` in the opening. He is the host who tells the story, never a character in it
(videos/office/host/README.md).

## 7. The video and the clarity check

`$WORK/shots.json` like the example (one section per script line: mood, pictures, caption_replace), then:

```bash
python3 videos/movies-explained/lore_video.py $WORK ta
python3 videos/movies-explained/lore_video.py $WORK en
python3 videos/doodle/clarity.py $WORK/out/ta/video.mp4 $WORK/out/en/video.mp4   # both CLEAR, or nothing is uploaded
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
              "category_id": 27, "privacy": "private", "meta": "tea-break"},
 "videos": [{"file": "...out/ta/video.mp4", "language": "ta", "title": "...", "description": "...", "tags": [...],
             "publish_at": "<next.py publish_at>", "playlists": ["<config.json playlist_id>"]},
            {"file": "...out/en/video.mp4", "language": "en", "title": "...", "description": "...", "tags": [...],
             "publish_at": "<next.py publish_at_en>", "playlists": ["<config.json playlist_id>"]}]}
```

- Title: under 60 characters, the moment as a hook with English office words and an emoji, ending `#shorts`
  ("6 மணிக்கு Layoff Mail 😅 நாம ஒரு Family-யா? #shorts").
- Only the Office Tea Talks playlist (config.json "playlist_id"): never Tea Break's history playlists, which promise
  every word is true.
- **First, the search check** (the owner approved this pattern on 22 Nov 2026). Write the three searches each Short
  should show up for, such as "layoff tamil", "IT layoff tamil" and "கம்பெனி ஃபேமிலி இல்ல". Their words must appear
  in the title or the description's first two lines, which are the only lines people see.
- **Tamil description:**
  - Line 1: the moment with the theme's search word, ending in the question ("7 வருஷம், 'நாம ஒரு ஃபேமிலி', அப்புறம்
    காலை 6 மணிக்கு ஒரு layoff மெயில். ஆனா கார்த்திக் ஏன் பயப்படல?").
  - Line 2: "பாடம்: …".
  - A blank line, then "Office Tea Talks: ஒவ்வொரு கதையிலும் ஒரு ஆபீஸ் பாடம், தமிழிலும் English-லும்."
  - "இது ஒரு கற்பனைக் கதை. கதாபாத்திரங்கள் கற்பனையானவை."
  - "குரல்: என் சொந்தக் குரலின் AI நகல். படங்கள் AI மூலம் வரையப்பட்டவை, இசை எங்களுடையது."
  - A line `Theme: <the trends.py theme>` and a line `Point: <the point id>`. next.py reads both.
  - Three hashtags: the theme's word, #officelife, #tamil (#layoff #officelife #tamil).
- **Tamil tags:** 10 to 15. Start with the searches ("layoff tamil", "IT layoff tamil", "layoff story tamil"), add
  config.json "tags_always", and stop. Tags only help with spellings and variants.
- **English title:** under 60 characters, the question the story answers, ending `#shorts` ("Fired by Email at 6 AM.
  Why Wasn't He Scared? #shorts"). Run it through `.claude/skills/yt-package/title.py`.
- **English description:**
  - Line 1: the moment with the theme's search word, ending in the question ("Seven years at one company, "we're one
    big family", then a 6 a.m. layoff email. So why wasn't Karthik scared?").
  - Line 2: the lesson, worded the way people search it ("The lesson: your company is not your family. …").
  - A blank line, then "Office Tea Talks: short office stories with one lesson each, in English and Tamil."
  - "This is a fictional story. All characters are invented."
  - "Voice: an AI copy of my own voice. Pictures drawn with AI, music is ours."
  - The same `Theme:` and `Point:` lines as the Tamil Short.
  - Three hashtags: the theme's word, #officelife, #corporatelife.
- **English tags:** 10 to 15. Start with the searches ("fired by email", "laid off", "layoff story", "company is not
  your family"), add config.json "tags_always_en", and stop.

`python3 videos/doodle/upload.py $WORK/upload.json`

`"meta": "tea-break"` queues each uploaded Short for the Tea Break Facebook Page and Instagram
(`videos/meta/README.md`): a scheduled `meta.py run` posts it there at its YouTube time. A queueing warning does
not stop the run; report it, with the `meta.py queue` command it prints.

## 10. Report

A few lines:
- the theme and the point used;
- for each language, the title, the link, and when it goes public (India time);
- the clarity numbers;
- what was redone, and anything that failed.
