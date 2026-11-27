# What we learn from Lemo-Opuscar (27 Nov 2026)

The owner (27 Nov 2026): "we are going to study them and from that we improve ourself". Lemo-Opuscar
(https://github.com/lemomo-ai/lemo-opuscar, by Lemomo / LemoLab) is a library of 99 film styles for coding agents,
each a style guide plus a demo film made entirely in code (a web page drawn frame by frame, synthesised and sampled
sound, no video model). This file is our own summary of the methods worth taking, in our own words. We do not copy
their guides into this public repository (see Licence below).

## Licence and safety (checked 27 Nov 2026, commit 439b98a)

- **Films we make with their method are ours**, commercial use included, and need no credit (their LICENSE, "Films
  you make").
- **Code** (core/, tools/, plugin/, demo code) is MIT. **Guides** (every .md, the style guides, image prompts) are
  CC BY-NC 4.0, with an added permission to read, follow and adapt them to make your own films, commercial ones
  included. That permission does **not** cover publishing the guides or our adapted copies, so they never go into
  this repository; our notes stay in our own words, like this file.
- **Clawd** (the small orange character in some of their films) is Anthropic's and is licensed by nobody there:
  never use it.
- **Security** (what we verified in their code; nothing of theirs was installed or run here): no telemetry; model
  downloads are checked against SHA-256 checksums (tools/fetch.sh); the installer clones their repo and runs
  `npm install` (2 packages, locked) and `pip install` with **unpinned** Python packages (we would pin our own);
  edge-tts sends text to Microsoft (Chinese voices only, not used by us); their image styles call the user's own
  image tool (we would use ours). OSV: 0 known vulnerabilities in the npm lockfile; NVD: no CVEs. No SECURITY.md.

## Their method, and where we fall short

| Their rule | What we do now | The gap to close |
|---|---|---|
| **A treatment before anything is drawn**: three possible structures and the one chosen, a logline, a reference work (what to learn, what not to take), a shot list with the reason for each shot, a beat sheet, a cue map, a sound table | our recipes go from the idea straight to the script | add a short treatment step to every recipe (text only, cheap) |
| **Sound is half the film**: every visible action has a sound, three layers (ambience, foley, music), two real silences before the turn, sound used as a transition (J and L cuts) at least twice | voice and music; effects only in the whiteboard engine; no silences | foley on every action (card slides, numbers landing, bars growing, picture cuts) from `videos/doodle/sfx.py`; a silence before the punchline |
| **One timeline drives everything**: sections, tempo and hit points in one file that the picture, the score, the mixer and the subtitles all read; a script checks each hit lands on its beat | scenes follow the voice lines; the music is a loop that ignores the cuts | let `music.py` take the scene times and put cuts and hits on its beats |
| **Pace for the viewer**: a caption stays at least 1.8 s and at least the spoken line + 0.6 s; text that animates in holds about letters ÷ 15 + 1.5 s; a check script measures every text on screen | no check | a reading-time check in the builders, from the texts each frame draws |
| **Camera with reasons**: at least four kinds of move, one signature shot, transitions made from the medium itself (a page turn, ink spreading) instead of fades and hard cuts; the subject fills a third of the frame at key moments | a depth push on pictures, hard cuts | one designed transition per series (e.g. the number card slides away and becomes the next scene) |
| **Performance**: anticipation, action, follow-through; poses blended, never switched; check expressions at final size | covered for the anime clips (ANIME_CRAFT.md), not for the host | host gestures and small head moves between poses |
| **Lip sync from the voice**: loudness for how open, the voice's brightness (spectral centroid) for wide against round, sampled on twos (12 a second), bigger on shouts | loudness only, 4 open shapes | add round mouth shapes chosen by the centroid (ஓ, ஊ round; இ, ஏ wide) in `videos/money/mouth.py` |
| **Review loop**: contact sheets every 1-2 s, 0.2 s strips of key actions, loudness, black-frame check, speech-to-text again on the final mix, one full viewing with sound | contact sheets, clarity.py | add blackdetect and a Whisper pass on the final mix |
| **Not the demo again**: compare the new film with the example on six points (structure, opening, signature shot, camera path, score shape, ending); at least four must differ | every Office Short follows the example's shape | the same six-point check against the recipe's example, so the daily Shorts stop looking alike |
| **Maps**: no borders unless the film is about them; a country's official map where it is in frame; check every map shot enlarged | no rule | ours: any map of India follows the Survey of India's official outline (Jammu and Kashmir, Ladakh and Arunachal Pradesh in full), or shows no borders |
| **Facts file**: each claim with its source and the quoted words | sources in descriptions; sources.json in the money recipe | a FACTS file for every history video too |

## Styles that fit our channels (to learn from, not to copy)

| Our channel | Their styles to study | What to take |
|---|---|---|
| Tea Break history | Comic History Cartoon, 1920s Newsreel, 1920s Silent Film | countries and sides as paper puppets with pinned joints on an old printed map; land changing hands as paper being cut and slapped down; the film as one comic page the camera travels across; year tags and caption boxes; a darker, joke-free panel when history turns violent |
| Money Tea Talks | Spreadsheet Film, Stick-figure Explainer, Isometric Infographic | the answer computed on screen; one hero element that leads the eye; one idea per beat; colour that means a rule fired |
| Office Tea Talks | Stick-figure Explainer, Sci-fi Sitcom Toon (for its timing) | dialogue comedy timing: interruptions, awkward pauses, reaction shots, a last-second reversal |
| Devotional (planned) | Shadow Puppetry, Gilded Illumination, Red Paper-cut | lamp-lit translucent puppets (close to our Tamil tholpavai tradition), carved detail, a stage frame |
| Kiddo Corner | Crayon Picture Book, Paper Pop-up Book, Watercolor | crayon texture that reacts to pressure, a wash that reveals what was hidden, pages that fold up |
| F-Rank / anime | 80s Cel Anime, Manga Panels | hard-edged cel shading, colour sets per lighting, a model sheet first, panels as a page |

## Deeper study: how their toolkit actually works (27 Nov 2026, second pass)

Read in their code and guides (AGENTS.md, DIRECTOR.md, TECHNIQUE.md, core/, the comic-history, scifi-toon,
spreadsheet and shadow-puppet styles and demos). What each part teaches us, and the concrete change for us.

### Workflow

- **Ask once, then never again.** One message with every open question (facts, the user's own material, language,
  whether to see a storyboard), then defaults for everything else. Our scheduled runs already ask nothing; our
  interactive work should batch its questions the same way.
- **Treatment before the example.** They write their own plan (three structures, the chosen one and why) before
  opening the demo, then use the demo only for technique, never its story, shots or timeline. For us: a run writes
  its plan before reading the recipe's example, so the daily Shorts stop copying the example's shape.
- **A fixed style guide, a free story.** Each style guide has the same eleven parts: essence and what it is not;
  materials and rendering; colour logic; type and subtitles; motion; camera grammar (each move, what it expresses,
  what it serves); sound palette; native moves (a menu of moments only this medium can do, each with the kind of
  content it fits); pitfalls; engine; variation space. For us: one such "style bible" per series (Tea Break history,
  Office, Money, Kiddo Corner, devotional), in our own words, so every run keeps the look while the stories vary.

### Picture

- **Every frame is a function of time** (`render(t)`, no state carried between frames, seeded randomness), so any
  frame can be drawn alone. That lets them render with several browser workers at once, each making a segment, joined
  without re-encoding; JPEG frames piped to ffmpeg; film grain added by ffmpeg, never drawn (drawn grain makes frames
  incompressible). Our builders draw every frame in one Python process: splitting the frame range over 3-4 processes
  would cut the build time by about that much.
- **One world-to-screen function**: every effect that follows a subject goes through the same camera transform.
- **Easing helpers** they use everywhere: smoothstep, ease in/out, back (overshoot), a damped spring for settles, a
  monotone cubic for keyframes that never overshoot. Our anime and money scenes would move better with the spring and
  back eases on landings and pops.
- **On twos for characters, smooth for the camera** (same as our ANIME_CRAFT.md).

### Paper puppets (Comic History) — the biggest new capability for Tea Break history

1. An image model draws a **part sheet**: one character's head, torso, upper and lower arms, legs and a few spare
   expression heads, separated, on a flat green background (prompts per character; the second sheet uses the first as
   a style reference).
2. A ~100-line script **keys out the green** (green dominance = g − max(r, b); a smooth alpha ramp; the green fringe
   clamped away) and **cuts every connected piece** into its own PNG, with a numbered debug picture so the joint
   positions can be read off once.
3. The film rigs each character: pivots per part, the arms solved by forward kinematics or two-bone inverse
   kinematics so a hand reaches a target, heads swapped for expressions (a 1.07-1.10× pop on the swap), a thin cream
   card edge around each part so it reads as cut paper, a small shadow between parts and a larger cast shadow on the
   map.
4. Motion on twos, with spring overshoot on hops and landings; one in-between frame with ink motion lines for a big
   strike; impacts spread (camera shake, paper scraps, a hat jumping off).

We can do all of it with our own picture Space (FLUX.2 klein, green-background part sheets) and Python: real
character animation for Tea Break's stories at almost no GPU cost, instead of still pictures moving in depth.

### Lip sync (Sci-fi Sitcom Toon)

Per 1/24 s of each line: **openness** from loudness (RMS, scaled to the line's own 95th percentile, a small floor),
and **brightness** from the spectral centroid (about 1,200 Hz → round, 3,800 Hz → wide), drawn on twos. The mouth is
one parametric shape (open, width, smile, skew) with teeth and tongue inside. For us: give `videos/money/mouth.py` a
width from the centroid (இ, ஏ wide; ஓ, ஊ narrow and round) on top of its four open shapes.

### Sound

- **A score is a map of the story**: each side or character gets its own instrument; the tune passes from one to the
  other when the story turns; a serious section drops every comic sound; the heaviest hit lands at the climax; the
  ending plays both themes together. Every cue is written in film seconds in one file.
- **Real instruments, free**: they use sample libraries under CC0 (free for any use): Versilian's VSCO 2 Community
  Edition and VCSL (orchestra, woodwinds, brass, harp, marimba, bells, gongs, frame drums), FreePats (guitar,
  accordion, kalimba) and Karoryfer; Salamander piano and one drum kit need a credit line (CC BY). No Indian
  instruments, but usable stand-ins: flute (for a bansuri feel), oboe (for a nadaswaram-like reed), frame drums, temple
  bells, gongs. Our music.py synthesises one marimba-and-whistle loop for every series.
- **Plucked strings by physical modelling** (Karplus-Strong waveguide with a buzzing bridge for shamisen and pipa):
  the same bridge buzz is what gives a veena or sitar its sound, so a veena voice for the devotional channel can be
  modelled with no samples at all.
- **Foley from synthesis**: short recipes (noise bursts, filtered sweeps, decaying sine partials) for clicks, paper
  slaps, whooshes, thumps, dings, pops, creaks, a heartbeat; every sound placed on its frame from the film's event
  list.
- **The voice mix**: the voice compressed first (text-to-speech peaks are high), then set by RMS about 10 dB above the
  music; while the voice speaks, the music and foley dip 3 dB and **the music's 300 Hz-4 kHz band dips another 7 dB**
  (room for the words without killing the music). Their percussion-led styles duck music about 12 dB under a
  storyteller. Mastering: two-pass loudnorm to −14 LUFS, a 4× oversampled look-ahead limiter for a true peak at or
  under −1 dBTP (AAC encoding adds peaks a single pass misses), measured again after encoding.
- **Silence is cut hard**: the whole bed stops, at most one sound inside it.

### Checks

- **Reading time** per on-screen text: the page reports every text and its box at each moment; each must stay fully
  in frame for (CJK characters ÷ 4.5 + other characters ÷ 15) + 1.5 s, at least 1.5 s. For Tamil we would count
  letter clusters (a consonant with its vowel sign is one), at about 8 a second (to be checked by eye).
- **Numbers heard by value**: their speech check compares numbers by value, not spelling, and fails a line where a
  number is heard as a different number. Ours compares by eye; Whisper writes Tamil numbers as digits, so a script
  can check them automatically.
- **Mastering refuses bad audio** (truncated, silent, damaged) instead of making a film with it.

## The plan, quick wins first

1. **Clearer voice in every series**: in `videos/doodle/mix.py`, dip the music's 300 Hz-4 kHz band under speech
   (on top of the overall duck). Measured with clarity.py before and after.
2. **Lip sync**: mouth width from the voice's brightness (money host first, then office).
3. **Sound design** in the money builder: an effect on every action (card slide, number landing, bar growing), a hard
   silence before the punchline.
4. **Reading-time check** in the money builder (Tamil letter clusters), then the others.
5. **Numbers heard by value** in the voice checks.
6. **Treatment and "not the example again"** steps in the money, office and Tea Break recipes.
7. **Real instruments**: fetch the CC0 libraries (VSCO 2 CE, VCSL) into the cache, never the repository, and give
   each series its own palette and a score written in film seconds (history: tuba and accordion comedy; money:
   pizzicato and marimba; devotional: flute, oboe, bells, frame drum, a modelled veena; kids: kalimba, glockenspiel).
8. **Faster builds**: render frame ranges in parallel processes and join the segments.
9. **A style bible per series** (the eleven parts above), in our own words.
10. **A Comic History pilot** for one Tea Break story: part sheets from our picture Space, keyed and cut, rigged
    puppets on a printed map. Shown to the owner before any change to the weekly run.
11. **The India map rule** in every recipe that can show a map.
