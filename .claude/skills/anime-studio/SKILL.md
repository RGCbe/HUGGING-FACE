---
name: anime-studio
description: Master orchestrator for the 34-agent Anime Studio (.claude/agents/01..34). Coordinates pre-production, Settei, separated backgrounds, key/motion animation, compositing, sound, QA, and YouTube upload.
---

# 34-Agent Anime Studio Orchestrator

This skill coordinates the **34 specialized anime studio agents** in `.claude/agents/` (16 Major + 18 Minor roles) across 8 departments.

## Execution Pipeline Order
1. **Direction (`01`–`03`, `17`–`19`):** Lock story arc, script, continuity rules, and *Ekonte* storyboard.
2. **Design / *Settei* (`04`–`06`, `20`–`21`):** Lock character turnarounds, prop/monster sheets, lighting boards, and hex color keys.
3. **Backgrounds & 3D (`11`, `25`–`26`):** Paint/generate clean location backgrounds separately from characters.
4. **Animation (`07`–`10`, `22`–`24`):** Generate key poses, clean anatomy, bridge motion (End-Frame Chaining / action cuts), and verify no morphing.
5. **Finishing (`12`, `27`–`28`):** Enforce flat cel color consistency and prepare aura/VFX overlays.
6. **Compositing & Editing (`13`–`14`, `29`–`30`):** Layer characters + backgrounds + speed lines + impact flashes + HUDs + J/L-cut pacing.
7. **Sound & Voice (`15`, `31`–`33`):** Generate/align dialogue, SFX, and OST; master to `-14 LUFS`.
8. **Production & QA (`16`, `34`):** Audit every cut frame-by-frame (`ffprobe`, contact sheets) and prepare `upload.json` for YouTube/Meta.
