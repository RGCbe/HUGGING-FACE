# Uncensored model research (October 2026)

Notes from researching uncensored ("abliterated" / "heretic") models on the Hugging Face Hub.

## How models are uncensored

| Method | What it does | Hub tag |
|---|---|---|
| Abliteration | Finds the model's internal "refusal direction" and removes it from the weights. No retraining. | `abliterated` |
| Heretic / ARA | Newer abliteration from [p-e-w/heretic](https://github.com/p-e-w/heretic). Optimises the weights to stop refusals while keeping normal behaviour almost unchanged. | `heretic` |
| Fine-tuning | Further training on data without refusals. Changes the model's style more. | `uncensored` |

## Best models by size

Ranked with the [UGI Leaderboard](https://hf.co/spaces/DontPlanToEnd/UGI-Leaderboard) (1,329 models).
UGI = uncensored knowledge and willingness (higher is better). Willing = how rarely it refuses, out of 10.
Smarts = the leaderboard's NatInt score. Re-run `python research/ugi_rank.py` to refresh.

| Size | Model | UGI | Willing | Smarts | License |
|---|---|---|---|---|---|
| 31B | [coder3101/gemma-4-31B-it-heretic](https://hf.co/coder3101/gemma-4-31B-it-heretic) | 65.7 | 10 | 36.5 | Apache-2.0 |
| 31B | [llmfan46/gemma-4-31B-it-uncensored-heretic](https://hf.co/llmfan46/gemma-4-31B-it-uncensored-heretic) | 65.0 | 10 | 36.4 | Apache-2.0 |
| 26B (4B active) | [MuXodious/gemma-4-26B-A4B-it-SOMPOA-heresy](https://hf.co/MuXodious/gemma-4-26B-A4B-it-SOMPOA-heresy) | 54.0 | 9.5 | 34.5 | Apache-2.0 |
| 35B (3B active) | [llmfan46/Qwen3.6-35B-A3B-uncensored-heretic](https://hf.co/llmfan46/Qwen3.6-35B-A3B-uncensored-heretic) | 50.9 | 10 | 31.6 | Apache-2.0 |
| 9B | [huihui-ai/Huihui-Qwen3.5-9B-abliterated](https://hf.co/huihui-ai/Huihui-Qwen3.5-9B-abliterated) | 43.2 | 9.5 | 19.8 | Apache-2.0 |
| 9B | [trohrbaugh/Qwen3.5-9B-heretic-v2](https://hf.co/trohrbaugh/Qwen3.5-9B-heretic-v2) | 40.5 | 9.5 | 24.2 | Apache-2.0 |
| 4B | [MuXodious/Qwen3.5-4B-SOMPOA-heresy-v2](https://hf.co/MuXodious/Qwen3.5-4B-SOMPOA-heresy-v2) | 44.7 | 10 | 22.4 | Apache-2.0 |
| 8B | [llmfan46/gemma-4-E4B-it-ultra-uncensored-heretic](https://hf.co/llmfan46/gemma-4-E4B-it-ultra-uncensored-heretic) | 38.5 | 10 | 16.4 | Apache-2.0 |
| 357B (32B active) | [ArliAI/GLM-4.6-Derestricted-v3](https://hf.co/ArliAI/GLM-4.6-Derestricted-v3) | 69.8 | 8.8 | 30.9 | MIT |

Findings:
- "Heretic" models beat plain "abliterated" ones at every size.
- Uncensoring costs very little intelligence (Qwen3.6-27B: smarts 33.2 → 29.2, willingness 2.8 → 9.5).
- The leaderboard has not tested open models since July 2026, so Qwen3.8 and DeepSeek-V4.1 variants have no scores yet.

## Commercial use: licenses checked

| Model | License | Commercial use |
|---|---|---|
| Gemma-4 and Qwen3.5 heretic text models above | Apache-2.0 | Yes |
| [lodestones/Chroma1-HD](https://hf.co/lodestones/Chroma1-HD) (images) | Apache-2.0 | Yes |
| [hexgrad/Kokoro-82M](https://hf.co/hexgrad/Kokoro-82M) (voice) | Apache-2.0 | Yes |
| [ResembleAI/chatterbox](https://hf.co/ResembleAI/chatterbox) (voice, cloning) | MIT | Yes |
| [Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice](https://hf.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice) (voice) | Apache-2.0 | Yes |
| Qwen-Image-2.1 and every "Uncensored" re-upload of it | Qwen Research License | **No** (non-commercial only) |
| fishaudio/drama-3 (voice) | Fish Audio Research License | Probably not; check the license |
| FLUX.3 Klein, LTX-2.5 | Custom, gated | Unknown; read the terms after requesting access |
| lodestones/Kroma | Krea 2 Community License | Read the terms |
| Laxhar/noobai-XL-1.1 | Fair AI Public License | Has restrictions; read the terms |
| FLUX.1-dev fine-tunes | FLUX.1-dev non-commercial | Unclear for outputs |

## Running without your own hardware

| Option | Cost | Notes |
|---|---|---|
| Existing public ZeroGPU Spaces | Free | 5 GPU minutes a day on a free account |
| Your own ZeroGPU Space | Free | Up to 2 Spaces on a free account; same 5 minutes a day |
| Inference Providers (e.g. Featherless) | Pay per use | Gemma-4-31B heretic and Huihui Qwen3.5-9B are served there |
| HF PRO | $9/month | 40 GPU minutes a day, extra at $1 per 10 minutes |
| Dedicated GPU Space | From $0.40/hour | L4 (24 GB) is $0.80/hour |

## Rules that apply to what you publish

- **YouTube (2026):** mass-produced, repetitive or "distressing" AI content can't be monetized; realistic AI content must be disclosed.
- **Adult platforms:** OnlyFans reportedly allows AI content only of the verified creator, labelled as AI. Fansly banned photorealistic AI content in June 2025.
- **Law:** the US TAKE IT DOWN Act (May 2025) criminalises publishing sexual deepfakes of real people. Sexual content involving minors, including drawn or AI-generated, is illegal almost everywhere.
- **Hugging Face:** adult content is allowed when tagged `not-for-all-audiences`; sexual content without consent or involving minors is banned.

Check each platform's official policy before relying on these summaries.
