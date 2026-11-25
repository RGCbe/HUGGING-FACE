# The F-Rank Tea Seller: Real Anime Production & Continuity Blueprint

## 1. Executive Summary & Root Cause Diagnosis

### The Problem in Cut 5
Cut 5 reached a duration of 3:47 with 56 shots, but was paused because:
1. **"Moving Pictures" Stagnation:** It felt like a slideshow of slightly wiggling still photos rather than authentic anime action (*Dragon Ball*, *One Piece*, *Solo Leveling*).
2. **Severe Continuity Breaks:** Every cut caused a visual and momentum disconnect:
   * **Momentum Death:** Characters started at 0:00 momentum on every cut; an arm raised in shot A did not complete the swing in shot B.
   * **Lighting & Time-of-Day Shifts:** Scene S08–S10 appeared as a sunny afternoon, while S13–S15 abruptly switched to dark evening.
   * **Character Face/Costume Mutation:** S01 armor was copper; S02 was silver. S26 Viktor looked 28; S29 Viktor looked 45.
   * **Camera Axis Flipping (180° Rule):** Characters appeared to gaze or move in disconnected directions.

---

## 2. The 4 Continuity Rules (Fixing the Disconnect)

```
[Shot A: Windup (Momentum 0 to 80%)]
       │
       ▼ (Extract Last Rendered Frame)
[Anchor Frame (Pose, Lighting & Hand Position Match)]
       │
       ▼ (Generate Next 1.2s from Anchor)
[Shot B: Strike (Completes Swing 80% to 100%)]
       │
       ▼ (1-2 Frame Inverse Flash)
[Impact Frame (Inverted B&W / Shockwave)]
```

### Rule 1: End-Frame Chaining (Eliminate Pose Resets)
* **Never** generate Shot B from a completely new still image if it directly follows Shot A in the same scene.
* **The Method:** Take the **exact last rendered frame of Shot A** and feed it as the starting visual anchor for Shot B.
* **Why it works:** Hand position, sword angle, hair flutter, and clothing wrinkles carry over continuously across the cut.

### Rule 2: Match-on-Action
* **Never** cut while a character is standing still and then start another shot where they are standing still.
* **The Method:** Cut **in the middle of physical motion**:
  * *Example:* Shot A begins the tea kettle tip. Cut to Shot B *while the tea is mid-air*, completing the pour into the glass from an over-the-shoulder perspective. The human brain stitches the continuous motion across the camera cut.

### Rule 3: Scene-Level Lighting & Palette Lock
* Lock the environmental prompt per scene, not per shot:
  * **The Mumbai Tea Stall:** `"Mumbai Marine Drive, 6:30 PM sunset dusk, warm amber backlight, deep teal shadow grade, Arabian sea background."`
  * **The Dungeon Cavern:** `"Dark underground cavern, cold blue bioluminescent moss, directional torchlight, deep shadows."`
* Apply a unified LUT / Color Grade in FFmpeg over the entire scene sequence so exposure never jumps.

### Rule 4: Audio J-Cuts & L-Cuts (Sound Bridges)
* Never cut video and audio at the exact same split-second.
* **J-Cut:** Allow the tea kettle boiling sound or dungeon monster growl to start **0.4 to 0.6 seconds before** the visual cut occurs. The ear prepares the brain for the next scene, masking the visual transition.
* **L-Cut:** Allow character dialogue or combat reverberation to ring out across the cut into the next shot.

---

## 3. The Two-Pillar Production Architecture

Real anime separates dialogue from combat into two distinct pipelines:

```
                      [Episode Production]
                               │
       ┌───────────────────────┴───────────────────────┐
       ▼                                               ▼
[PILLAR 1: DIALOGUE & ACTING]                [PILLAR 2: COMBAT SAKUGA]
* Characters: Arjun, Meera, Viktor           * Fast Micro-Cuts: 0.8s - 1.5s
* Engine: LongCat-Video-Avatar               * Engine: Pure Text-to-Video
* Synced to ElevenLabs Audio                 * No Static Photo Anchor
* Natural Blinks & Head Tilts                * Impact Frames & Speed Lines
```

### Pillar 1: Dialogue & Acting Pipeline
* **Tool:** LongCat-Video-Avatar 1.6 on your Hugging Face Space (`Rggroups/anime-motion`).
* **Workflow:**
  1. Record the dialogue cut with ElevenLabs (*Manoj kumar T* clone or character voice).
  2. Run the character reference face into LongCat with the audio cut.
  3. Frame dynamically (over-the-shoulder, low-angle smirk, tight eye close-up).
  4. Crop the bottom 16% (`"lip_crop": 0.16` in `shots.json`) to prevent watermark/subtitle artifacts.

### Pillar 2: Action & Combat Pipeline (The Dragon Ball Feel)
* **Tool:** Wan 2.2 / Hunyuan Pure Text-to-Video on ZeroGPU.
* **Key Strategy:**
  1. **Micro-Cuts (0.8s to 1.5s):** Never ask AI for a 5-second fight. Generate short, explosive action beats.
  2. **Action Prompts (No Image Anchor):** Describe body mechanics, perspective, and speed:
     > `"High speed anime battle, armored blonde warrior dashing forward, throwing rapid flurry of glowing punches, rotating camera angle, Dragon Ball sakuga style, 24fps"`
  3. **Composited Anime FX:**
     * Radial speed lines on high-velocity dashes.
     * 2-frame negative/whiteout impact flashes on strikes.
     * FFmpeg camera shake and sub-bass thuds on hits.

---

## 4. Master Character Reference Lock

To prevent face and wardrobe drift across shots:

| Character | Visual Identifiers (Locked Prompt Anchors) | Role & Voice |
|---|---|---|
| **Arjun (18)** | Dark brown skin, messy black hair, white collarless kurta, red waist sash, red string bracelet on right wrist, calm confident gaze. | F-Rank Tea Seller (ElevenLabs library voice) |
| **Viktor Hale** | Tall, slicked-back blonde hair, modern polished silver plate armor (never copper), black cape with silver clasps, golden glowing eyes when awakened. | B-Rank Hunter (Arrogant, loud) |
| **Meera** | Young Indian woman, single thick black braid over shoulder, white healer robe with gold trim, carved wooden staff with green crystal. | Healer (Kind, observant) |
| **The Minotaur** | 10-foot dark stone-skinned beast, cracked glowing horns, heavy chained iron club, glowing red eyes. | Dungeon Boss |

---

## 5. Milestone Action Storyboard: The 30-Second "Awakening" Teaser

This 6-shot sequence demonstrates the full continuity and combat pipeline:

```
[S01: The Pour] ──► [S02: The Gulp] ──► [S03: Eyes Ignite] ──► [S04: The Dash] ──► [S05: The Strike] ──► [S06: Aftermath]
 (Match-on-Action)    (Dialogue Cut)      (Extreme Close-up)     (Speed Lines T2V)     (Impact Flash)       (Quiet Contrast)
```

1. **Shot 1 (2.5s) - The Pour (Dialogue/Setup):**
   * *Visual:* Medium close-up of Arjun pouring amber chai into a glass. Match-on-action from hand to glass.
   * *Voice:* Arjun: *"One hour. That's all you get."* (LongCat)
2. **Shot 2 (1.8s) - The Gulp (Reaction):**
   * *Visual:* Viktor in battered armor inside the dark dungeon, drinking from the glass.
   * *Audio:* J-cut of bubbling energy starts before the cut.
3. **Shot 3 (1.2s) - The Ignition (Close-up Burst):**
   * *Visual:* Macro close-up on Viktor's eyes snapping wide, pupils flaring bright golden.
   * *Engine:* Pure T2V fast burst.
4. **Shot 4 (1.5s) - The Dash (High Speed Sakuga):**
   * *Visual:* Viktor dashes forward with radial speed lines; ground stone shatters beneath his boots.
5. **Shot 5 (0.8s) - The Strike (Combat Impact):**
   * *Visual:* Giant diagonal energy slash through the Minotaur, followed by a 2-frame black-and-white inverse impact flash.
   * *Audio:* Heavy bass drop + metal shear sound effect.
6. **Shot 6 (3.0s) - The Aftermath (Contrast Outro):**
   * *Visual:* Cut back to Arjun's quiet stall in Mumbai evening dusk, casually wiping a tea counter as sirens wail softly in the background.
