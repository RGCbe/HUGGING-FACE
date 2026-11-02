# The F-Rank Tea Seller: where things stand (2 Nov 2026)

## On WEBTOON
- Episode 1 is live: https://www.webtoons.com/en/canvas/the-f-rank-tea-seller/list?title_no=1182633
- Episode 2 is packed in `ep02/upload/` (26 slices, thumbnail, PUBLISH.txt). The owner publishes it on Thu 5 Nov.

## YouTube reviews (private, scheduled, every word checked)
| Video | Link | Public |
|---|---|---|
| Ep 1 review, 8:09 | https://youtu.be/tzr6iIxQg-0 | Fri 6 Nov 12:30 UTC |
| Ep 1 Short, 1:15 | https://youtu.be/3Q_9upx0e1k | Sun 8 Nov 12:30 UTC |
| Ep 2 review, 6:36 | https://youtu.be/aQ0Aad6XMIY | Fri 13 Nov 12:30 UTC |
| Ep 2 Short, 0:56 | https://youtu.be/MiYxzFF3pFk | Sun 15 Nov 12:30 UTC |

The custom thumbnails were refused (403) until the channel is phone-verified. They are in
`epNN/recap/out/recap_thumbnail.jpg`. TikTok parts (Ep 1: 6, `tiktok_parts` in recap.json; Ep 2: 6)
are posted by the owner.

## Next: the owner's ElevenLabs voice
The owner said the voice in these reviews doesn't sound like him. It came out higher (median 150 Hz
against his 139 Hz), thinner and swinging up to about 190 Hz. He made his own voice clone on ElevenLabs.

1. The key comes only from the environment (`ELEVENLABS_API_KEY`, set in the cloud environment
   settings) or the git-ignored `.env.local`. Never ask for it in chat. Verify with
   `npx -y @elevenlabs/cli@latest onboard check --env-path .env.local` (it never prints the key).
2. Ask the owner the clone's name, and find its voice_id with `GET /v1/voices`.
3. Add an ElevenLabs engine to `videos/kural/tts.py` (one request per piece:
   `POST /v1/text-to-speech/{voice_id}?output_format=pcm_24000`), wire it into `say()` in
   `videos/teabreak/build.py`, and set `"voice_engine"` in both recap.json files. Keep the Whisper check
   (`videos/kural/check.py`). Moods are the `[excited]`-style tags at the start of a line.
4. Make a short sample, and wait for the owner's yes before re-voicing.
5. Re-voice both reviews: `recap.py voice|video|short|tiktok f-rank/epNN`. The two reviews and their
   Shorts are about 13,000 characters.
6. Replace the uploads: upload the new ones private on the same schedule (`recap.py upload`, then
   `../doodle/upload.py`), wait until YouTube has processed them, then delete the four videos above.
   The owner approved replacing them. If the new voice isn't ready by about 5 Nov, ask whether to hold
   the 6 Nov review.

A fresh container needs the voice tools for the listening check:
`KURAL_HOME=$HOME/.cache/tea-break VOICE_ENGINE=qwen FIXED_CLIPS=0 bash videos/kural/setup.sh`
(see `.claude/skills/tea-break-weekly/SKILL.md`).
