# The movies-and-series channel: step by step

## A. Setting up the channel (once)

| Step | Who | What |
|---|---|---|
| 1 | Manoj | Create the channel on YouTube (a separate channel under his Google account): **Manoj Explains** (Manoj's choice, 20 Nov 2026), handle **@ManojExplainsMovies** (free on 20 Nov; @ManojExplains belongs to another channel). Never "Marvel" or "MCU" in the name, handle or logo (their trademarks). |
| 2 | Manoj | Give upload permission once, the same way as for Tea Break; the key is saved in the cloud environment's settings as `YT_REFRESH_TOKEN_MOVIES`, never in chat. |
| 3 | Manoj | Put the profile picture on the channel (YouTube's API cannot set it): the logo, made by Claude (`brand/manoj_explains_logo.png`). |
| 4 | Claude | Banner (Manoj's 3D anime face and the channel name, `brand/manoj_explains_banner.jpg`), channel description, keywords, links, playlists ("Marvel lore", "Marvel lore in Tamil", "Before Avengers: Doomsday", later "Long explainers"). |
| 5 | Claude | Upload defaults: not made for kids; AI-content label ticked ("altered or synthetic content": AI pictures and AI voice); English or Tamil as the video language; comments on. |

## B. Every video (Claude, automatic)

1. **Question:** the next one from the topic list (`topics.json`), checked against what the channel already has.
2. **Research:** official pages (Marvel, Disney), Wikipedia, the trade press; every fact in `sources.md`;
   theories marked as theories; spoilers only after the plot is published.
3. **Script, English:** 300-400 words (2-3 minutes); the question first, "here's the thing", three points, the
   answer, a question for the comments. The first line scored with the hook checker (at least 60).
4. **Script, Tamil:** the same story in spoken Tamil, numbers shown as digits in the captions.
5. **Voice:** Manoj's AI voice in both languages; every English word checked with speech recognition, every Tamil
   section checked to be heard as Tamil.
6. **Pictures:** our own 3D anime pictures (no Marvel characters, costumes, logos or actors), Manoj's 3D anime self at the start and
   the end in the outfit for that kind of video; every picture looked at (wrong counts, stray text, anything that
   copies a design is redrawn).
7. **Video:** `lore_video.py`: moving pictures, big captions, ONE/TWO/THREE cards, name cards, our own music and
   sound effects, -14 LUFS; frames and loudness checked.
8. **Title, description, tags:** the title checker, the sources in the description, "pictures and voice made with
   AI" in the description, ESA/Webb credit when its pictures are used.
9. **Upload:** private, scheduled; the English and the Tamil video as two separate videos.
10. **Manoj:** may watch it in YouTube Studio before it goes out; nothing else needed.

## C. Schedule (India time)

| What | When |
|---|---|
| English lore video | 7:00 pm |
| Tamil lore video | 8:00 pm |
| Long compilation (10-15 videos joined, 30-40 min) | Sunday, every two weeks |

**How many a week:** each video in both languages uses about 3,800 of the 161,000 ElevenLabs voice credits a month
(Tea Break and the devotional channel use the same credits). So **four topics a week** (eight videos) fit; a video
every day needs a free voice model first.

## D. Launch: before Avengers: Doomsday (in cinemas 18 Dec 2026)

1. Who is Doctor Doom? (made)
2. What is the Multiverse Saga, in two minutes?
3. Why did the Avengers break up after Endgame?
4. What happened to every Infinity Stone after Endgame?
5. Who are the Fantastic Four, and why does Doom hate Reed Richards?
6. Why is Doomsday the biggest Avengers film since Endgame?

After 18 December: Doomsday questions once the plot is published (spoiler warning in the title).

## E. The rules (never broken)

- No film or trailer clips, stills, posters, comic panels, logos, film music, actors' faces, and no AI pictures of
  Marvel characters or costumes (Disney had AI videos of its characters removed from YouTube in December 2025).
- Every fact has a source; a theory is called a theory.
- Every video is our own script, voice, pictures, music and edit.
