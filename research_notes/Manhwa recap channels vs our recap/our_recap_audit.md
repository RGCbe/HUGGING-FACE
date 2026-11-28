# Our recap measured: "The F-Rank Tea Seller", Episode 1 (Tea Break with Manoj)

All sources below are local project files or measurements on them, taken on 2026-10-29. No web sources were used: the task was to measure our own files. "Measured" means I ran ffprobe/ffmpeg/numpy/librosa on the file named in the link. The measurement scripts and contact sheets are in `/tmp/claude-0/-home-user-HUGGING-FACE/1f6a9d07-9b37-5360-b91a-1c1bc7ba9d52/scratchpad/ourrecap/` (analyze.py, levels.py, voice.py, voice2.py, voice3.py, recap_A-D.jpg, short_A.jpg, tk1-3.jpg). That scratch folder is temporary. No project file was changed, and nothing was uploaded.

Deliverables measured: the 16:9 recap `out/recap.mp4` (189.8 s), the vertical Short `out/short.mp4` (44.4 s), the three TikTok parts (67.9 / 66.7 / 62.9 s) and `out/recap_thumbnail.jpg`. The recap goes public 2026-10-30 12:30 UTC (YouTube id wca8rGT6xlk) and the Short on 2026-11-01 12:30 UTC (id 5lejbz98fCc). Both are private until then — [upload.results.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/upload.results.json)

## Script: words, rate, point of view, first 15 seconds, intro, ending

### Takeaway
The script has 29 lines and 468 words, read at about 150 words per minute. It is told by a third-person narrator in the present tense. A 11-second premise hook comes first, then an 8-second "Hello friends, I'm Manoj" intro, and the story proper starts at 0:20. All character dialogue is reported in the narrator's voice ("Arjun, totally calm, says: cardamom"), not acted. The video ends with a WEBTOON / every-Thursday / "tell me in the comments" call to action. It never asks viewers to subscribe or like.

### Cited Findings
- **Size:** 29 narration lines, 468 spoken words (emotion tags removed), 61 sentences. Sentences run a median of 7 words (mean 7.7, min 2, max 16); 19 of the 61 are 5 words or fewer — [recap.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json), [voiceover_en.txt](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/voiceover_en.txt)
- **Rate:** 150.3 words per minute over the 186.8 s voice track and 147.9 over the full 189.8 s video. Counting only the time inside lines (leaving out the 0.5 s gaps between lines) gives 162.5. Counting only time when the voice is actually sounding gives 194 — [timing.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/timing.json), measured on [tts/line_NN.wav](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/tts/)
- **First 3 s, exact words:** "This boy is the weakest hunter on Earth." — [timing.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/timing.json)
- **First 15 s, exact words** (from the word timings): "This boy is the weakest hunter on Earth. He sells tea for ten rupees a glass. But anyone who drinks his tea becomes unstoppable, for exactly one hour. Hello friends, I'm Manoj. Today is something new: our very…". Line 1 (the hook) runs 0.00–11.12 s and is shown over panel p05 (Arjun pouring tea, with the bubble "Chai! Hot chai! Ten rupees a glass!") — [timing.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/timing.json), frames 0.5/3/9 s in recap_A.jpg
- **Channel intro:** line 2 runs 11.62–19.50 s (7.88 s, 20 words): "Hello friends, I'm Manoj. Today is something new: our very own webtoon, The F-Rank Tea Seller. Here is episode one." It is voice only. The screen shows the comic (panel p03, the city with the Gate) with captions; there is no logo, face or title card — [recap.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json), frames 11.9/12.2/15 s
- **Story start:** the story itself starts at 20.00 s with "It is the year twenty thirty-one…" — [timing.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/timing.json)
- **Point of view and tense:** a third-person narrator in the historical present ("Viktor points at Arjun and laughs", "They run", "a giant red eye opens"). First person appears only for the host, in the intro ("I'm Manoj", "our very own webtoon") and in the CTA ("tell me"). The viewer is addressed directly in "But look at Arjun's face" (line 11) and "You can read episode one…" (line 29) — [recap.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json)
- **How dialogue is handled:**
  - It is reported without quotation marks, introduced by "says:" (2), "asks:" (2), "thinks:" (3) and "laughs." (1).
  - Some dialogue has no speaker attached: "What is this power?" (L15), "Did he just one-shot it?" (L17), "What did you put in that tea?" (L24).
  - The script has 8 question marks, 1 exclamation mark (L07 "…it's the F-Rank tea boy!") and 7 colons.
  - Every voice is the same narrator voice (one cloned voice, one reference recording).
  
  — [recap.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json), [tts/refs.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/tts/refs.json)
- **Emotion tags on lines:** excited 2, warm 3, mysterious 4, funny 6, serious 2, shocked 2, untagged 10 — [recap.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json)
- **Joke lines:**
  - L06 "two million followers and zero manners"
  - L08 "Is it poisoned with weakness?"
  - L22 "So they do the smartest thing a hunter can do. They run."
  - L25 "And Arjun, totally calm, says: cardamom." (marked `punch`, with a rimshot after)
  - L26 "And Meera just asks: can I get one to go?"
  - L27 "…ten rupees for an hour of power? I'm undercharging."
  
  — [recap.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json)
- **Structure by line:**

  | Lines | Part |
  |---|---|
  | L01 | hook |
  | L02 | host intro |
  | L03–L06 | world, stall, Arjun, Viktor |
  | L07–L10 | Viktor mocks and drinks |
  | L11 | Arjun's secret ("one hour") |
  | L12–L18 | dungeon, power-up, rampage |
  | L19–L23 | boss, power runs out, retreat |
  | L24–L26 | confrontation and punchline |
  | L27 | skill reveal |
  | L28 | cliffhanger ("Something has noticed his tea.") |
  | L29 | CTA |

  The video covers the whole of Episode 1 (one episode, not a multi-chapter recap) — [recap.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json)
- **Ending / CTA:** L29 runs 176.48–186.80 s (10.32 s, 34 words, 198 wpm, the second-fastest line): "You can read episode one free on WEBTOON. The link is in the description. A new episode comes every Thursday. So tell me in the comments: what do you think is inside the Gate?" There is no subscribe or like request and no pointer to another YouTube video. After the voice ends, the picture runs 3.0 s longer (TAIL) with a 1.5 s audio fade-out — [recap.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json), [recap.py](file:///home/user/HUGGING-FACE/videos/manga/recap.py)
- **Narration vs lettering wording:** the narration paraphrases the lettered text rather than reading it word for word. Examples: the box says "biggest Gate in the city", the voice says "in Mumbai"; the box says "Monster cores come out. Hunters get rich.", the voice says "they come out rich"; the box says "Viktor Hale", the voice says "Viktor" — [episode.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/episode.json), [recap.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json)

### Inferences
- The hook is a premise statement with no question or open loop in the first 3 s. The channel intro takes about 4% of the runtime (seconds 11.6–19.5) before the story starts.
- Dialogue is reported, not performed, and every character has the same voice. Comedy therefore rests on wording and the music stop, not on acted voices.

### Gaps
- No retention data exists (the video is not public yet), so how the hook or the intro actually performs cannot be measured.

## Pacing: panel time on screen, changes per minute, longest static stretch

### Takeaway
The camera visits 28 panel positions, with 27 panel changes in 189.8 s (8.5 per minute). A panel stays on screen for a median of 6.0 s (min 2.7 s, max 18.4 s). The picture is completely still in about 72% of frames; the longest still stretch is 17.5 s, during the host intro and world setup.

### Cited Findings
- **Panel holds:** each line targets a panel; consecutive lines on the same panel merge into one hold. That gives 28 holds and 27 changes, 8.54 changes per minute. Hold length (including the 0.8 s move in):

  | Statistic | Value |
  |---|---|
  | Min | 2.74 s (p28 "They crawl out of the Gate") |
  | Median | 6.04 s |
  | Mean | 6.78 s |
  | Max | 18.36 s (p03, covering L02 intro + L03 world setup) |

  Holds of 8 s or more: p05 11.62 s, p03 18.36 s, p06 8.34 s, p07 8.58 s, p33 12.82 s, end card 13.32 s — [timing.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/timing.json), [recap.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json), analyze.py
- **Camera motion**, from the camera path re-computed with recap.py's own camera_path logic:
  - It moves in 1,613 of 5,694 frames (28.3%).
  - The longest still stretch is 17.53 s, starting at 12.47 s (p03).
  - Other still stretches of 6 s or more: 12.73 s from 177.07 s (end card), 12.03 s from 157.47 s (p33), 7.77 s at 44.37 s, 7.53 s at 36.03 s, 6.97 s at 111.57 s, 6.47 s at 59.13 s.
  
  — [recap.py](file:///home/user/HUGGING-FACE/videos/manga/recap.py), [panels.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/out/webtoon/panels.json)
- **Moves:** each move between panels is a 0.8 s eased (smoothstep) vertical scroll. Panels taller than the view are scrolled top to bottom while the line is said; that applies to 6 lines (p05, p15, p19, p24, p25, p34). Every other panel is held still — [recap.py](file:///home/user/HUGGING-FACE/videos/manga/recap.py)
- **Panel order:** the camera goes backwards once, from p05 to p03 at 11.62 s, because the hook uses a panel that comes later in the strip. Panels never targeted are p01 (the cold-open: Viktor glowing, "This power… where is it coming from?!", VWOOM), p02 ("One hour earlier…" card), p09, p14 ("Dungeon Gate. Level 9."), p18 ("Viktor! We have to retreat!"), p23 ("For the next fifty-eight minutes, Viktor was unstoppable." + SLASH!) and p32 ("That night." / "Nobody knew the truth about his tea."). Some of these pass by during moves. In total 28 of the 35 strip panels are targeted — [recap.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json), [episode.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/episode.json)
- **Line lengths:** 2.24 s (L23) to 12.32 s (L27), joined by 0.5 s gaps — [timing.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/timing.json), [build.py GAP](file:///home/user/HUGGING-FACE/videos/teabreak/build.py)

### Inferences
- Motion is limited to vertical pans and 0.8 s scrolls. For about 72% of the runtime the image is frozen, and only the captions change.

### Gaps
- I have no comparison numbers for competitor channels here (other researchers cover those).

## Visuals: frame share, bubbles vs narration, captions, motion, transitions

### Takeaway
In the 16:9 recap, the comic is a 1000 px column covering 52% of the frame. The rest is a darkened, blurred copy of the same strip. All lettering (20 bubbles, 12 narration boxes, 8 sound-effect words on targeted panels) stays on screen while the narrator speaks. For 11 of the 20 bubbles the narrator says essentially the same words, and a punchline bubble is usually readable 1–4 s before it is spoken. Captions are a handwriting font in a pale-yellow box at the bottom centre, sometimes covering lettered text. There are no zooms, shakes, cuts or fades. The only motion is the vertical scroll, and the only "transition" is a whoosh sound with each scroll.

### Cited Findings
- **Format:** 1920x1080, 30 fps, H.264 High yuv420p, video about 1.26 Mb/s (CRF 21), AAC 44.1 kHz stereo about 166 kb/s, 34.0 MB — ffprobe on [recap.mp4](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/out/recap.mp4)
- **Frame share:** the 800 px strip is scaled to 1000 px wide (×1.25), giving a 1000x1080 column = 52.1% of the frame's width and area. The two 460 px side bands show the same strip rows from a 480 px copy, blurred (Gaussian radius 6), at 0.45 brightness, stretched. Each frame shows 864 px of strip height, so a square panel (800 px tall in the strip) nearly fills the height and a wide panel (547 px) leaves its neighbours' boxes and bubbles visible — [recap.py](file:///home/user/HUGGING-FACE/videos/manga/recap.py), [panels.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/out/webtoon/panels.json), frames recap_A–D.jpg
- **Lettering in the source:** the lettered strip has 23 speech/thought bubbles, 16 narration boxes, 10 sound-effect words, 2 cards and 1 "[ HIDDEN SKILL ]" status window. All are drawn into the panels. The strip is 800x32,805 px — [episode.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/episode.json), [strip.png](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/out/webtoon/strip.png)
- **Bubbles vs narration** (share of each item's words that the narrator also says in the line spoken over that panel):

  | Lettering on targeted panels | Count | Narrator repeats 80%+ of the words |
  |---|---|---|
  | Bubbles | 20 | 11 (p08, p10, p13 thought, p19, p21, p26, p27, p29, p30, p31, p33) |
  | Narration boxes | 12 | 8 |
  | Sound-effect words | 8 | 1 (GULP) |

  — analyze.py on [episode.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/episode.json) and [recap.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json)
- **Punchlines visible before they are spoken:** the time from a panel settling (line start + 0.8 s) to the narrator saying the bubble's words:

  | Bubble | Readable before spoken |
  |---|---|
  | "Look, everyone" | 2.18 s |
  | "Nothing special" | 1.52 s |
  | "One hour" | 2.18 s |
  | "What is this power" | 3.76 s |
  | "Did he just one-shot it" | 1.30 s |
  | "Oh no" | 3.82 s |
  | "RUN" | 2.22 s |
  | "What did you put in that tea" | 3.36 s |
  | "…Cardamom." | 1.40 s |
  | "Can I get one to go" | 0.98 s |
  | "Ten rupees… I'm undercharging" | 8.38 s |

  — [timing.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/timing.json); seen in frames 150.5 s and 151.6 s (the "…CARDAMOM." bubble is on screen while the caption reads "totally calm,")
- **Caption style:** burned-in ASS subtitles in Patrick Hand at 64 px, dark #111111 text on an opaque pale-yellow (#FFE680) box (BorderStyle 3, outline 10), bottom centre, 42 px bottom margin. A caption holds at most 7 words / 40 characters and breaks at punctuation. The 16:9 video has 111 captions: median 4 words / 23 characters, median 1.56 s on screen (range 0.20–2.94 s). They appear phrase by phrase, with no word-by-word highlight — [captions.py](file:///home/user/HUGGING-FACE/videos/doodle/captions.py), [captions.ass](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/captions.ass)
- **Numbers in captions:** numbers are shown spelled out ("It is the year twenty thirty-one.", "For fifty-eight minutes,", "sixty minutes"), because no `--replace` file is passed — [captions.ass](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/captions.ass), [recap.py](file:///home/user/HUGGING-FACE/videos/manga/recap.py)
- **Captions over lettering:** the caption box sits inside the comic column. In 7 of 36 sampled 16:9 frames it overlaps or touches lettered text: narration boxes at 15, 25, 33, 40 and 47 s, the thought bubble "ONE HOUR. THAT'S ALL YOU GET." at 78 s, and the next panel's "DID HE JUST… ONE-SHOT IT" bubble at 104 s — frames recap_A–C.jpg from [recap.mp4](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/out/recap.mp4)
- **Motion and transitions:** the strip scale is fixed, so there are no zooms, no Ken Burns effect and no shakes. Motion is only vertical: eased 0.8 s scrolls between panels and slow scrolls down tall panels. There are no cuts, flashes, colour effects or video fades, and no rendered motion on the art itself (no parallax, no speed lines) — [recap.py](file:///home/user/HUGGING-FACE/videos/manga/recap.py)
- **No branding:** nowhere in the recap is there an on-screen title card, series logo, channel logo, host face, subscribe animation or progress indicator — frames recap_A–D.jpg
- **Ending frame:** the last 13.3 s (176.5–189.8 s) are one static frame. The black "TO BE CONTINUED" card (Bangers font) sits in the lower part, under the bottom of p34 and the box "…something had noticed." The camera stops at the end of the strip, so the "end" card cannot be centred — frames 180/186/189.6 s in recap_D.jpg, [recap.py](file:///home/user/HUGGING-FACE/videos/manga/recap.py)

### Inferences
- Bubbles and boxes are not hidden or replaced. In about half the dialogue the viewer can read the line on screen before (and while) the narrator says it, which removes the surprise from punchlines such as "…Cardamom." and "I'm undercharging."
- With 48% of the 16:9 frame given to a blurred background, the art is shown at about half the frame's width.

### Gaps
- I did not check every frame for caption/lettering collisions, only 36 samples. A full count would need the bubble geometry mapped to caption times.

## Audio: loudness, voice vs music, effects and stings, moods, silences

### Takeaway
The recap is mastered to -14.3 LUFS integrated (LRA 4.1 LU, true peak -0.9 dBFS). Music is ducked about 17.6 dB under speech and sits about 30 dB below the voice while it speaks; in pauses it comes back to about 14 dB below speech level. Music never stops for longer than a fraction of a second: no stretch of the recap falls below -40 dBFS. Besides music there are 27 whooshes (one per panel change) and 4 stings (2 hits, a wah-wah, a rimshot), plus one music cut-out under the "cardamom" punchline. The music has 17 mood segments, changing 5 times a minute; "playful" fills 38% of the runtime.

### Cited Findings
- **Loudness of each output** (ffmpeg ebur128):

  | File | Integrated | LRA | True peak |
  |---|---|---|---|
  | recap.mp4 | -14.3 LUFS | 4.1 LU | -0.9 dBFS |
  | short.mp4 | -14.6 LUFS | 3.9 LU | -1.3 dBFS |
  | tiktok_part1.mp4 | -14.4 LUFS | 3.6 LU | |
  | tiktok_part2.mp4 | -14.5 LUFS | 4.3 LU | |
  | tiktok_part3.mp4 | -14.3 LUFS | 5.3 LU | |

  — [recap.mp4](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/out/recap.mp4), [short.mp4](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/out/short.mp4), tiktok_part1–3.mp4
- **Mix chain:** the voice is normalised to -16 LUFS. Music is played at ×0.3 gain and side-chain compressed by the voice (threshold 0.02, ratio 6, attack 20 ms, release 450 ms). Whooshes are added at ×0.5 and stings at ×0.35 after ducking. The final mix is normalised to -14 LUFS (true peak -1.5). A punchline cuts the music from 0.9 s before the punch word to 0.5 s after (0.12 s ramps) — [mix.py](file:///home/user/HUGGING-FACE/videos/doodle/mix.py), [config.json music_gain 0.3](file:///home/user/HUGGING-FACE/videos/teabreak/config.json)
- **Stems**, rebuilt with the same filter settings from voice_pad.wav, music.wav, music_stings.wav and events.json:

  | Stem | Integrated loudness |
  |---|---|
  | Voice | -16.0 LUFS |
  | Ducked music | -33.3 LUFS (17.3 LU under the voice) |
  | Music before ducking | -27.8 LUFS |
  | Stings (while sounding) | -25.2 LUFS |
  | Whooshes | -36.3 LUFS |

  — levels/stems in scratch, from [recap folder](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/)
- **Speech vs pauses, in 100 ms windows:**
  - During speech the music's RMS has a median of -47.2 dBFS against -16.8 for the voice: the voice leads by a median of 30.3 dB (10th percentile 2.5 dB, 90th 41.4 dB).
  - Ducking depth during speech: median 17.6 dB.
  - In pauses (129 windows at least 0.25 s from any word) the music returns to -31.0 dBFS.
  - In the final mix, speech windows have a median of -14.7 dBFS and pause windows -28.5 dBFS.
  - Speech covers 79.1% of the timeline.
  
  — levels.py on [recap.mp4](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/out/recap.mp4) and the stems
- **Silences:**
  - No stretch of 0.25 s or longer falls below -40 dBFS (silencedetect at -50 and -40 dB found nothing).
  - At -30 dBFS there are only 14 short dips of 0.26–0.47 s. They include 150.61–150.95 s and 151.77–152.14 s around "cardamom" (the music stop runs 150.38–151.78 s) and the final 0.47 s of fade.
  - The 3.4 s "silence" mood (149.1–152.5 s) has the voice running over it.
  
  — ffmpeg silencedetect on [recap.mp4](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/out/recap.mp4), [events.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/events.json)
- **Sound effects:**
  - 27 whooshes, one 0.15 s before each line that changes panel. Each is 0.45 s of synthetic noise swept up and down in pitch.
  - 4 stings: hit at 102.70 s (the one-swing ogre kill), wahwah at 135.30 s (sword bounces off), rimshot at 152.14 s (after "cardamom"), hit at 169.46 s (the red eye).
  - 1 punch music-stop.
  - No effects for the comic's sound-effect words (GRRAAAH, KRASH, KRAAACK, SLASH, DOOM DOOM, VWOOM), no impacts, no ambience, no crowd or monster sounds.
  
  — [events.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/events.json), [sfx.py](file:///home/user/HUGGING-FACE/videos/doodle/sfx.py), [episode.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/episode.json)
- **Music moods:** 18 mood events became 17 segments (16 changes, 5.06 per minute). Segments last a median of 7.8 s (min 3.4 s, max 40.0 s: playful 35.2–75.2 s). Time per mood:

  | Mood | Seconds | Share of 189.8 s |
  |---|---|---|
  | Playful | 73.0 | 38% |
  | Curious | 36.5 | 19% |
  | Dramatic | 27.1 | 14% |
  | Suspense | 22.7 | 12% |
  | Warm | 14.3 | 8% |
  | Triumphant | 7.8 | 4% |
  | Sneaky | 6.0 | 3% |
  | Silence | 3.4 | 2% |

  The "sad" cue at 139.96 s lasts only 2.74 s and was folded into "playful", because score.py drops moods shorter than 3.0 s. Tempos range from 84 bpm (suspense) to 112 bpm (playful), with a 1.2 s crossfade on each side of a change — [video.log](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/video.log), [score.py](file:///home/user/HUGGING-FACE/videos/doodle/score.py)
- **Music source:** written note by note by score.py and played through the General MIDI FluidR3 sound font with fluidsynth. Example instruments: playful uses pizzicato, bassoon and marimba; suspense uses tremolo strings, contrabass, piano and timpani; dramatic uses strings, horn, timpani and taiko; triumphant uses strings, brass and timpani. The file states it is "Everything is generated, so there is nothing for a copyright claim to match" — [score.py](file:///home/user/HUGGING-FACE/videos/doodle/score.py)

### Inferences
- The music is a continuous bed under 100% of the runtime, broken only by the 1.4 s punchline drop. There is no true silence used for effect.
- Sound design is minimal: whooshes on scrolls and 4 musical stings. None of the drawn sound-effect words is heard.

### Gaps
- I did not listen to the audio (no playback in this environment). Mix judgments rest on level measurements only.

## Voice: the narration in depth (rate, pauses, pitch, loudness, emotion tags, spectrum, script style)

### Takeaway
The narration is a Qwen3-TTS clone of Manoj's voice from one 11.6 s reference recording. Because refs.json is empty, every emotion tag fell back to that one neutral reference, and the tags make no measurable difference. "Excited", "shocked" and "funny" lines have the same pitch, pitch range and loudness as untagged lines.

The delivery is narrow-ranged: median pitch 129 Hz, a typical within-line pitch spread of 4.9 semitones (5th–95th percentile), and per-line median pitch varying only 124–141 Hz across all 29 lines. Questions end with falling or flat pitch.

Speech is fast and continuous: about 194 words per minute while sounding, with only 43 internal pauses of 0.12 s or more across 29 lines (median 0.28 s). There is no vocal pause before any punchline word.

The tone is dark: the 2–5 kHz "presence" band is 29 dB below the low (<200 Hz) band, with nothing above 12 kHz (24 kHz audio). The reference recording has the same balance. Background noise is low (pause floor about -60 dBFS, about 38 dB below speech).

### Cited Findings
- **Engine and emotion setup:**
  - `tts/refs.json` is `{}`, and voice.log says "emotion samples: none yet (every line in the usual voice)".
  - tts.py: "A line without a tag, or with a tag --refs lacks, uses REF_WAV. Tags are never read out.". REF_WAV is the owner's `ref_cut.wav` (11.6 s, 24 kHz).
  
  — [tts/refs.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/tts/refs.json), [voice.log](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/voice.log), [tts.py](file:///home/user/HUGGING-FACE/videos/kural/tts.py), [build.py emotion_refs()](file:///home/user/HUGGING-FACE/videos/teabreak/build.py)
- **How lines are assembled:** each line is cut into pieces of at least 8 words (40 pieces for 29 lines), each piece carrying the line's tag. Pieces are joined with 0.2 s of silence and lines with 0.5 s. Whisper heard 461 of 468 words exactly; 7 sections had one word that did not match exactly (sections 2, 3, 6, 7, 8, 17, 18), and every section passed. In the Short's new CTA line, the first attempt was "NOT CLEAR" ("this story" heard as "f rank t seller", "webtoon" as "viptune"). It was redone with seed 7 and passed — [tts/pieces.txt](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/tts/pieces.txt), [build.py GAP/BREATH](file:///home/user/HUGGING-FACE/videos/teabreak/build.py), [voice.log](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/voice.log)
- **Words per minute:**
  - 150 over the whole voice track and 162.5 inside lines.
  - 194 per minute of sounding speech (144.9 s of sound in 172.8 s of line audio).
  - Per line: min 122 (L25 "cardamom" line), median 160, max 214 (L23 "They crawl out of the Gate, barely alive."), standard deviation 20.5.
  - Fastest lines: L23 214, L29 CTA 198, L09 195, L04 191, L22 191, L13 188, L19 185.
  - Slowest lines: L25 122, L07 137, L28 138, L18 140.
  
  — [timing.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/timing.json), voice.py, voice2.py
- **Pauses, from timing.json word gaps:** inside lines, 87% of word gaps are 0 (median 0.00 s, 90th percentile 0.14 s, max 1.06 s). Whisper word times butt up against each other, so this undercounts pauses. Between lines (last word to next first word) the gap is a median of 0.94 s (90th percentile 1.07 s, max 1.34 s), which includes the inserted 0.5 s — [timing.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/timing.json)
- **Pauses, from the audio energy** (20 ms frames more than 25 dB below the line's speech median, at least 0.12 s): 43 internal pauses across 29 lines (1.5 per line), median 0.28 s, 90th percentile 0.52 s, max 0.84 s (L02, after "The F-Rank Tea Seller." before "Here is episode one."). 10 are 0.4 s or longer and 2 are 0.6 s or longer. Five lines have no internal pause at all (L10, L17, L22, L23, L25) — voice2.py on [tts/line_NN.wav](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/tts/)
- **Joke timing in the voice:** there is no quiet stretch of 0.12 s or more right before "cardamom" (L25, "says: cardamom"), "Oh no" (L21), "They run" (L22), "to go?" (L26) or "nothing special" (L10). There is 0.18 s before "I'm undercharging" (L27). The comic beat comes from the mix instead: the music drops 150.38–151.78 s and a rimshot lands at 152.14 s, 0.86 s after "cardamom" starts at 151.28 s — voice2.py, [events.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/events.json)
- **Pitch** (librosa pYIN, 60–400 Hz; frames more than 1.8× or less than 0.55× the line median removed as octave errors):
  - Overall median F0 is 129.4 Hz.
  - Per-line median F0 spans only 123.5–141.1 Hz (standard deviation 3.8 Hz) across 29 lines.
  - Within-line spread (5th–95th percentile) is a median of 4.9 semitones (min 3.1 on L20, max 7.2 on L28).
  - Within-line standard deviation is a median of 1.49 semitones; interquartile range is 1.2–2.9 semitones.
  - Before cleaning, the 5–95% range over all frames is 115–163 Hz (6.0 semitones).
  
  — voice.py, voice2.py on [tts/line_NN.wav](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/tts/)
- **Pitch shape of lines:** the first 0.6 s of a line sits a median of 0.5 semitones above the line's median and the last 0.6 s a median of 0.8 semitones below. All 7 lines with a question end flat or falling after cleaning (-0.3 to -1.9 semitones): L08 "Is it poisoned with weakness?", L15, L17, L24, L26, L27, L29. Only L03 (+8.3, likely a trailing artifact, see below) and L14 (+3.7) end higher — voice2.py
- **Possible voice artifacts, to check by ear:**
  - L17 "Did he just one-shot it?": the final "it?" has 0.40 s tracked at about 358 Hz with voicing probability 0.62. That is either a squeaky rise or a glitch.
  - L03: about 0.3 s of pitched sound at about 262 Hz (voicing probability 0.43) comes after the last word "rich.".
  - All other frames above 1.8× the median have voicing probability of 0.28 or less, which points to tracker noise.
  
  — voice3.py on [tts/line_17.wav, line_03.wav](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/tts/)
- **Loudness across lines:** before the mix normalises the voice, per-line integrated loudness ranges from -23.8 LUFS (L26) to -18.9 LUFS (L21, L22), standard deviation 1.24 LU. The per-line median speech-frame RMS is -21.6 dBFS (line medians -24.8 to -18.5). Per-line LRA is 0.0–5.6 LU, except about 20 LU on two 3.2 s lines where the measurement is unreliable — voice.py, voice3.py, ffmpeg ebur128 per line
- **Emotion tags vs delivery** (mean of per-line values; F0 and range after cleaning):

  | Tag | Lines | F0 (Hz) | Range (semitones) | WPM | LUFS |
  |---|---|---|---|---|---|
  | Excited | 2 | 126.4 | 4.3 | 151 | -22.2 |
  | Shocked | 2 | 127.8 | 5.9 | 169 | -21.0 |
  | Funny | 6 | 129.6 | 4.7 | 150 | -21.4 |
  | Mysterious | 4 | 130.7 | 5.4 | 155 | -21.6 |
  | Warm | 3 | 131.2 | 5.1 | 182 | -21.4 |
  | Serious | 2 | 129.8 | 4.6 | 170 | -20.6 |
  | Untagged | 10 | 128.5 | 4.7 | 171 | -21.4 |

  Kruskal-Wallis tests across the tag groups find no difference: F0 p=0.51, range p=0.61, WPM p=0.31, LUFS p=0.92. Excited + shocked + funny lines (n=10) against untagged lines (n=10): F0 128.6 vs 128.5 Hz (p=0.57), range 4.9 vs 4.7 semitones (p=0.79), loudness -21.5 vs -21.4 LUFS (p=0.85). Only WPM differs, 154 vs 171 (p=0.21, not significant). The "excited" lines have the lowest pitch and narrowest range of any group — voice.py, voice2.py
- **Spectral balance of the clone** (voice.wav, 24 kHz, Welch power relative to the 50 Hz–12 kHz total):

  | Band | Clone voice.wav | Reference ref_cut.wav |
  |---|---|---|
  | 50–200 Hz | -5.2 dB (30.5% of power) | -4.9 dB |
  | 200–500 Hz | -2.5 dB (56.6%) | -2.5 dB |
  | 500–2000 Hz | -8.9 dB (12.8%) | -9.6 dB |
  | 2–5 kHz | -34.5 dB | -35.0 dB |
  | 5–8 kHz | -38.0 dB | -36.8 dB |
  | 8–12 kHz | -45.5 dB | -40.4 dB |

  For the clone, the 2–5 kHz presence band is 29.3 dB below the band under 200 Hz, and the median spectral centroid over speech is 515 Hz. The clone matches the reference within about 1 dB up to 8 kHz and has about 5 dB less energy at 8–12 kHz — voice.py, voice2.py on [voice.wav](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/voice.wav) and the reference file named by VOICE_REF in ~/.cache/tea-break/env.sh
- **Noise:** in natural pauses inside lines, the noise floor (10th percentile of 20 ms frames) is a median of -59.5 dBFS (worst -54.1 dBFS), against speech at about -21.6 dBFS, so roughly 38 dB below speech. The inserted 0.2 s and 0.5 s gaps are digital silence. In the final video the music covers every gap — voice2.py, voice.py
- **Script style for the voice:** 61 sentences with a median of 7 words; present tense; third person; dialogue reported with "says:/asks:/thinks:" rather than acted. Example: L07 "Viktor points at Arjun and laughs. Look, everyone, it's the F-Rank tea boy!" is the narrator saying Viktor's line, in the same voice, with no change of character. There are 8 questions: 1 rhetorical question to the audience (L29 "what do you think is inside the Gate?") and 7 that are characters' lines voiced by the narrator. Joke timing relies on the wording plus the mix's music drop and rimshot, with no vocal pause — [recap.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json), voice2.py

### Inferences
- A within-line spread of about 5 semitones, near-identical median pitch on every line and falling pitch on every question point to an even, "reading" delivery. On these numbers, tagged "excited" or "shocked" lines cannot be told apart from neutral narration.
- The dark spectrum comes from the reference recording, not the TTS: the clone copies the reference's tone almost exactly. From general speech-acoustics knowledge (not measured here), a typical voice's 2–5 kHz band is roughly 15–20 dB below total power, so -34.5 dB is darker than usual. This should be checked against a known-good human recording before acting on it.

### Gaps
- There are no human listening checks or comparison recordings (for example a competitor narrator) to calibrate "flat" against. The pitch statistics are relative to this voice only.
- Pitch-tracker errors were removed with a fixed 0.55×–1.8× window. A real expressive jump outside it (the L17 "it?") would have been removed too.
- The emotion tests are on small groups (n=2 to 10 lines), so "no difference" means none detectable here.

## Packaging: title, description, tags, thumbnail, chapters, end screen

### Takeaway
The title is 68 characters, built as "premise with a number | series name, Episode 1". The description is 567 characters with one WEBTOON link and no timestamps, so there are no chapters. There are 10 generic tags. The thumbnail is two panel crops with one line of text that nearly repeats the title. No end screen or cards are set up. The long video goes into the playlist "Funny True History Stories", which promises true stories.

### Cited Findings
- **Title:** "His Tea Gives You 1 Hour of Power | The F-Rank Tea Seller, Episode 1" — 68 characters, 15 words. The part before the "|" is 33 characters. Formula: second-person premise with a digit ("1 Hour"), then the series name, then the episode number — [recap.json meta](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json), [upload.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/upload.json)
- **Description:** 567 characters, 95 words, 5 paragraphs, in this order:
  1. A 2-sentence logline: "A boy who sells tea next to a monster Gate is the weakest hunter on Earth. But anyone who drinks his tea becomes unstoppable, for exactly one hour."
  2. "Read Episode 1 free on WEBTOON:" plus the link https://www.webtoons.com/en/canvas/the-f-rank-tea-seller/list?title_no=1182633
  3. "New episode every Thursday. What do you think is inside the Gate? Tell me in the comments!"
  4. A credit: "The F-Rank Tea Seller is our own webtoon by Tea Break Comics. Created by Manoj, made with AI tools."
  5. An AI note: "The voice is an AI copy of my own voice, the pictures are made with an AI image model, and the music is original."
  
  It has 1 link, 0 hashtags and 0 timestamps — [upload.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/upload.json)
- **WEBTOON status:** the WEBTOON Canvas episode is recorded as live ("Episode 1 published Oct 29, 2026; weekly on Thursdays") — [PUBLISH.txt](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/upload/PUBLISH.txt)
- **Tags:** 10 tags, 93 characters in total: webtoon, manhwa, manga recap, webtoon recap, the f-rank tea seller, fantasy comedy, hunter, dungeon, tea, anime — [upload.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/upload.json)
- **Other upload settings:** category 24 (Entertainment), language en, made for kids false, "altered or synthetic content" (containsSyntheticMedia) true, private until publish_at. The YouTube API calls are in upload.py — [upload.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/upload.json), [upload.py](file:///home/user/HUGGING-FACE/videos/doodle/upload.py)
- **Publish times:**
  - Long video: 2026-10-30 12:30 UTC, a Friday, 18:00 IST.
  - Short: 2026-11-01 12:30 UTC, a Sunday.
  - The channel config's default long-video day is Saturday 18:00 IST, and the narration and description say a new episode comes "every Thursday" (WEBTOON's schedule).
  
  — [recap.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json), [config.json](file:///home/user/HUGGING-FACE/videos/teabreak/config.json)
- **Playlists:** the long video is set to playlist PLUAmyQAv4d68, "Funny True History Stories", whose description says "Every word is true, with the sources in each video's description". The Short goes to PLNMchGZEVlZw, "Funny History Shorts" ("Every word is true"). recap.py reuses the Tea Break "long" and "shorts" playlists — [upload.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/upload.json), [config.json](file:///home/user/HUGGING-FACE/videos/teabreak/config.json), [recap.py step_upload](file:///home/user/HUGGING-FACE/videos/manga/recap.py)
- **Thumbnail** (I looked at the image): 1280x720 JPEG, 217 KB.
  - The left 512 px show Viktor in silver armour with glowing hands and blue eyes (crop of p19, without lettering).
  - The right 720 px show a close-up of Arjun's deadpan face with lanterns behind (p30).
  - A 48 px dark gap separates the two.
  - The bottom 145 px are a black band at 67% opacity with one line of Bangers 112 px text: "HIS TEA = " in white and "1 HOUR OF POWER" in yellow #ffd43b, with an 8 px black outline.
  - There is no tea or cup, no monster, no series logo or name, no episode number and no channel branding. Mean brightness is 110/255.
  - The text (5 words plus "=") repeats the title's first half.
  
  — [recap_thumbnail.jpg](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/out/recap_thumbnail.jpg), [recap.py thumbnail()](file:///home/user/HUGGING-FACE/videos/manga/recap.py)
- **Chapters:** none. The description has no timestamps — [upload.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/upload.json)
- **End screen:** none configured. upload.py has no end-screen or card code. The video's last 13.3 s are the static "TO BE CONTINUED" frame under the spoken CTA, with no empty area left for end-screen elements — [upload.py](file:///home/user/HUGGING-FACE/videos/doodle/upload.py), frames 180–189.6 s

### Inferences
- The title leads with the hook and uses the series name as a suffix. Neither the title nor the tags say "recap" in a search-style phrase beyond the generic "manga recap" and "webtoon recap" tags.
- Putting a fictional webtoon in a playlist that says "Every word is true" contradicts that playlist's promise.

### Gaps
- There is no CTR, impression or retention data (the video is not public). Whether YouTube suggests an automatic end screen cannot be known from local files.

## The Short and the TikTok parts: lengths, hooks, labels, end cards, safe areas

### Takeaway
The Short is 44.4 s: 8 lines (6 reused from the recap, 2 new) over 8 panels, shown full width. It opens on "This knight drank tea from the weakest hunter on Earth," and ends on a spoken WEBTOON CTA over the first Arjun panel. It has no on-screen label, title or end card, and it never mentions the one-hour limit that its "sixty minutes" payoff depends on.

The three TikTok parts (67.9 / 66.7 / 62.9 s) are the whole recap re-framed vertically and cut at line pauses. Each has a "PART n/3 · THE F-RANK TEA SELLER" label at the top and a 2.5 s end card. Parts 2 and 3 start mid-story with no "previously" line.

### Cited Findings
- **Short, format:** 1080x1920, 30 fps, 44.4 s (voice 41.42 s + 3 s tail), -14.6 LUFS — ffprobe on [short.mp4](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/out/short.mp4), [short.log](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/short.log)
- **Short, script:** 8 lines and 99 words: 143 wpm over the voice and 134 over the video. Panel order: p12, p19, p20, p25, p26, p29, p30, then p05. Lines 2–7 reuse recap L15, L16, L20, L21, L24 and L25. The two new lines are:
  - opening: "[excited] This knight drank tea from the weakest hunter on Earth, and became unstoppable."
  - closing: "[warm] Read this story free on WEBTOON, with a new episode every Thursday."
  
  Whisper matched all 99 words — [recap.json short](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json), [voice.log](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/voice.log)
- **Short, hook (first 3 s):** "This knight drank tea from the weakest hunter on Earth," spoken over p12 (Viktor gulping, the GULP sound-effect word and the bubble "…Hmph. Nothing special."). The frame also shows the bottom of p11's box ("Meera. Healer. The only nice one in the party.") above and p13's bubble ("GOOD LUCK IN THERE.") below — [short timing.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/short/timing.json), frames 0.3/1.5/3.0 s in short_A.jpg
- **Short, story gap:** the words "hour" or "one hour" are never said. Line 4 says "the clock reaches sixty minutes" with no set-up. "Viktor" is first named in line 4 and "Arjun" in line 6, neither introduced — [recap.json short](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json)
- **Short, pacing:** 7 panel changes (9.46 per minute); panels hold 3.46–7.78 s (median 5.74). The camera moves in 12.8% of frames. Every panel fits the vertical view, so none is scrolled.
  - Music: 6 mood segments — playful 5.3 s, dramatic 15.5 s, playful 6.0 s, dramatic 6.4 s, silence 3.4 s, warm 8.8 s.
  - Effects: stings hit, wahwah and rimshot; 1 punch music-stop; 7 whooshes.
  
  — analyze.py, [short.log](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/short.log), [short/events.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/short/events.json)
- **Short, visuals:** the strip fills the full 1080 px width (100%) and each frame shows 1,422 px of strip height, so neighbouring panels' lettering is on screen. Captions are Patrick Hand 84 px, at most 4 words / 22 characters, bottom margin 330 px (bottom of the caption at about y=1590 of 1920); 35 captions. There is no on-screen title, series label, hook text or end card — [captions.py](file:///home/user/HUGGING-FACE/videos/doodle/captions.py), [short/captions.ass](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/short/captions.ass), frames short_A.jpg
- **Short, ending:** the last move, from p30 back up to p05, scrolls backwards through about 32,700 px of strip in 0.8 s; other panels (p23 SLASH!, p14 Dungeon Gate, the wolves) flash past at 36.9–37.1 s under the caption "Read this story free". The Short ends on p05 (Arjun, "CHAI! HOT CHAI! TEN RUPEES A GLASS!") for about 7 s — [recap.py camera_path](file:///home/user/HUGGING-FACE/videos/manga/recap.py), [panels.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/out/webtoon/panels.json), frames 36.9/37.1/40/44.2 s
- **Short, packaging:** title "He drank the F-Rank's tea... #webtoon #manhwa" (45 characters). Description is 330 characters: "The weakest hunter's tea gives you one hour of power. Read The F-Rank Tea Seller free on WEBTOON: [link]" plus the credit and AI note. Tags are the first 5 long-video tags plus "shorts". It publishes 2026-11-01 12:30 UTC — [upload.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/upload.json)
- **TikTok, lengths and cuts:** part 1 is 67.87 s (body 0–65.31 s), part 2 is 66.67 s (body 65.31–129.43 s) and part 3 is 62.90 s (body 129.43–189.80 s); each adds a 2.5 s end card. Cuts fall in the pause after the first line that pushes a part past 61.5 s. Part 1 ends after "Is it poisoned with weakness?" and part 2 after "…and the clock reaches sixty minutes." The audio is the 16:9 recap mix — [tiktok.log](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/tiktok.log), [recap.py step_tiktok](file:///home/user/HUGGING-FACE/videos/manga/recap.py), analyze.py
- **TikTok, hooks (first 3 s):**
  - Part 1: "This boy is the weakest hunter on Earth."
  - Part 2: "Meera, the healer, is the only nice one on the team."
  - Part 3: "The golden light fades away. His sword…"
  
  Parts 2 and 3 have no recap line — [timing.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/timing.json)
- **TikTok, label:** "PART n/3 · THE F-RANK TEA SELLER" in Bangers 58 px, white on a 60%-opacity black box, centred at y=190, for the whole body. It sits over the comic art and covers part of whatever panel is behind it — [recap.py](file:///home/user/HUGGING-FACE/videos/manga/recap.py), [label1.txt](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/tiktok/label1.txt), frames tk1–3.jpg
- **TikTok, safe areas:** captions are 84 px with a bottom margin of 560 px (bottom of the caption at about y=1360); 155 captions. The code comment says "TikTok covers the top ~150 px (tabs) and the bottom ~500 px (name, caption, sound): keep text between" — [recap.py](file:///home/user/HUGGING-FACE/videos/manga/recap.py), [tiktok/captions.ass](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/tiktok/captions.ass)
- **TikTok, end cards** (2.5 s each): a dark #0d0d0f page with the 900x900 series cover (Arjun with "THE F-RANK TEA SELLER" logo) at y=260. Below it, Bangers 110 px text: "PART 2 IS NEXT" (yellow) / "FOLLOW SO YOU" / "DON'T MISS IT!" on part 1 ("PART 3 IS NEXT" on part 2), and "READ IT FREE" / "ON WEBTOON" / "THE F-RANK TEA SELLER" on part 3. The card audio is the raw music at ×0.35 with fades — [recap.py end_card()](file:///home/user/HUGGING-FACE/videos/manga/recap.py), frame 66.5 s in tk1.jpg, 62.0 s in tk3.jpg
- **TikTok, part 3 ending:** part 3 keeps the YouTube wording "The link is in the description" and "tell me in the comments". It also holds the static TO BE CONTINUED frame for about 13 s before its end card (frames at 50.0 s and 59.5 s are identical) — [recap.json L29](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json), tk3.jpg

### Inferences
- The Short is self-contained in look but not in story: the one-hour rule behind its payoff is never stated, and the closing CTA panel is reached by a 0.8 s blur through the whole strip.
- The TikTok parts carry series identity (label + cover card) that the YouTube Short and the 16:9 recap do not have.

### Gaps
- I could not test how YouTube's or TikTok's current interfaces overlap the frames (no device previews). The safe-area numbers are the code's own assumptions plus caption pixel positions.

## Things that look broken or inconsistent (observations only)

### Takeaway
Nothing is technically corrupt: every file decodes, durations match the logs, and loudness is on target. There are, however, about ten content and metadata mismatches worth a human look.

### Cited Findings
- **Wrong playlists:** the fiction recap and Short go into the Tea Break true-history playlists ("Every word is true") — [upload.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/upload.json), [config.json](file:///home/user/HUGGING-FACE/videos/teabreak/config.json)
- **Emotion tags do nothing:** no emotion reference samples exist (refs.json `{}`), and excited/shocked/funny lines measure the same as neutral ones — [tts/refs.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/tts/refs.json), voice analysis above
- **Short story gap:** the Short's payoff ("the clock reaches sixty minutes") has no "one hour" set-up, and character names are used without introduction — [recap.json short](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json)
- **Short blur scroll:** the Short's final camera move is a 0.8 s backwards scroll through about 32,700 px of the strip (36.6–37.4 s) — [recap.py](file:///home/user/HUGGING-FACE/videos/manga/recap.py), short_A.jpg
- **YouTube wording on TikTok:** TikTok part 3 says "The link is in the description" and "tell me in the comments" — [recap.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json), [recap.py](file:///home/user/HUGGING-FACE/videos/manga/recap.py)
- **Captions over lettering:** in the 16:9 recap, captions cover parts of narration boxes and bubbles (7 of 36 sampled frames) — recap_A–C.jpg
- **Punchlines readable early:** punchline bubbles are readable 1–4 s before they are spoken (8.4 s for "I'm undercharging") — [timing.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/timing.json)
- **"sad" mood dropped:** the "sad" cue for "They crawl out of the Gate" was silently dropped (shorter than 3.0 s), so that line plays over playful music — [video.log](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/video.log), [score.py](file:///home/user/HUGGING-FACE/videos/doodle/score.py)
- **Possible pitch glitches:** L17 "it?" (about 358 Hz for 0.4 s) and L03 (pitched sound after "rich.") need a listen — voice3.py
- **Skipped cold open:** the strip's own cold open (p01 glowing Viktor, p02 "One hour earlier…") is skipped, and the camera starts on p05 then jumps back up to p03 during the intro — [recap.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json), [episode.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/episode.json)
- **Spelled-out numbers:** captions show "twenty thirty-one", "fifty-eight" and "sixty minutes" while the title and thumbnail use "1 Hour" — [captions.ass](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/captions.ass)
- **Publish day:** the long video is scheduled for a Friday, while the channel config's long-video day is Saturday; the narration and description say a new episode every Thursday — [recap.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json), [config.json](file:///home/user/HUGGING-FACE/videos/teabreak/config.json)
- **Harmless log noise:** voice.log contains "sox: not found" warnings; the voice step still completed — [voice.log](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/voice.log)

### Inferences
- The playlist mismatch and the Short's missing "one hour" set-up are the two items most likely to confuse a viewer. The emotion-tag finding means the script's tags currently have no effect on delivery.

### Gaps
- I did not play any file, so possible audio glitches (L17, L03) are flagged from measurements only.
