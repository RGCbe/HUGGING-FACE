# Manga / webtoon test: "The F-Rank Tea Seller"

A capability test for making our own webtoon (for WEBTOON CANVAS) and a YouTube episode from it.

| File | What it does |
| --- | --- |
| `gen.py` | draws two character sheets, then six panels with the sheets as reference images (Cloudflare Workers AI, FLUX.2 klein; needs `CF_ACCOUNT_ID` and `CF_API_TOKEN`) into `img/` |
| `letter.py` | letters the panels (speech and thought bubbles, narration boxes, sound effects) into an 800 px wide strip, and cuts it into WEBTOON CANVAS upload slices (800 x 1280 JPG) in `out/` |
| `video.py` | turns the strip into a 1920 x 1080 video, the camera moving panel to panel with the narration (`voice/sec_NN.wav`, made from `narration.txt` with `../kural/tts.py`) |
| `example/` | the upload slices from the test |

Fonts: Bangers and Comic Neue (SIL Open Font License, `fonts/OFL-*.txt`).

Findings: the art is real manhwa quality and the characters stay recognisable across panels when their
sheet is passed as a reference. Cloudflare's safety filter refuses weapons and fights (magic-light action
passes), the model sometimes paints made-up signs in the background, and skin tone drifts a little.
