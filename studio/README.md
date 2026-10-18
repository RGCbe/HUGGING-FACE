---
title: Private Studio
emoji: 🎨
colorFrom: purple
colorTo: indigo
sdk: gradio
sdk_version: 6.30.0
python_version: "3.12"
app_file: app.py
pinned: false
license: apache-2.0
short_description: Private image and writing studio for fictional adults
startup_duration_timeout: 1h
tags:
  - not-for-all-audiences
models:
  - lodestones/Chroma1-HD
  - MuXodious/Qwen3.5-4B-SOMPOA-heresy-v2
---

# Private Studio

A private Hugging Face Space for making images and writing about **fictional adults**.

| Job | Model | License |
|---|---|---|
| Images | [lodestones/Chroma1-HD](https://huggingface.co/lodestones/Chroma1-HD) | Apache-2.0 |
| Writing, and the age check on every image | [MuXodious/Qwen3.5-4B-SOMPOA-heresy-v2](https://huggingface.co/MuXodious/Qwen3.5-4B-SOMPOA-heresy-v2) | Apache-2.0 |

## Safety rules built in

1. **Prompts are checked first** (`safety.py`). Anything that mentions or hints at a minor
   (words, ages under 18, school settings, spelling tricks like `t33n`) is blocked, and so is
   anything that points at a real person (celebrities, "my ex", social media handles, links).
2. **Every image is checked after it is made.** The text model looks at the image and answers
   whether anyone looks under 18. Only a clear "NO" lets the image through; anything else
   discards it.
3. **Generated writing is checked** for references to minors before it is shown.
4. **No photo uploads.** The studio only makes images from text, so it can't be used to edit a
   real person's photo.
5. **Images are labelled.** Every PNG carries `ai_generated: true` in its metadata.

The filters are strict on purpose and will sometimes block harmless prompts (for example
"young woman" or "girl"). Describe characters as adults, such as "woman in her thirties".

No filter is perfect, and these can't recognise every real person by name. You are responsible
for only making and publishing content about fictional adults, and for following the rules of
the sites you post on.

## Running it

- Keep the Space **private** (Settings → Visibility).
- Set the hardware to **ZeroGPU** (Settings → Space hardware).
- The first start downloads about 37 GB of models and can take 15–30 minutes.
- Free accounts get 5 minutes of GPU time a day; each image uses roughly 30–60 seconds.
