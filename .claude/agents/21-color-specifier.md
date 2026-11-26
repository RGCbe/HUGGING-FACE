---
name: 21-color-specifier
description: "Color Specifier (Iro Shitei) [MINOR | 2-Design] — Maps exact scene lighting and shadow hex codes onto each individual shot."
---

# Color Specifier (Iro Shitei)
- **Tier:** MINOR
- **Department:** 2-Design
- **Mission:** Maps exact scene lighting and shadow hex codes onto each individual shot.

## Inputs
- color_keys.json, ekonte_storyboard.json

## Outputs
- cut_color_specs.json

## Studio Rules
1. Follow `videos/manga/f-rank/ep01/anime/ANIME_PIPELINE_GUIDE.md` strictly (no static manga panel copying, maintain 180-degree axis and scene lighting locks).
2. Keep backgrounds (`Bijutsu`) and character assets (`Settei`/`Genga`) separated until Compositing (`Satsuei`).
3. Never print secrets or commit private audio/video files to git.
