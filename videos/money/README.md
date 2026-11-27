# Money Tea Talks (finance Shorts on the Tea Break channel)

The owner's wish (27 Nov 2026): "now add finance genre", "not doodle style", "new playlist", "lets upload in tamil
and use the multi language option", "KEEP AUTODUB". Short money lessons for working people, told as stories with
the numbers worked out on screen. The recipe is `.claude/skills/money-tea-talks/SKILL.md`; a scheduled run makes one
Short for each Tuesday and Friday at 13:00 India time.

## What a Short is

About 50 seconds, Tamil voice (the owner's ElevenLabs clone), flat vector style, in 4 steps:

| Step | On screen | Job |
|---|---|---|
| 1. Hook | the result first (e.g. the finished chart), never the host first | the question with a number in it |
| 2. Story | two invented people, flat pictures moving in 3D | one wise choice, one not; a little funny, never mocking |
| 3. Proof | the money drawn by code (`build.py` scene kinds) | exact numbers, every rate called an example |
| 4. Lesson | number cards, then the host's lesson and a comments question | the punchline number, one line to remember |

English comes from YouTube's automatic dubbing (a Tamil video is dubbed into English only; YouTube's own help page,
"Use automatic dubbing"). The run adds an English title and description and Tamil and English subtitles.

## The rules that are never broken

- **Education only, never advice** (India's market regulator SEBI limits unregistered creators to investor
  education): no stock, fund, app or bank names; no "buy this"; no live prices; no promised returns; no broker,
  course or app promotions; every rate shown on screen as "an example, not a guarantee".
- Every number is computed by Python in the run, and the calculation is kept with the work files.
- A fact (an interest rate, a rule, a law) is checked in two good sources (RBI, NPCI, SEBI, a bank's own schedule
  of charges) before the script is written, and the sources go in the description. A fact that cannot be sourced
  is cut.
- The characters are invented and the description says it is a story. No real people or companies.
- Every word on screen stays inside YouTube Shorts' clear band (y 288-1248, x 48-888): `build.py` stops otherwise.
- The owner's host pictures in `host/` are flat cartoons made from his doodle host, which is allowed in this public
  repository; his photo, voice audio and the videos never are.

## Files

| File | What it does |
|---|---|
| `build.py` | the Short from `WORK/spec.json` + the Tamil voice + `words.json`: scene kinds host, picture, bars, cards, rule; music, mix, subtitles |
| `mouth.py` | the host's lips: 4 mouth shapes drawn on the same picture, chosen from the voice's loudness per frame |
| `check_voice.py` | the listening check (faster-whisper) and the word timings `build.py` follows |
| `next.py` | the next free Tuesday or Friday slot and the next unused topic |
| `subtitles.py` | uploads the Tamil and English subtitles (needs the key's youtube.force-ssl permission) |
| `topics.json` | the topics in order, each in the 4 steps, with the facts each needs sourced |
| `config.json` | slots, voice settings, picture style, the private work dataset |
| `host/` | the owner's flat host: think and comment poses, with their mouth shapes |

## Where data goes

- Pictures: the owner's own private Hugging Face Space (`videos/doodle/imagegen.py --engine auto`, Cloudflare
  Workers AI when its GPU time is used up).
- Voice: ElevenLabs (the owner's account), with ELEVENLABS_API_KEY only.
- Work files: the owner's private dataset `Rggroups/office-tea-talks-work` under `money/SLUG/`.
- YouTube: the Tea Break channel with its own key; Facebook and Instagram through the queue (`videos/meta`), posted
  only by the owner's VPS.
