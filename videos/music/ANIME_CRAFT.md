# Anime craft: how TV anime is made, and how our videos copy it

The owner (26 Nov 2026): "first fully decode how the real animation made the anime" (Dragon Ball, One Piece: both
Toei Animation). This is the study, written as rules for our automation. Sources at the end. `anime_fx.py` and
`lyric_video.py` apply them; `motion_shots.json` (per video) carries the motion prompts.

## 1. The pipeline and who does what

| Step | Japanese term | What happens | Ours |
|---|---|---|---|
| Script | kyakuhon | The episode's events and dialogue, adapted from the manga chapters | the lyrics and the facts |
| Storyboard | ekonte | Every cut (shot) drawn simply, with camera, action, dialogue and its length in frames; the blueprint | `plan.json`: shots, times, moves |
| Designs | settei | Model sheets: each character from every angle, expressions, colours, props | the character reference drawn from his photo (`ref/char_A2.png`) |
| Layout | reiauto | The exact frame of each cut: where characters stand, the camera, how the background fits | the picture prompt's composition |
| Key animation | genga | The key poses only: start, extreme, contact, follow-through | the picture (the start key pose) |
| Animation direction | sakkan (sakuga kantoku) | Corrects key drawings so every face and body stays on model across many animators | our check of every picture and clip: one face, one bat, one ball |
| In-betweens | douga | The drawings between the key poses | the AI motion model (Wan 2.1 image-to-video) |
| Finishing | shiage | Scan or draw digitally, ink, paint flat colours | (the model paints) |
| Backgrounds | haikei / bijutsu | Painted separately, often bigger than the frame so the camera can pan | painted into the picture |
| Compositing | satsuei ("photography") | Characters over backgrounds, glow, diffusion, lens flares, parallax, camera moves, effects | `lyric_video.py`, `anime_fx.py` |
| Edit, sound | henshū, afureko | Cut to length; voices recorded after the animation; music and effects | cut to the song's lines |

A TV series is "multithreaded": several episodes are in production at once with rotating teams, which is how a
weekly show is possible.

## 2. Timing: the heart of the anime look

- Film runs at 24 frames a second. Anime is drawn "on twos" (12 drawings a second, each held 2 frames) or "on
  threes" (8 a second) most of the time; only fast, important action goes "on ones" (24). Fights mix ones for the
  burst and twos for the heavy exchanges.
- The drawings are on twos or threes, but the CAMERA (pans, zooms, shakes) and composited effects move smoothly at
  the full frame rate. That contrast (steppy characters, smooth camera) is a large part of what reads as anime.
- The timesheet (X-sheet) is the score of a cut: one row per frame, saying which drawing is shown on each frame and
  each layer, plus the camera instructions. The key animator writes it; compositing follows it exactly.
- Rule for us: AI clips come out smooth (every frame different). Put the character motion on twos (`--twos`), keep
  camera moves and effects at 30 fps. Use ones only for the hit itself. `plan.json` (shot times) and the `anime_fx.py`
  options for each shot are our timesheet.

## 3. Movement: how a pose is sold

- Key poses first, in-betweens after. A motion = anticipation (a small move the opposite way), the action, then
  follow-through and settle. Hair, cloth and accessories arrive later than the body.
- Spacing: ease in and ease out (drawings bunch near the key poses, spread in the middle of a fast move).
- Smear frames: on a very fast move, 1-2 in-betweens stretch the body or the bat across its path, or draw it
  several times. They stand in for motion blur.
- Holds: a still pose for drama. A moving hold keeps it alive (hair, cloth, aura, eyes, breathing still move), so it
  never looks frozen.
- Cycles and reuse: walks, runs, crowd cheering, flags, fire are loops. Bank footage (transformations, attacks) is
  reused across episodes on purpose.
- Rule for us: one clear action per clip, starting from its key pose (the picture). The motion prompt names the
  anticipation and the follow-through ("he draws the bat back, swings hard, follows through high").

## 4. Action and impact: the Dragon Ball / One Piece language

- Impact frames: 1-3 frames at the moment of contact, usually monochrome, inverted or one solid colour, often a
  graphic silhouette. Short enough not to break the flow, strong enough to feel the hit.
- Speed lines (radial or parallel) behind or around the action, and a camera shake on the hit, then settling.
- Effects as design: Yoshinori Kanada (1970s-80s) drew light, fire, smoke and explosions as bold, angular graphic
  shapes in hard light and dark, with snappy, uneven timing (long holds, then a burst) and dramatic poses. Much of
  TV action animation since (Gainax, Imaishi's Trigger, the "Neo-Kanada" animators) keeps that language.
- Stills that hit hard: a still frame (tome-e) for the biggest moment, with only the camera or effects moving.
  Osamu Dezaki's "harmony" cels go further: the drawing is repainted like a detailed illustration for that one beat.
- Rule for us (`anime_fx.py`): on the contact frame, `--impact T` (inverted, then hard black-and-white, then a white
  flash), `--lines` from T for about 0.9 s, `--shake` from T for about 0.5 s. Only on real hits: the six, the bat on
  the ball. One or two per song section, or they stop meaning anything.

## 5. Faces and singing

- Dialogue is cheap on purpose (kuchipaku, "mouth flaps"): 2-3 mouth shapes (closed, half, open) swapped in time with
  the voice, blinks every
  few seconds, the head mostly held. Big emotion gets a close-up with a moving hold, not lots of drawings.
- Rule for us: a talking or singing face uses mouth flags from the voice (`depthmove.mouth_flags`) or the lip-sync
  model; never let the AI clip invent random mouth movement on a held face.

## 6. Compositing (satsuei)

- Diffusion and bloom: a soft glow on light areas (floodlights, skies, confetti). Lens flares on bright lights
  (Makoto Shinkai's signature). A colour grade per scene (warm dawn, night blue and gold).
- Parallax: background layers move slower than the foreground, giving depth from flat drawings (`depthmove` does
  this from a depth map).
- Camera language: fix (still), PAN (side to side), TU / TB (track up / back: push in, pull out), follow (camera
  keeps up with the runner while the background slides).
- Rule for us: camera moves happen in compositing, smooth, over the AI clip, and so do glow and flares where we can
  add them there (whether asking the motion model for glow smears faces is not tested yet: check those clips).

## 7. Cutting

- A cut is a shot. An episode of about 20 minutes of story is built from many short cuts; a cut lasts as long as its
  action and line need.
- Cut on the action (mid-swing to the ball flying) or on the beat; hold longer on emotion.
- Rule for us: cut on the sung lines and the song's beats; 2-4 s cuts in choruses and the dance break, longer holds
  in the slow opening verse and the bridge.

## 8. Our checks (the sakkan's job)

Every picture and every clip, before the edit: the same face everywhere; one bat, flat-bladed; one red ball; no
extra people that look like him; hands with five fingers; nothing melting or morphing mid-clip (check frames at about
5 a second); no logos or readable text. Remake with another seed or fix in edit mode. The owner watches the cut last.

## 9. Where our tools fall short of a real studio (be honest about these)

| A studio has | We have | What it costs us |
|---|---|---|
| Key poses at the start AND the end of a move, in-betweens drawn to them | Wan 2.1 gets only the first picture; the model guesses the rest | the action can drift, slow down or miss its pose; check every clip |
| One cut as long as the action needs | at most about 3.4 s a clip (832x480, about 60 s of GPU each, 2400 s a day) | a longer shot ends on a held frame; it must be a moving hold (a slow camera push), never a freeze |
| A sakkan correcting every face | the face in the picture; the model may change it as it moves | remake faces that change; keep faces large and steady |
| Effects drawn by hand on the hit frame | `anime_fx.py` overlays (impact, speed lines, shake) | they are the same for every hit; use few |
| Mouth flaps timed to the voice | no lip-sync on the AI clips | no singing faces in AI clips; the lyrics are on screen instead |

## 10. Rules for the 28 shots of the Vaibhav video (`vaibhav/video/motion_shots.json`)

| Kind of shot | Shots | Timing | Effects |
|---|---|---|---|
| His action: walk, swing, raise the bat | S01, S05, S08, S15, S17, S19, S23, S25, S26 | on twos | none, or a shake on a big landing |
| The hit (bat meets ball) | S06, S10, S18, S24 | on twos, the contact frame on ones | `--impact` on the contact frame, `--lines` 0.9 s, `--shake` 0.5 s |
| Emotion close-ups, the father, the bowlers | S02, S16, S20, S21 | on twos, moving hold | none |
| Dream, sleep | S03 | on threes, moving hold | (soft glow at compositing) |
| Crowds, drummers | S09, S11, S12, S14, S28 | on twos (test threes for the far crowd) | none |
| Camera moves and effects: the stadium rise, the ball in the sky, fireworks | S04, S07, S13, S22, S27 | full 30 fps (smooth, the anime camera) | none |

- Find the contact frame in each hit clip by eye (frames at 10 a second), never by guessing from the clip length.
- The 3-clip test (S01, S06, S12) answers three questions before the other 25: does Wan keep his face and one bat, do
  twos read as anime on these clips, and do the hit effects look good or cheap. The owner picks; nothing more is made
  until he says yes.

## Sources

- Toei Animation, how an anime is made: https://corp.toei-anim.co.jp/en/company/animation_production.html
- ABEMA Times, the anime production process: https://times.abema.tv/en/articles/-/10229971
- Anime News Network, a guide to anime ending credits (the roles), part IV:
  https://www.animenewsnetwork.com/feature/2016-08-17/your-ultimate-guide-to-anime-ending-credits-part-iv/.105472
- Kanzenshuu, Dragon Ball production positions and roles: https://kanzenshuu.com/animation-production/positions-and-roles
- Sakuga Blog, anime production schedules: https://blog.sakugabooru.com/2021/11/28/anime-production-schedules/
- Sakuga Blog, the layout crisis:
  https://blog.sakugabooru.com/2022/08/05/the-layout-crisis-the-collapse-of-animes-traditional-immersion-and-the-attemps-to-build-it-anew/
- Sakuga Blog, industry and production Q&A: https://blog.sakugabooru.com/2017/01/11/sakuqa-anime-industry-and-production-questions-1/
- Anime News Network lexicon, "shot on threes": https://www.animenewsnetwork.com/encyclopedia/lexicon.php?id=61
- iD Tech, animating on ones, twos and threes: https://www.idtech.com/blog/what-does-animating-on-ones-twos-and-threes-mean
- Wikipedia, limited animation: https://en.wikipedia.org/wiki/Limited_animation
- Animation Obsessive, "Don't call it limited animation": https://animationobsessive.substack.com/p/dont-call-it-limited-animation
- Animetudes, Yoshinori Kanada and the nature of animation:
  https://animetudes.com/2021/07/21/yoshinori-kanada-and-the-nature-of-animation/
- Animetudes, the Kanada style now: https://animetudes.com/2021/07/09/the-kanada-style-now/
- Wikipedia, smear frame: https://en.wikipedia.org/wiki/Smear_frame
- 80.lv, impact frames: https://80.lv/articles/learn-how-to-add-accents-to-your-animations-with-impact-frames
- Anime News Network, interview with a director of photography (compositing): https://www.animenewsnetwork.com/interview/.140449

Not found in a source and written from general knowledge: the details of the timesheet and of the sakkan's work, the
mouth-flap shapes, and the camera notation (PAN, TU, TB).
