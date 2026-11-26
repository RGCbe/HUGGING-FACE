---
name: tamil-song
description: Make a Tamil song in the owner's own voice - a 2-minute rap-kuthu (or another style he names) about a real person or story, built like a Tamil film song (thogaiyara, pallavi, anupallavi, interlude, charanam, ending), lyrics in everyday spoken Tamil checked by lyrics_check.py, the beat from the private music Space (ACE-Step 1.5), checked for clear words, saved to the private dataset. Use for "make a song", "make a song about X", "an anthem for X", or when a scheduled task asks for a song.
---

# Tamil song: one run

Read `videos/music/SONG_CRAFT.md` first: the parts of a Tamil song, the word craft, the beat, the owner's standing
wishes, and what was measured on 25-26 Nov 2026. The worked example is the Vaibhav anthem,
`videos/music/vaibhav/song.json` (v3 lyrics, score 100) and `vaibhav/sample_d.json` (the beat the owner picked).

**Never commit audio** (the owner's voice). Work files stay in `~/.cache/music/SLUG/`; finals go to the private dataset
`Rggroups/music-work/SLUG/`. Commit code and lyric files only, after a key-pattern search over the diff (CLAUDE.md).

## The owner's wishes (all must hold, or the song is not finished)

1. About the person and how they play or live: real facts, each checked in two sources; his own claims marked as his.
2. Every word crystal clear: at least 70% of the lyric letters heard by faster-whisper medium on the final mix.
3. Sung like a song, with a melody: never spoken or read.
4. His voice only: lead, gang, every voice (his ElevenLabs clone "Manoj kumar T", or his own recordings).
5. About 2 minutes. Rap-kuthu unless he names another style.

## 1. Ready the container

```bash
for v in HF_TOKEN ELEVENLABS_API_KEY; do [ -n "${!v:-}" ] || echo "missing $v"; done
sudo apt-get install -y -q ffmpeg >/dev/null 2>&1 || true   # its rubberband filter tunes the singing
pip install -q numpy soundfile scipy librosa gradio_client==2.5.0 faster-whisper==1.2.1
pip install -q --index-url https://download.pytorch.org/whl/cpu torch==2.11.0 torchaudio==2.11.0   # stems only
```

The music Space `Rggroups/music` (private, ZeroGPU) runs `/song` (ACE-Step 1.5 XL turbo + 4B LM) and `/voice`
(Seed-VC). If it is asleep, the first call wakes it (a few minutes). Rebuild it only with
`python3 videos/music/build_space.py` (pinned sources; read its notes before changing a pin, and re-run the security
checks of CLAUDE.md for any new version).

## 2. The story and the lyrics

- Find the person's facts and moves (two sources each). Pick the 3-4 moments a fan would shout about.
- Write to the 2-minute map in SONG_CRAFT.md, in Tamil script, everyday spoken Tamil, gang answers in brackets.
  Section tags carry both names, e.g. `[Pallavi - Chorus, sung hook, gang answers]`,
  `[Charanam - Verse, Tamil rap, punchy flow]`, so ACE-Step and the checker both read them.
- `python3 videos/music/lyrics_check.py SONG.json`: fix every finding until the score is 90 or more.

## 3. The beat

Copy `vaibhav/sample_d.json`'s caption (rap-kuthu, 100 BPM) unless the owner asked for another sound; set the
duration to the map (about 115 s) and two seeds. Then:

```bash
python3 videos/music/song.py SONG.json takes     # on the Space, ~1 min of GPU each
python3 videos/music/song.py SONG.json stems     # take_N.band.wav = the beat, take_N.vocals.wav = the guide melody
python3 videos/music/song.py SONG.json check     # how clearly the AI singer sang (the guide's quality)
```

## 4. The singer (the step that is not automatic yet)

No automatic method meets wishes 2, 3 and 4 together (SONG_CRAFT.md, the table). In order:

1. **His own sung takes**, when he gives them: put them on the beat (`rap.py`-style placement by bar), tune lightly to
   the beat's key, double for the gang, mix.
2. **Suno Voices** only after he has read Suno's voice-data terms and said yes (his voice goes to Suno's servers).
3. **A singing model of his voice** trained on 10-30 minutes of his singing, kept private on his Hugging Face, after the
   security checks.

Until one of these exists, do not publish a song: make the beat, the lyrics and a demo with `rap.py` (`"sing": true`
lines), send them to the owner, and say plainly which wish is not met.

## 5. Mix, check, save

- `rap.py PLAN.json` places lines by bar on the beat, makes the gang from his own takes, ducks the beat under the
  voice and masters to -14 LUFS (true peak -1 dB).
- Check the final mix: words heard >= 70% (faster-whisper medium, the script in `song.py check`), no clipping.
- `python3 videos/music/song.py SONG.json save`: everything to the private dataset (refused if not private).
- Send the owner the MP3 from the scratchpad, with the words-heard score and what each check found.
