# The F-Rank Tea Seller, Episode 1 "Hunter's Chai": the anime version (director's plan)

Status: PLAN ONLY, nothing made yet (18 Nov 2026). The shot list is `shots.json` next to this file.

## The idea
We turn Episode 1 of our webtoon into a real anime episode. It is made of many short AI shots, 2 to 6 seconds each,
joined into one long video, with voices, sound effects, music and English subtitles. The energy is shonen anime like
One Piece and Dragon Ball: power-ups, aura, impact flashes, big reactions, comedy timing. The people look **more
like real humans**. Everything is OUR OWN: our characters, our story, our music. We do not copy any show's
characters, designs or shots.

- Length: about **3 to 3.5 minutes**, 44 shots (36 made by AI, 8 cards and freeze frames made in the edit).
- Format: 16:9, 1920x1080, 24 fps, for YouTube. Later: 3 Shorts cut from it, and a Tamil version.

## The look (decided after a style test, see step 1)
- Semi-realistic shonen anime: real body proportions (7 to 7.5 heads tall), adult faces, normal-size eyes.
- Clean cel shading, soft rim light, painted backgrounds, strong light and shadow (lanterns, portal glow, aura).
- No chibi. The two chibi comedy panels (6 and 26) become realistic faces with comedy timing instead.

## The cast (same faces in every shot, from one character sheet each)
| Who | Look | Voice |
|---|---|---|
| Arjun, 18 | dark brown skin, messy black hair, white kurta, red sash, red string bracelet | calm, warm, young (ElevenLabs library voice) |
| Viktor Hale, B-Rank | tall, slicked-back blonde hair, silver armor, black cape | loud, arrogant (library voice) |
| Meera, healer | brown skin, long black braid, white robe with gold trim, staff | kind, bright (library voice) |
| Raghu (name to confirm), tank | huge, bald, black beard, heavy armor, tower shield | one grunt only in this episode |
| Narrator | | Manoj's own voice clone |

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
1. **Keyframe**: one 16:9 picture of the shot (1344x768), drawn with our anime picture model and each character's
   reference sheet, so faces stay the same.
2. **Motion**: the keyframe becomes a 5-second clip with **Wan image-to-video** (the same model family as our
   anime-motion Space test) from the motion line in `shots.json`. Two takes per shot; I keep the better one.
3. **Clean-up**: upscale 832x480 to 1920x1080 (anime upscaler), smooth to 24 fps, trim to the shot length.
4. **Edit**: cut to the voice; add sound effects, original music, impact flashes, the name cards and status windows
   (our own overlay code), English subtitles; loudness to YouTube's -14 LUFS.
5. **Check**: I watch every shot for broken hands or faces and wrong characters, and re-make those.

## Where it runs and what it costs
- Pictures and clips: **GridShare** (rented RTX 4090 or 3090, 24 GB), one session of about 3 hours.
  About **₹150-200** for the whole episode with retakes. The balance is ₹494.93 (18 Nov).
- Voices: ElevenLabs, about 1,400 characters (~650 credits). **ElevenLabs ends on 2 Dec, so all voices are made
  before then.**
- Music and sound effects: our own tools (no outside music).
- Edit: here, with our ffmpeg pipeline.

## Schedule (about 5 working days)
| Day | Work | You check |
|---|---|---|
| 1 | Style test: 3 keyframes in 2 looks + 1 animated test clip | pick the look |
| 2 | Character sheets for the 4 characters, then all 36 keyframes | one contact sheet of all keyframes |
| 3 | Animation on GridShare (both takes), upscale | - |
| 4 | Voices (before 2 Dec), sound, music, edit, subtitles, overlays | the first full cut |
| 5 | Fixes, final render, upload private and scheduled; 3 Shorts cut from it | the final video |

## What I need from Manoj
1. **The relay form** for `relay.gridshare.in` (the same GridShare key again). It lets me send pictures to the
   rented machine and bring the clips back. The cloud machine I work on cannot use SSH.
2. **Pick the look** after the style test on day 1.
3. **The tank's name** (Raghu is a suggestion).
4. OK for the budget (about ₹150-200 of the GridShare balance).

## Risks and how we handle them
- Faces change between shots: one reference sheet per character, two takes per shot, re-make the bad ones.
- AI clips are short (about 5 s): fights are cut into many quick shots, like real anime editing.
- Long dialogue lip-sync is weak: talking shots stay short; long lines go over reaction shots or close-up eyes.
- GridShare machines are home PCs and can go offline: work is saved in /workspace and moves to another machine.
- ElevenLabs ends 2 Dec: voices first, before anything else in week 2.

## After Episode 1
- 3 Shorts from the long video: (1) "F-Rank tea boy" to "One hour. That's all you get." (S14-S20), (2) the power-up
  and one slash (S26-S29), (3) "...Cardamom." (S38-S40). Shown as the 16:9 picture centred on a blurred
  background with big subtitles.
- Tamil version: the same pictures and clips, Tamil voices and subtitles.
- If the episode does well: Episodes 2 and 3 the same way, re-using the character sheets.
