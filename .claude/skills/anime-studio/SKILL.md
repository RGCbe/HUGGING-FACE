---
name: anime-studio
description: Run the anime studio, the 34 job cards in .claude/agents/01..34, for an anime episode or an anime music video. It covers the script, storyboard, character and scene locks, start pictures, AI motion clips, effects, edit, sound and checks, then a private upload. Use for "make the anime", "the next F-Rank episode", "animate the song video", or when the owner asks the studio to work.
---

# The anime studio

- Each card in `.claude/agents/` is one job of a real anime studio (`videos/music/ANIME_CRAFT.md`, section 1),
  written for our tools: what goes in, what comes out and where, the commands, and when the job is done.
- First read `.claude/skills/anime-studio/RULES.md`: keys, files, people, the owner's approvals, GPU time.
  Every card follows it.

## How to run it without wasting time and money

- Do the jobs in this session, in the order below, using each job's card as its checklist.
  - Do not start 34 agents: each one starts from zero and reads everything again.
- Start a card as a separate agent only for the three checks. Fresh eyes matter there, because a checker that did
  not make the work judges only what is on screen:
  - `08-animation-director`: the start pictures;
  - `24-in-between-checker`: the clips;
  - `34-production-assistant-qa`: the finished cut.
  Give them the paths. They write a review file and never fix anything themselves.
- A card may also run as its own agent when its job is big and separate (a whole season arc or a whole script), or
  when the owner asks.
- Some jobs are one step for us:
  - 10 and 22 are one imagegen run and its fixes;
  - 13, 28 and 29 are one `anime_fx.py` pass.

## Projects

**F-Rank Tea Seller, Episode 1 movie** (a story episode)
- **Folders:**
  - `<SERIES>`: `videos/manga/f-rank`;
  - `<EP>`: `videos/manga/f-rank/ep01/anime`.
- **Guide and plans:**
  - `ANIME_PIPELINE_GUIDE.md` (V2, 25 Nov: 2D anime);
  - `PLAN.md`, `SCRIPT.md`, `ANIME_SCRIPT_V2.md`;
  - the shot list `shots.json` and the clip list `all_shots.json`.
- **Cast:**
  - `<SERIES>/cast/*.jpg` and `<SERIES>/characters.json`;
  - the voices in `<SERIES>/cast/voices.json`.
- **Media:** `<EP>/out/` and `<EP>/voice/` (git-ignored), backed up to the private dataset `Rggroups/frank-ep01-work`.
- **Look:** the 19 Nov clips have a live-action look, and V2 is 2D anime. Confirm with the owner which look the next
  cut uses.

**The Vaibhav fan-song video** (a music video)
- **Folder (`<EP>`):** `videos/music/vaibhav/video`.
- **Guide and plans:**
  - `ANIME_CRAFT.md`, section 10 (the rules for its 28 shots);
  - `plan.json`, `motion_shots.json`, `images_anime.json`.
- **The song is fixed:** `~/.cache/music/eleven-song/eleven.mp3`.
- **Media:** `~/.cache/music/vaibhav-video/`, with the pictures in `animeA/`, the clips in `clips/` and the builds in
  `build/`. The face reference `ref/char_A2.png` stays there and never goes in git.

**A new project**
- 16 makes `<EP>/STUDIO.md` (its kind, folders, guide, cast, the owner's wishes, the private backup) and adds the
  project here.

## Order for a story episode

1. **Set up (16 producer):** `STUDIO.md`, the GPU-time plan, the schedule.
2. **Story:**
   1. 01 writes the vision;
   2. 03 plans the season arc;
   3. 17 writes the script;
   4. 19 checks continuity.
3. **Storyboard:** 18 makes `shots.json` and `all_shots.json`, then 02 checks and approves it.
4. **Design:**
   - 04 characters and 20 props and creatures;
   - 05 one lighting lock per scene;
   - 06 colour words, and 21 each shot's scene and grade.
5. **Voices (32):** before the pictures. The AI lip-sync needs the audio, and each shot lasts as long as its line.
   Real studios record after the animation; we cannot.
6. **Start pictures:**
   1. 10 makes them and 22 cleans them up;
   2. 08 checks them, as an agent;
   3. fixes;
   4. the owner sees a few.
7. **Motion:**
   1. 09 plans the action;
   2. 23 makes three test clips, and the owner says yes before the batch;
   3. 24 checks the clips, as an agent;
   4. remakes.
   - 11, 25 and 26 handle camera moves and empty shots.
8. **Finishing:**
   1. 13 writes the compositing spec;
   2. 28 makes the effects and 29 composites;
   3. 12 checks colour, and 27 fixes it at the source.
9. **Edit and sound:**
   1. 14 makes a rough cut;
   2. 15 writes the sound sheet;
   3. 33 makes the effects and 31 the score;
   4. 14 makes the final cut and the Short;
   5. 30 makes the cards and captions.
10. **Checks and upload:**
    1. 34 does the final check, as an agent;
    2. 07 checks the series for drift;
    3. the owner watches the cut;
    4. upload private, then back up `<WORK>` and update `STATUS.md`.

## Order for a music video

The song is finished first and does not change. Every shot follows it.

1. **Set up:** 16 makes the project card. 15 marks the song's sections and the time of each sung line.
2. **Plan:** 01 writes down the owner's look. 18 cuts the storyboard on the lines and beats (`plan.json`,
   `motion_shots.json`), then 02 approves it.
3. **Pictures:** 04, 20 and 05 design; 10 and 22 make and clean up the start pictures; 08 checks them.
4. **Motion:** 09 marks the hits; 23 makes the three-shot test first, then the batch after the owner's yes; 24 checks.
5. **Finishing:** 13 writes a spec per shot (`ANIME_CRAFT.md`, section 10), and 28 and 29 run `anime_fx.py`.
6. **Edit:** 14 cuts with `videos/music/lyric_video.py`, plus `--short`. The captions are part of it (30).
7. **Checks and upload:** 34 checks, the owner watches, then upload private.

## Cards with no tool behind them yet

- 11 and 26: no 3D models or rigs. They use depth moves and camera moves instead.
- 27: a finished AI clip cannot be repainted. It fixes colour in the start picture or with a grade.
- 25: characters cannot be kept separate from backgrounds until compositing (no frame-by-frame cut-out yet).

Each of these cards says what to do instead.

## What the runs taught (keep adding)

**26 Nov 2026, the first run (the Vaibhav video, 21 start pictures):**
- **Checker 08 failed 19 of 21 pictures,** including the ones in the video already sent to the owner. Earlier checks by eye had missed:
  - a bat in two pieces;
  - four balls in one shot;
  - a swoosh-style logo;
  - twin drummers;
  - baseball-like clubs.
  I spot-checked 3 of its findings, and all 3 were right. It took about 15 minutes. The run showed that a separate checker that looks at every picture at full size is worth what it costs.
- **Remakes fix one thing and can break another.** Check every remake, and fix the new problem with a short edit.
- **The clip tool's default negative said "cartoon, anime".** For anime that pushes the model towards a photo-real face. Each shot now carries its own negative (card 23).
- **Every motion prompt asked for "one cricket bat, one red ball",** even the drummers. Props now go only in the shots that have them.
- **The maker's own quick look is not a check.** I passed the two fixed test pictures by eye. The checker then
  found a bat bent into a "V" at its joint and a drummer with three hands, and I confirmed both close up.
  Only a checker's pass counts.
- **Edits on top of edits add new faults.** When a picture fails twice, make 3 fresh takes (new seeds, better
  prompt) and let the checker pick the best, as with song takes.

## A run is done when

- The owner has seen the cut.
- It is uploaded private, or he said to wait.
- `<WORK>` is backed up.
- The repo diff has no media and no keys.
- `STATUS.md` says where things stand, including what was checked and what was not.
