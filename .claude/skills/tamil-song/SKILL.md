---
name: tamil-song
description: Make a Tamil song sung in the owner's own voice (he does not sing: a solo AI guide singer is re-voiced from his real speech) - a 2-minute rap-kuthu (or another style he names) about a real person or story, built like a Tamil film song (thogaiyara, pallavi, anupallavi, interlude, charanam, ending), lyrics in everyday spoken Tamil checked by lyrics_check.py, the beat from the private music Space (ACE-Step 1.5), checked for clear words, saved to the private dataset. Use for "make a song", "make a song about X", "an anthem for X", or when a scheduled task asks for a song.
---

# Tamil song: one run

Read `videos/music/SONG_CRAFT.md` first: the parts of a Tamil song, the word craft, the beat, the owner's standing
wishes, and what was measured on 25-26 Nov 2026. The worked example is the Vaibhav anthem,
`videos/music/vaibhav/song.json` (v3 lyrics, score 100) and `vaibhav/sample_d.json` (the beat the owner picked).

**Never commit audio** (the owner's voice). Work files stay in `~/.cache/music/SLUG/`; finals go to the private dataset
`Rggroups/music-work/SLUG/`. Commit code and lyric files only, after a key-pattern search over the diff (CLAUDE.md).

## The owner's wishes (all must hold, or the song is not finished)

1. About the person and how they play or live: real facts, each checked in two sources; his own claims marked as his.
2. Every word crystal clear: aim for 70% of the lyric letters heard (faster-whisper medium, `song.py check`); the best
   full song so far, v3, is 52% on his vocal. The owner's ears decide.
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

## 4. The singer: a solo AI guide, re-voiced into his voice

The owner does not sing (26 Nov 2026: "I dont have that skills"), so never ask him to. The route that works
(SONG_CRAFT.md, the 26 Nov table; the worked example is `vaibhav/guide_v3.json`, take 11):

1. The caption asks for ONE solo male singer and "No backing vocals, no gang chorus, no crowd vocals": a crowd cannot
   be re-voiced, and every voice must be his anyway.
2. Pick the take whose vocal scores best in `song.py check` (the v3 guide: 53%).
3. Re-voice it zero-shot from 15 s of his REAL speech (`reference.wav`, cut from `teabreak/natural.opus`):
   `song.py SONG.json voice 1` with `"vc_model": "base"`. It kept the words (52%) and sounded like him (0.73; his
   ElevenLabs clone scores 0.37). Save it as `take_N.vocals.base.wav` and score it with `check-voice base`.
4. The fine-tuned model of his voice (`/learn`, `voices/manoj-seedvc-ft-200steps.pth` in the private dataset) scored
   lower (41%, 0.71); try it again only with more of his real speech (a few minutes of talking).
5. Never ElevenLabs output as training data (its terms forbid using output for competing models), and never text-to-
   speech for sung lines (it reads instead of singing: the owner's verdict, 26 Nov 2026).

## 5. Mix, check, save

- `song.py SONG.json mix` with `"voice_engine": "base"`, `"doubles": true`, `"orig_under": 0` and the hook's
  `"gang_words"`: the band, his re-voiced lead, his doubles left and right, a crowd of him in the hook lines, mastered
  to -14 LUFS (true peak -1 dB). The AI singer's own vocal is never in the mix.
- Check: words heard on his vocal within 5 points of the AI guide's, no clipping; the owner's ears decide.
- `python3 videos/music/song.py SONG.json save`: everything to the private dataset (refused if not private).
- Send the owner the MP3 from the scratchpad, with the words-heard score and what each check found.
