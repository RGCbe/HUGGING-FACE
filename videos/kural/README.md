# Super Kural

A daily Short for children: one Thirukkural at a time, in order, told as a tiny doodle story in
the channel owner's AI voice, with the couplet written in Tamil on a palm leaf. The daily run is
the `kural-daily` skill (`.claude/skills/kural-daily/SKILL.md`), started by a scheduled task.

| File | What it does |
| --- | --- |
| `kurals.json` | All 1,330 kurals: Tamil text, transliteration, chapter, G. U. Pope's verse translation (1886) and the Drew/Lazarus prose translation (1840/1885), all public domain |
| `config.json` | Channel, first and last kural (the series stops at 1080, before the book of Love), publish time, private voice dataset |
| `next.py` | The next kural, from the channel's public feed, and today's publish time |
| `show.py` | Prints one kural for writing its story |
| `stories/NNNN.json` | A day's story: lines to say, what to draw on each board, the meaning and the lesson |
| `make.py` | Story to finished Short: voice, listening test, timings, scenes, render, captions, music, title, upload details |
| `tts.py` | Chatterbox-Turbo voice in the owner's voice (temperature 0.5 for steadier words) |
| `check.py` | The listening test: Whisper hears each line without seeing the script; any wrong, missing or extra word fails |
| `story.js` | Builds the boards from a story (portrait layout): hook, intro, story, the kural, the lesson |
| `music.py` | Original music: tanpura drone, bansuri-style flute in raga Mohanam, soft tabla, small bells |
| `setup.sh` | Readies a fresh cloud container and writes `env.sh` for make.py |
| `requirements-*.txt` | Exact Python packages for the voice and listening models |

## How a video is put together

1. The hook (story line 1), then the fixed intro "Hello little friends! It's Super Kural time!"
2. The rest of the story, one board per line.
3. The fixed "Now listen to what the great poet Thiruvalluvar says.", with the couplet written in
   Tamil, then the meaning in English.
4. The lesson, then the fixed goodbye "See you tomorrow for the next Super Kural!"

The three fixed lines say the Tamil words (Kural, Thiruvalluvar) that the voice finds hardest.
They were recorded once, kept only from takes Whisper heard exactly, and approved by ear. The
daily lines use plain English, so every word can be checked automatically.

Every new line is voiced, then heard back without the script. A line that is not perfectly
clear is voiced again with another seed (six tries), and the run stops with the words to reword
if it still fails. The finished mix is heard once more, and the music is turned down if it hides
any word.

## Voice files

The voice sample and the fixed clips are not in this repository. They are in a private Hugging
Face dataset (`voice_repo` in config.json), which `setup.sh` downloads with `HF_TOKEN`. The
uploads also need `YT_CLIENT_ID`, `YT_CLIENT_SECRET` and `YT_REFRESH_TOKEN` (see
`../doodle/README.md`). All four are environment variables in the cloud environment's settings.
