"""Talking shots on the owner's own private ZeroGPU Space (Rggroups/anime-motion): LongCat-Video-Avatar 1.6.

One start picture + one voice line (+ a short prompt) -> a 5-second lip-synced clip at 25 fps, no sound.
Model: meituan-longcat/LongCat-Video-Avatar-1.6 (MIT licence). The longcat_video/ package is Meituan's MIT
LongCat-Video code as ported to ZeroGPU in the Space victor/LongCat-Video-Avatar-1.6 (copied from a pinned
revision by space_app.py, after it was read; the vocal separator and the prompt enhancer are left out).
This app file is new: no web page, two API endpoints (/talk on half a GPU, /talk_xl on a full one).
"""
import spaces  # noqa: F401  (must be imported before torch)

import json
import math
import os
import sys
import tempfile
import time
import types
import uuid
from pathlib import Path

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import gradio as gr
import imageio
import numpy as np
import torch
import torch.nn.functional as F
from huggingface_hub import snapshot_download
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.resolve()))

WEIGHTS = Path("weights")
BASE_DIR = WEIGHTS / "LongCat-Video"
AVATAR_DIR = WEIGHTS / "LongCat-Video-Avatar-1.6"
MODEL_TYPE = "avatar-v1.5"  # 1.6 uses the 1.5 (Whisper) audio path, without loudness normalisation
FPS, FRAMES = 25, 125
NEGATIVE = ("Close-up, bright tones, overexposed, static, blurred details, subtitles, style, works, paintings, images, "
            "overall gray, worst quality, low quality, JPEG compression residue, ugly, incomplete, extra fingers, "
            "poorly drawn hands, poorly drawn faces, deformed, disfigured, misshapen limbs, fused fingers, "
            "still picture, messy background, three legs, many people in the background, walking backwards")


def sdpa_shim():
    """The DiT calls xformers' memory_efficient_attention; send it to torch's own SDPA instead (no xformers wheel)."""
    try:
        import xformers.ops as xops
    except Exception:
        xf = types.ModuleType("xformers")
        xops = types.ModuleType("xformers.ops")
        xf.ops = xops
        sys.modules["xformers"], sys.modules["xformers.ops"] = xf, xops

    class BlockDiagonal:
        def __init__(self, q_seqlen, kv_seqlen):
            self.q_seqlen, self.kv_seqlen = list(q_seqlen), list(kv_seqlen)

        @classmethod
        def from_seqlens(cls, q_seqlen, kv_seqlen):
            return cls(q_seqlen, kv_seqlen)

    try:
        bias = xops.fmha.attn_bias
    except Exception:
        bias = types.SimpleNamespace()
        xops.fmha = types.SimpleNamespace(attn_bias=bias)
    bias.BlockDiagonalMask = BlockDiagonal

    def one(q, k, v):
        return F.scaled_dot_product_attention(q.transpose(1, 2).contiguous(), k.transpose(1, 2).contiguous(),
                                              v.transpose(1, 2).contiguous()).transpose(1, 2)

    def attention(q, k, v, attn_bias=None, op=None, **_):
        if attn_bias is None:
            return one(q, k, v)
        if not isinstance(attn_bias, BlockDiagonal):
            raise NotImplementedError(f"attention mask {type(attn_bias)} is not supported")
        outs, qo, ko = [], 0, 0
        for ql, kl in zip(attn_bias.q_seqlen, attn_bias.kv_seqlen):
            outs.append(one(q[:, qo:qo + ql], k[:, ko:ko + kl], v[:, ko:ko + kl]))
            qo, ko = qo + ql, ko + kl
        return torch.cat(outs, dim=1)

    xops.memory_efficient_attention = attention


sdpa_shim()

# 1) weights, once per machine (public models: no token needed)
if not (BASE_DIR / "vae" / "config.json").exists():
    snapshot_download("meituan-longcat/LongCat-Video", local_dir=str(BASE_DIR),
                      allow_patterns=["tokenizer/*", "text_encoder/*.safetensors", "text_encoder/*.json",
                                      "vae/*.safetensors", "vae/*.json"])
if not (AVATAR_DIR / "loraB" / "lora.safetensors").exists():
    snapshot_download("meituan-longcat/LongCat-Video-Avatar-1.6", local_dir=str(AVATAR_DIR),
                      allow_patterns=["base_model_int8/*", "loraA/*", "loraB/*", "scheduler/*",
                                      "whisper-large-v3/model.safetensors", "whisper-large-v3/*.json",
                                      "whisper-large-v3/*.txt"])

# 2) the DiT's attention: the SDPA route above instead of flash-attention / block-sparse kernels
cfg_path = AVATAR_DIR / "base_model_int8" / "config.json"
cfg = json.loads(cfg_path.read_text())
for k in ("enable_flashattn2", "enable_flashattn3", "enable_bsa"):
    cfg[k] = False
cfg["enable_xformers"] = True
cfg_path.write_text(json.dumps(cfg, indent=2))

# 3) load everything on the CPU at start-up; ZeroGPU moves it to the GPU inside each @spaces.GPU call
from transformers import AutoTokenizer, UMT5EncoderModel  # noqa: E402

from longcat_video.audio_process import get_audio_encoder, get_audio_feature_extractor  # noqa: E402
from longcat_video.modules.autoencoder_kl_wan import AutoencoderKLWan  # noqa: E402
from longcat_video.modules.quantization import load_quantized_dit  # noqa: E402
from longcat_video.modules.scheduling_flow_match_euler_discrete import FlowMatchEulerDiscreteScheduler  # noqa: E402
from longcat_video.pipeline_longcat_video_avatar import LongCatVideoAvatarPipeline  # noqa: E402

device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.bfloat16 if device == "cuda" else torch.float32
tokenizer = AutoTokenizer.from_pretrained(str(BASE_DIR), subfolder="tokenizer", torch_dtype=dtype)
text_encoder = UMT5EncoderModel.from_pretrained(str(BASE_DIR), subfolder="text_encoder", torch_dtype=dtype)
vae = AutoencoderKLWan.from_pretrained(str(BASE_DIR), subfolder="vae", torch_dtype=dtype)
scheduler = FlowMatchEulerDiscreteScheduler.from_pretrained(str(AVATAR_DIR), subfolder="scheduler", torch_dtype=dtype)
dit = load_quantized_dit(str(AVATAR_DIR), subfolder="base_model_int8", cp_split_hw=[1, 1])
# 1.6's two distillation LoRAs, mixed per step as in Meituan's 1.6 commands (--mix_steps=4 --mix_alpha=1.0)
dit.load_lora(str(AVATAR_DIR / "loraA" / "lora.safetensors"), "dmd", multiplier=1.0, lora_network_dim=128,
              lora_network_alpha=64)
dit.load_lora(str(AVATAR_DIR / "loraB" / "lora.safetensors"), "opsd", multiplier=1.0, lora_network_dim=128,
              lora_network_alpha=64)
dit.enable_lora_mix("dmd", "opsd", 1.0, 4)
audio_encoder = get_audio_encoder(str(AVATAR_DIR / "whisper-large-v3"), MODEL_TYPE)
audio_features = get_audio_feature_extractor(str(AVATAR_DIR / "whisper-large-v3"), MODEL_TYPE)
pipe = LongCatVideoAvatarPipeline(tokenizer=tokenizer, text_encoder=text_encoder, vae=vae, scheduler=scheduler, dit=dit,
                                  audio_encoder=audio_encoder, audio_feature_extractor=audio_features,
                                  model_type=MODEL_TYPE)
pipe.to(device)
audio_encoder.to(device, dtype=dtype)
print("ready", flush=True)


def load_16k(path):
    import soundfile as sf
    from scipy.signal import resample_poly
    x, sr = sf.read(path, dtype="float32", always_2d=False)
    if x.ndim > 1:
        x = x.mean(axis=1)
    if sr != 16000:
        g = math.gcd(int(sr), 16000)
        x = resample_poly(x, 16000 // g, int(sr) // g).astype(np.float32)
    return np.ascontiguousarray(x, dtype=np.float32)


def run(image_path, audio_path, prompt, resolution, seed, fast):
    if not image_path or not audio_path:
        raise gr.Error("a picture and a voice line are both needed")
    t0 = time.time()
    speech = load_16k(audio_path)
    need = FRAMES * 16000 // FPS
    if len(speech) < need:  # the voice line is padded with silence to the clip length
        speech = np.concatenate([speech, np.zeros(need - len(speech), np.float32)])
    full = pipe.get_audio_embedding(speech, fps=FPS, device=device, sample_rate=16000, model_type=MODEL_TYPE,
                                    use_loudness_norm=False)
    idx = torch.arange(5, device=full.device) - 2  # each frame sees the audio of 2 frames either side
    centre = torch.arange(0, FRAMES, device=full.device).unsqueeze(1) + idx.unsqueeze(0)
    audio_emb = full[torch.clamp(centre, 0, full.shape[0] - 1)][None, ...].to(device)
    if fast:
        pipe.dit.configure_dbcache(enabled=True, fn=1, bn=0, warmup_steps=1, max_cached_steps=3,
                                   max_continuous_cached_steps=1, residual_diff_threshold=0.35, downsample_factor=4)
    else:
        pipe.dit.configure_dbcache(enabled=False)
    with torch.inference_mode():
        frames = pipe.generate_ai2v(image=Image.open(image_path).convert("RGB"),
                                    prompt=(prompt or "A person is talking naturally.").strip(),
                                    negative_prompt=NEGATIVE, resolution=resolution, num_frames=FRAMES,
                                    num_inference_steps=8, text_guidance_scale=1.0, audio_guidance_scale=1.0,
                                    output_type="np", generator=torch.Generator(device=device).manual_seed(int(seed)),
                                    audio_emb=audio_emb, use_distill=True)[0]
    out = os.path.join(tempfile.gettempdir(), f"talk_{uuid.uuid4().hex[:8]}.mp4")
    with imageio.get_writer(out, fps=FPS, codec="libx264", quality=8) as w:
        for f in (frames * 255).clip(0, 255).astype(np.uint8):
            w.append_data(f)
    print(f"made {out} in {time.time() - t0:.1f}s", flush=True)
    return out


@spaces.GPU(duration=200)
def talk(image_path, audio_path, prompt, resolution="480p", seed=42, fast=True):
    return run(image_path, audio_path, prompt, resolution, seed, fast)


@spaces.GPU(duration=150, size="xlarge")
def talk_xl(image_path, audio_path, prompt, resolution="480p", seed=42, fast=True):
    return run(image_path, audio_path, prompt, resolution, seed, fast)


with gr.Blocks(title="Talking shots") as demo:
    gr.Markdown("Private API for talking shots (LongCat-Video-Avatar 1.6).")
    inputs = [gr.Image(type="filepath", label="start picture"), gr.Audio(type="filepath", label="voice line"),
              gr.Textbox(label="prompt"), gr.Radio(["480p", "720p"], value="480p", label="resolution"),
              gr.Number(value=42, precision=0, label="seed"), gr.Checkbox(value=True, label="fast (DBCache)")]
    video = gr.Video(label="clip")
    gr.Button("Make (half GPU)").click(talk, inputs, video, api_name="talk")
    gr.Button("Make (full GPU)").click(talk_xl, inputs, video, api_name="talk_xl")

if __name__ == "__main__":
    demo.queue(max_size=8).launch(show_error=True)
