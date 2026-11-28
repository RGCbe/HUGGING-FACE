---
title: Music
emoji: 🎵
colorFrom: yellow
colorTo: red
sdk: gradio
sdk_version: 6.17.3
python_version: "3.12"
app_file: app.py
pinned: false
license: gpl-3.0
short_description: Private music API (ACE-Step 1.5 + Seed-VC) for Manoj
---

Private, on ZeroGPU. `/song`: ACE-Step 1.5 (MIT; XL turbo DiT + 4B planner LM) makes a full song from a style caption
and lyrics. `/voice`: Seed-VC (GPL-3.0; the 44.1 kHz singing model) re-voices a sung vocal with a reference voice.
Built by `videos/music/build_space.py` from pinned sources; called by `videos/music/song.py`.
