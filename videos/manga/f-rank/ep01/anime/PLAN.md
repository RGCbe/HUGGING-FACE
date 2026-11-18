# The F-Rank Tea Seller, Episode 1 "Hunter's Chai": the movie version (director's plan)

Status: PLAN ONLY, nothing made yet (18 Nov 2026). The shot list is `shots.json` next to this file.
Changed on 18 Nov: Manoj wants **real humans, like Marvel movies** (live-action look), not anime.

## The idea
We turn Episode 1 of our webtoon into a short **live-action-looking movie episode**. It is made of many short AI
shots, 2 to 6 seconds each, joined into one long video, with voices, sound effects, music and English subtitles.
It should feel like a big superhero film: real people, real streets of Mumbai, cinematic light, VFX for the
golden aura, the portal and the monsters, and the same comedy timing as the webtoon.
Everything is OUR OWN: our characters, our story, our music. We do not copy any film's characters, costumes,
logos or shots, and **no face is a real actor or a real person**.

- Length: about **3 to 3.5 minutes**, 44 shots (36 made by AI, 8 cards and freeze frames made in the edit).
- Format: 16:9, 1920x1080, 24 fps, for YouTube. Later: 3 Shorts cut from it, and a Tamil version.

## The look (decided after a style test, see step 1)
- Photorealistic, cinematic: real skin, hair, cloth and metal; widescreen movie framing; shallow depth of field.
- Light from real sources: tea-stall lanterns, street lights, the blue portal, the golden aura, fire in the dungeon.
- Colour grade like a blockbuster: warm skin, teal shadows; night scenes rich, not muddy.
- VFX only where the story needs it: the Gates, the aura, the slash, the monsters, the status window.
- No comic text on screen (no "KRASH" letters); those become sound effects. Name cards and the status window
  stay as clean movie-style graphics.
- Two looks for the style test: **A. bright superhero blockbuster** and **B. darker, grittier action film**.

## The cast (one locked face per character; every face is invented)
| Who | Look | Voice |
|---|---|---|
| Arjun, 18 | young Indian man, dark brown skin, messy black hair, white kurta, red sash, red string bracelet | calm, warm, young (ElevenLabs library voice) |
| Viktor Hale, B-Rank | tall foreign hunter, short slicked-back blonde hair, modern silver plate armor, black cape | loud, arrogant (library voice) |
| Meera, healer | young Indian woman, long black braid, white robe with gold trim, wooden staff | kind, bright (library voice) |
| Raghu (name to confirm), tank | huge, bald, black beard, heavy armor, tower shield | one grunt only in this episode |
| Narrator | | Manoj's own voice clone |

Viktor's design must not look like any film hero (no long hair, no red cape, no hammer).

## The story in 7 parts
| Part | Time | Shots | What happens |
|---|---|---|---|
| A. Cold open | 0:00-0:15 | S01-S04 | Viktor glowing in a dark cave: "This power... where is it coming from?!" Title. "One hour earlier..." |
| B. The world | 0:15-0:35 | S05-S07 | Mumbai 2031, Gates in the sky, hunters get rich, a tiny tea stall next to the biggest Gate |
| C. Arjun | 0:35-0:50 | S08-S11 | The tea pour (our signature shot), slow business, "Rank F" card |
| D. Viktor's party | 0:50-1:35 | S12-S20 | The insult, the tea, "Nothing special", Arjun's close-up: "One hour. That's all you get." |
| E. The dungeon | 1:35-2:15 | S21-S31 | Ambush, the tank is smashed, Viktor's power-up, one slash, "I just awakened", 58-minute montage |
| F. Minute sixty | 2:15-2:35 | S32-S36 | The boss, the jump, the aura fizzles out: "...Oh no." RUN! |
| G. The truth | 2:35-3:10 | S37-S44 | "What did you put in that tea?!" "...Cardamom." The hidden skill window. A red eye in the Gate. To be continued. |

## How each shot is made
1. **Face references**: one photoreal face and costume sheet per character, invented by AI, checked so they do not
   look like a real famous person.
2. **Keyframe**: one 16:9 photoreal picture of the shot (1280x720) with a photoreal image model and the face lock
   (the character's face reference), so the same person appears in every shot.
3. **Motion**: the keyframe becomes a 5-second 720p clip with **Wan 2.2 image-to-video** from the motion line in
   `shots.json`. Two takes per shot; I keep the better one.
4. **Clean-up**: upscale to 1920x1080, 24 fps, trim to the shot length, one colour grade over all shots.
5. **Edit**: cut to the voice; add sound effects, original music, impact flashes, the name cards and status window
   (our own overlay code), English subtitles; loudness to YouTube's -14 LUFS.
6. **Check**: I watch every shot for broken hands or faces and changed faces, and re-make those.

## Where it runs and what it costs
- Pictures and clips: **GridShare**, a rented RTX 4090 (24 GB, ₹48 an hour), about 5 to 7 hours in total.
  Photoreal 720p needs more GPU time than anime: about **₹250-350** for the whole episode with retakes.
  The balance is ₹494.93 (18 Nov), so this is one episode's budget.
- Voices: ElevenLabs, about 1,400 characters (~650 credits). **ElevenLabs ends on 2 Dec, so all voices are made
  before then.**
- Music and sound effects: our own tools (no outside music). Edit: here, with our ffmpeg pipeline.
- YouTube upload is marked as AI-made realistic content ("altered or synthetic content"), as YouTube requires for
  realistic AI people.

## Schedule (about 5 to 6 working days)
| Day | Work | You check |
|---|---|---|
| 1 | Style test: 3 keyframes in looks A and B + 1 moving test clip | pick the look |
| 2 | Face and costume sheets for the 4 characters | approve the faces |
| 3 | All 36 keyframes | one contact sheet of all keyframes |
| 4 | Animation on GridShare (both takes), upscale, colour grade | - |
| 5 | Voices (before 2 Dec), sound, music, edit, subtitles, overlays | the first full cut |
| 6 | Fixes, final render, upload private and scheduled; 3 Shorts cut from it | the final video |

## What I need from Manoj
1. **The relay form** for `relay.gridshare.in` (the same GridShare key again). It lets me send pictures to the
   rented machine and bring the clips back. The cloud machine I work on cannot use SSH.
2. **Pick the look** (A bright or B darker) after the style test on day 1.
3. **Approve the 4 faces** on day 2.
4. **The tank's name** (Raghu is a suggestion).
5. OK for the budget (about ₹250-350 of the GridShare balance).

## Honest limits
- AI movie shots look great for 2 to 5 seconds; they are not Marvel-level VFX in every frame. Some shots will need
  2 or 3 tries, and a few may look slightly "AI". Fast cutting, like a trailer, hides most of it.
- Faces can drift between shots: the face lock, two takes per shot and re-makes keep them steady.
- Fights are cut into many quick shots, like real action editing; long single-take fights are not possible.
- Long dialogue lip-sync is weak: talking shots stay short; long lines go over reaction shots or the narrator.
- GridShare machines are home PCs and can go offline: work is saved in /workspace and moves to another machine.

## After Episode 1
- 3 Shorts from the long video: (1) "F-Rank tea boy" to "One hour. That's all you get." (S14-S20), (2) the power-up
  and one slash (S26-S29), (3) "...Cardamom." (S38-S40). Shown as the 16:9 picture centred on a blurred
  background with big subtitles.
- Tamil version: the same pictures and clips, Tamil voices and subtitles.
- If the episode does well: Episodes 2 and 3 the same way, re-using the face sheets.
