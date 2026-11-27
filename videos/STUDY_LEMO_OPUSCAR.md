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

## The plan, quick wins first

1. **Lip sync**: wide and round mouth shapes from the voice's brightness, on twos (money host first, then office).
2. **Sound design** in the money builder: an effect on every action, a silence before the punchline, music ducking kept.
3. **Reading-time check** in the money builder (then the others).
4. **Treatment and "not the example again"** steps in the money, office and Tea Break recipes.
5. **Final-file checks**: black frames and a Whisper pass on the final mix.
6. **Music on the scene grid**, with a palette per series (not one marimba loop for everything).
7. **A Comic History pilot** for one Tea Break story (paper puppets on a printed map), shown to the owner before any change to the weekly run.
8. **The India map rule** in every recipe that can show a map.
