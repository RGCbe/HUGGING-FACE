# The F-Rank Tea Seller: where things stand (3 Nov 2026)

## On WEBTOON
- Episode 1 is live: https://www.webtoons.com/en/canvas/the-f-rank-tea-seller/list?title_no=1182633
- Episode 2 is packed in `ep02/upload/` (26 slices, thumbnail, PUBLISH.txt). The owner publishes it on Thu 5 Nov.

## YouTube reviews (private, scheduled, owner's ElevenLabs voice, every word checked)
| Video | Link | Public |
|---|---|---|
| Ep 1 review, 8:18 | https://youtu.be/IkLUX6FkzD8 | Fri 6 Nov 12:30 UTC |
| Ep 1 Short, 1:15 | https://youtu.be/nAF-gsZIiUo | Sun 8 Nov 12:30 UTC |
| Ep 2 review, 6:48 | https://youtu.be/1wQCM-Jbk1E | Fri 13 Nov 12:30 UTC |
| Ep 2 Short, 0:57 | not uploaded yet: YouTube's daily upload limit (`uploadLimitExceeded`) | Sun 15 Nov 12:30 UTC |

The Ep 2 Short and its upload file wait in `~/.cache/tea-break/pending/f-rank-ep02-short/`. Upload it with
`python3 videos/doodle/upload.py ~/.cache/tea-break/pending/f-rank-ep02-short/upload.json` once the limit has
reset, then take the old Ep 2 Short off the schedule. Until then the old one (https://youtu.be/MiYxzFF3pFk,
old voice) is still scheduled for 15 Nov as a fallback.

The old versions in the earlier voice are private with no publish date (taken off the schedule, not
deleted): Ep 1 review `tzr6iIxQg-0`, Ep 1 Short `3Q_9upx0e1k`, Ep 2 review `aQ0Aad6XMIY`. They are deleted
only if the owner asks.

The custom thumbnails were refused (403) until the channel is phone-verified. They are in
`epNN/recap/out/recap_thumbnail.jpg`. TikTok parts (6 for each episode, `tiktok_parts` in recap.json)
are posted by the owner.

## The voice
`"voice_engine": "eleven"` in recap.json: the owner's own ElevenLabs clone **"Manoj kumar T"**, model Eleven v4,
stability 0.3, similarity 0.9 (his pick, sample B). The script's mood tags become audio tags
(`videos/kural/eleven.py`); the Whisper listening check (`videos/kural/check.py`) still hears every piece and
re-voices any piece with a word it can't hear. The key comes only from the environment (`ELEVENLABS_API_KEY`) or
the git-ignored `.env.local`; never ask for it in chat. The Creator plan gives about 161,000 characters a
month, and v4 uses about 0.45 credits a character.

A fresh container needs the voice tools for the listening check:
`KURAL_HOME=$HOME/.cache/tea-break VOICE_ENGINE=eleven FIXED_CLIPS=0 bash videos/kural/setup.sh`
(see `.claude/skills/tea-break-weekly/SKILL.md`).
