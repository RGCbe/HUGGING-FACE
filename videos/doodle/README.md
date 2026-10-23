# Doodle video engine

Whiteboard-style videos: hand-drawn sketches that draw themselves with a marker pen, in time with
a voiceover. Each idea gets its own board, and the camera pans along one long whiteboard. All
artwork is drawn in code with [rough.js](https://roughjs.com) (MIT, `vendor/`), and the text uses
Patrick Hand and, for Tamil, Kavivanar (both SIL Open Font License, `fonts/`).

| File | What it does |
| --- | --- |
| `engine.js` | Scenes, timed items (`draw`, `write`, `pop`, `stamp`, and `image`: a picture painted in row by row behind the pen, then slowly zoomed), the camera, the pen, `renderAt(t)` |
| `doodles.js` | Reusable drawings: emu, person (hats: slouch, straw, top, helmet), gun, map of Australia, calendar, newspaper, trophy and more |
| `doodles_story.js` | People and things for children's stories: kids, grandparents, parents, a teacher, a poet; trees, animals, houses, a temple, books, lamps and more |
| `render.mjs` | Renders frames in headless Chromium (Playwright) and pipes them into ffmpeg; `--stills auto` saves one finished frame per scene for review; `--layout portrait` draws a 1080x1250 board at full size for Shorts; `--data` passes a JSON spec to the scenes |
| `imagegen.py` | Illustrations for a video's scenes from Qwen-Image (Apache-2.0) on a Hugging Face Space, one shared style per video (`images.json`); uses `HF_TOKEN` and the account's daily ZeroGPU quota, so it skips pictures that already exist and a rerun makes only the missing ones |
| `timing.py` | Word timings for a sectioned voiceover, aligned to the script (faster-whisper); also keeps what Whisper heard |
| `captions.py` | Burned-in ASS captions from the timings, with spoken numbers shown as digits; `--margin` moves them up or down |
| `short.py` | Builds a vertical Short: a new hook line plus stretches of the long video |
| `music.py` | Original background music (plucked bass, marimba, a whistled tune), synthesised so there is nothing to claim |
| `mix.py` | Mixes music under the voice, ducking it while the voice speaks, at -14 LUFS |
| `upload.py` | Uploads a video and its Shorts to YouTube (Data API, resumable) with title, description, tags, audience, AI-content label and thumbnail; private by default, dry run without credentials |

## Making a video

A video folder (for example `../01-emu-war/`) holds the script, `voiceover_en.txt` (one section
per line, as the voice reads it), `scenes.js`, and the generated `timing.json`.

```bash
# from videos/; $WHISPER_PY is a Python that has faster-whisper installed
$WHISPER_PY doodle/timing.py 01-emu-war/voiceover_en.txt "tts/full_en_{n:02d}.wav" 0.6 01-emu-war/timing.json
node doodle/render.mjs --scenes 01-emu-war/scenes.js --timing 01-emu-war/timing.json --out stills/x.mp4 --stills auto
node doodle/render.mjs --scenes 01-emu-war/scenes.js --timing 01-emu-war/timing.json --out silent.mp4
python3 doodle/captions.py 01-emu-war/timing.json captions.ass --replace 01-emu-war/caption_replace.json
ffmpeg -i silent.mp4 -i voiceover.m4a -vf "ass=captions.ass:fontsdir=doodle/fonts" -af apad -shortest out.mp4
OUT_DIR=. WORK_DIR=work TTS_DIR=tts python3 doodle/short.py 01-emu-war/short1.json
```

When Playwright is installed globally, set `PLAYWRIGHT_MODULE` to its folder.

In `scenes.js`, `cue(section, "words")` gives the time those words are spoken. `scene(t, build)`
starts a new board, and the engine pans to it just before `t`. Anything still drawing when the camera
leaves is sped up to finish in time, and items that start too late are reported as warnings.

## Uploading

`upload.py` reads a per-video `upload.json` and needs three environment variables, which are
never committed: `YT_CLIENT_ID`, `YT_CLIENT_SECRET` (an OAuth client in your own Google Cloud
project with the YouTube Data API v3 enabled) and `YT_REFRESH_TOKEN` (scope `youtube.upload`).
Without them it does a dry run. Videos are uploaded **private**. Google also keeps uploads from
unaudited API projects private, so you publish them from YouTube Studio.

This repository is public: don't commit voice samples, credentials or unreleased videos to it.
