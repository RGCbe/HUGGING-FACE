# Manga / webtoon test: "The F-Rank Tea Seller"

A capability test for making our own webtoon (for WEBTOON CANVAS) and a YouTube episode from it.

| File | What it does |
| --- | --- |
| `gen.py` | draws two character sheets, then six panels with the sheets as reference images (Cloudflare Workers AI, FLUX.2 klein; needs `CF_ACCOUNT_ID` and `CF_API_TOKEN`) into `img/` |
| `letter.py` | letters the panels (speech and thought bubbles, narration boxes, sound effects) into an 800 px wide strip, and cuts it into WEBTOON CANVAS upload slices (800 x 1280 JPG) in `out/` |
| `video.py` | turns the strip into a 1920 x 1080 video, the camera moving panel to panel with the narration (`voice/sec_NN.wav`, made from `narration.txt` with `../kural/tts.py`) |
| `example/` | the upload slices from the test |
| `space/` | our private ZeroGPU Space `Rggroups/manga-panels`: Animagine XL 4.0 with IP-Adapter Plus, so a character sheet passed as a reference keeps the face and clothes. The model stays loaded there, so nothing is downloaded per panel. Upload changes with `HfApi().upload_folder(repo_id="Rggroups/manga-panels", repo_type="space", folder_path="space")` |
| `draw.py` | draws a list of panels on that Space (`python draw.py f-rank/reftest.json f-rank/out`); about 5 s of the account's daily ZeroGPU time each (5 minutes free, about 55 panels a day) |
| `f-rank/` | The F-Rank Tea Seller: character sheet prompts (`characters.json`), the chosen sheets (`ref/`), a reference test (`reftest.json`) |

Fonts: Bangers and Comic Neue (SIL Open Font License, `fonts/OFL-*.txt`).

Findings: the art is real manhwa quality and the characters stay recognisable across panels when their
sheet is passed as a reference. Cloudflare's safety filter refuses weapons and fights (magic-light action
passes), the model sometimes paints made-up signs in the background, and skin tone drifts a little.

On our own Space (Animagine XL 4.0) there is no filter: swords, blood and monsters draw fine. A reference sheet
at strength 0.65 keeps the clothes exactly and the face close; name the skin tone with several tags
("dark-skinned male, dark skin, brown skin") or it lightens. Hosting a Gradio Space on a free account is only
allowed on ZeroGPU hardware, chosen when the Space is created.
