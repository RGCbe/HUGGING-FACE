# Vaibhav video: handover (28 Nov 2026)

The owner is taking this video over in another tool. This page says where it stands and how to finish it.

**Read first, and follow them:**
- `CLAUDE.md` at the repo root: the security rules, keys and the public repo;
- `.claude/skills/anime-studio/RULES.md`: files, people and GPU time;
- `videos/music/ANIME_CRAFT.md`, section 10: the rules for this video's 28 shots.

## The rules that matter most here

- **The repo is public.** Never commit video, audio, the start pictures or `ref/`. Media lives in
  `~/.cache/music/vaibhav-video/` and the private dataset `Rggroups/music-work`.
- **Before every push,** run a key-pattern search over the diff.
- **`HF_TOKEN`** goes only to the owner's own Spaces and datasets (`Rggroups/...`).
- **Vaibhav is a real 15-year-old.**
  - Stylised anime only, never a photo-realistic face.
  - No team kits, IPL or BCCI logos, and no readable brand text.
  - The real photo at the end is credited "Photo: Prime Minister's Office / PIB, Government of India (GODL-India)".
- **The owner watches the finished cut** before anything is uploaded, and uploads go up private.

## Get the files onto a new machine

```bash
python3 -c "import os; from huggingface_hub import snapshot_download; snapshot_download('Rggroups/music-work', repo_type='dataset', allow_patterns=['vaibhav-video/*', 'eleven-song/*'], local_dir=os.path.expanduser('~/.cache/music'), token=os.environ['HF_TOKEN'])"
```

This restores the following (backed up 28 Nov):

| Folder | What it holds |
|---|---|
| `~/.cache/music/vaibhav-video/animeA/` | the 21 approved start pictures |
| `skyreels/` | the 31 takes and `skyreels_log.jsonl` |
| `clips/` and `clips_raw/` | the older Wan clips |
| `ref/` | the face references |
| `build/video.mp4` | the last full cut, 26 Nov |
| `review_notes.txt` | the checker's notes |
| `~/.cache/music/eleven-song/eleven.mp3` | the finished song (it does not change) |

You also need ffmpeg and Python with `huggingface_hub` and `gradio_client`.

## Where it stands

- **Song:** finished.
- **Start pictures:** all 21 made and approved (`pictures_chosen.json`).
- **Clip model:** SkyReels-V2 image-to-video on the owner's private ZeroGPU Space `Rggroups/skyreels`.
  - Fast mode: 4 steps, 960x544, seeds 7 and 21.
  - Prompts are in `skyreels_prompts.json`.
- **Clip checks:** batch 1 (`review_skyreels_batch1.json`) and batch 2 (`review_skyreels_batch2.json`) were checked
  frame by frame by the clip checker (card 24).
  - On 28 Nov the owner said the agents choose the takes.
  - He saw the picks video but chose nothing himself.
- **The Space `Rggroups/skyreels` is PAUSED.** It is on free ZeroGPU (`zero-a10g`). Restart it from its Settings page
  before making clips.

### The 28 shots

Times are in seconds of the song (`plan.json`).

| Shot | Time | Picture | Take | State |
|---|---|---|---|---|
| S01 | 0.0-5.5 | t01 | t01_s7 | checked, picked (the older Wan `clips_raw/S01_a.mp4` is the other choice) |
| S02 | 5.5-9.7 | t02 | t02_s21 | checked, picked |
| S03 | 9.7-13.7 | t04 | t04_s7 | checked, picked |
| S04 | 13.7-19.6 | p01 | p01_s21 | checked, picked |
| S05 | 19.6-25.3 | p02 | p02_s21, cut_end 1.31 | **stand-in: remake p02** |
| S06 | 25.3-29.6 | p04 | p04_s21, cut_end 0.5 | checked, picked; bat meets ball on frame 28 (1.167 s); watch at full speed (face smears into the grille at 1.92-2.21 s) |
| S07 | 29.6-32.3 | p03 | p03_s7 | checked, picked |
| S08 | 32.3-35.4 | i03 | i03_s7, cut_end 0.68 | checked, picked |
| S09 | 35.4-38.7 | p06 | p06_s7 / p06_s21 | made, **not checked** |
| S10 | 38.7-40.8 | p05 | p05_s7 / p05_s21 | made, **not checked** |
| S11 | 40.8-42.9 | c04 | c04_s7 / c04_s21 | made, **not checked** |
| S12 | 42.9-46.6 | i01 | i01_s7 / i01_s21 | made, **not checked** (same files as round 2's S12_i2v; s21 had the best drummers then) |
| S13 | 46.6-50.3 | i02 | i02_s7 / i02_s21 | made, **not checked** |
| S14 | 50.3-53.9 | c07 | c07_s7 / c07_s21 | made, **not checked** |
| S15 | 53.9-60.3 | t03 | t03_s7 / t03_s21 | made, **not checked** |
| S16 | 60.3-64.3 | c01 | c01_s7 | made, **not checked**; c01_s21 not made |
| S17 | 64.3-66.0 | c02 | none | **not made** |
| S18 | 66.0-67.6 | c03 | none | **not made** |
| S19 | 67.6-71.4 | e01 | none | **not made** |
| S20 | 71.4-75.1 | c05 | none | **not made** |
| S21 | 75.1-79.5 | c06 | none | **not made** |
| S22 | 79.5-81.2 | p03 | p03_s21 | checked, picked (first 1.7 s) |
| S23 | 81.2-85.2 | p02 | p02_s7, cut_end 1.65 | **stand-in: remake p02** |
| S24 | 85.2-88.8 | c03 | none | **not made** (the other c03 seed) |
| S25 | 88.8-92.2 | i03 | i03_s21 | checked, picked |
| S26 | 92.2-96.0 | e01 | none | **not made** (the other e01 seed) |
| S27 | 96.0-99.2 | i02 | other i02 seed | made, **not checked** |
| S28 | 99.2-101.5 | c07 | other c07 seed | made, **not checked** |

A picture used by two shots gives each shot a different seed.

## What is left, in order

1. **Restart the Space** `Rggroups/skyreels`.
2. **Make the missing takes:**

   ```bash
   cd videos/music/vaibhav/video
   python3 skyreels_batch.py
   ```

   - It skips takes that exist and stops cleanly when the day's GPU time runs out. Run it again the next day.
   - There are 13 takes to make:
     - c01_s21;
     - c02, c03, e01, c05 and c06, 2 seeds each;
     - p02b, 2 seeds.
   - p02b is the p02 remake, with an untested new prompt in `skyreels_prompts.json`: no "to bat", props held low,
     73 frames.
   - Each take takes about 45-65 s of GPU time. The account has about 40 minutes a day.
3. **Check every take that is not checked yet,** frame by frame, the way card 24 does (`.claude/agents/24-in-between-checker.md`):
   - morphing faces, an older-looking face, extra or doubled bats and balls, logos or brand text, frozen frames;
   - the exact contact frame of any hit.
   - Write `review_skyreels_batch3.json` and onwards in the same shape as batch 2.
   - Pick a take per shot, and a `cut_end` where a take goes bad near its end.
4. **Place the picks** where the build looks for them.
   - `lyric_video.py` reads `~/.cache/music/vaibhav-video/clips_raw/S{NN}_{take}.mp4`, plus `plan.json`'s `"takes"`,
     `"cut_end"` and `"fx"`.
   - Copy each picked take to `clips_raw/S{NN}_sky.mp4` (for example `skyreels/t01_s7.mp4` to `clips_raw/S01_sky.mp4`).
   - Set `"takes": {"S01": "sky", ...}` and copy the `cut_end` values from the reviews into `plan.json`.
5. **Write the compositing spec** (`"fx"` per shot, `ANIME_CRAFT.md` section 10, `videos/music/anime_fx.py`):
   - drawings on twos;
   - the impact frame on S06 at frame 28 of the raw clip;
   - speed lines and shake only where the action earns them.
6. **Build:**

   ```bash
   python3 videos/music/lyric_video.py videos/music/vaibhav/video/plan.json
   python3 videos/music/lyric_video.py videos/music/vaibhav/video/plan.json --short
   ```

   This writes `build/video.mp4` (16:9) and `build/short.mp4` (9:16). Delete the old `build/video_*` shot files first,
   or the build reuses them.
7. **Final check** (card 34):
   - every shot looked at;
   - captions in sync;
   - loudness;
   - no logos, no photo-real face, the photo credit at the end.
8. **The owner watches the cut,** then uploads it private.
9. **Back up the new media** to `Rggroups/music-work` (`vaibhav-video/`).

To make a labelled review video of chosen takes for the owner's phone, use `picks_reel.py` (usage at its top).

## Not checked or still open

- **Untested:** the p02b prompt.
- **Never checked frame by frame:** 16 takes of batches 3 and 4 (S09-S16, S27, S28).
- **Never confirmed by the owner:**
  - the S01 choice between SkyReels t01_s7 and Wan S01_a. The checker leans to t01_s7: longer, no start pop.
- **Known faults in the picks:**
  - S01: the cow never turns its head, and his eyes grow a little late in the clip.
  - S06: a red label shows on the bat, and the ball leaves the frame and comes back in.
