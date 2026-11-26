"""SkyReels-V2 on the owner's own private ZeroGPU Space (Rggroups/skyreels): a TEST next to Wan 2.1 (anime-motion).

SkyReels-V2 14B 540P (image-to-video by default, or diffusion forcing) makes a clip from a START picture, or from a start AND an END picture (a key pose
at each end, the way anime is drawn: the model draws the in-betweens). Two modes:
  full  SkyReels' own way: guidance on (the negative prompt counts), 16-20 steps; slow (minutes of GPU per clip)
  fast  a speed LoRA (lightx2v image-to-video, or CausVid for df): guidance off (the negative prompt is
        IGNORED), 4-6 steps
Safety (CLAUDE.md, checked 26 Nov 2026): the diffusers-format repos hold only safetensors weights and no code, pinned
to exact revisions; the LoRA is loaded with use_safetensors=True (the loader would otherwise also accept pickles);
every package pinned, no known vulnerabilities in OSV or NVD that day. Private Space: only the owner's token reaches it.
"""
import os
import tempfile
import time

import gradio as gr
import spaces
import torch
from diffusers import (AutoencoderKLWan, SkyReelsV2DiffusionForcingImageToVideoPipeline, SkyReelsV2ImageToVideoPipeline,
                       UniPCMultistepScheduler)
from diffusers.utils import export_to_video
from huggingface_hub import hf_hub_download
from PIL import Image, ImageOps
from transformers import CLIPVisionModelWithProjection

# i2v (default): the image-to-video model, which also sees the start picture through its CLIP image encoder, with the
# lightx2v step/CFG-distilled LoRA made for image-to-video (Apache-2.0). df: the diffusion-forcing model with the
# CausVid LoRA (made for text-to-video), the first test of 26 Nov 2026. Set the Space variable SKYREELS_MODEL to switch.
KIND = os.environ.get("SKYREELS_MODEL", "i2v")
LORA_REPO, LORA_REV = "Kijai/WanVideo_comfy", "8260d429d19fd7a72304cad059160b95d843913f"
if KIND == "i2v":
    MODEL_ID, MODEL_REV = "Skywork/SkyReels-V2-I2V-14B-540P-Diffusers", "356ff72527c7cd9eeb60702ba47db4316b18d630"
    LORA_FILE, LORA_W = "Lightx2v/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors", 1.0
else:
    MODEL_ID, MODEL_REV = "Skywork/SkyReels-V2-DF-14B-540P-Diffusers", "34d48e4314e985069934d2f43d397f48aa566fd3"
    LORA_FILE, LORA_W = "Wan21_CausVid_14B_T2V_lora_rank32.safetensors", 0.95

vae = AutoencoderKLWan.from_pretrained(MODEL_ID, subfolder="vae", revision=MODEL_REV, torch_dtype=torch.float32,
                                       use_safetensors=True)
if KIND == "i2v":
    enc = CLIPVisionModelWithProjection.from_pretrained(MODEL_ID, subfolder="image_encoder", revision=MODEL_REV,
                                                        torch_dtype=torch.float32, use_safetensors=True)
    pipe = SkyReelsV2ImageToVideoPipeline.from_pretrained(MODEL_ID, revision=MODEL_REV, vae=vae, image_encoder=enc,
                                                          torch_dtype=torch.bfloat16, use_safetensors=True)
else:
    pipe = SkyReelsV2DiffusionForcingImageToVideoPipeline.from_pretrained(MODEL_ID, revision=MODEL_REV, vae=vae,
                                                                          torch_dtype=torch.bfloat16, use_safetensors=True)
pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config, flow_shift=5.0)  # 5.0 for image-to-video
pipe.to("cuda")
pipe.load_lora_weights(hf_hub_download(LORA_REPO, LORA_FILE, revision=LORA_REV), adapter_name="fast",
                       use_safetensors=True)
pipe.set_adapters(["fast"], adapter_weights=[0.0])


def fit(path, width, height):
    """The picture cropped and scaled to exactly width x height (centre)."""
    return ImageOps.fit(Image.open(path).convert("RGB"), (int(width), int(height)), Image.LANCZOS)


def frames_of(seconds):
    n = int(round(float(seconds) * 24))
    return max(17, min(97, (n - 1) // 4 * 4 + 1))  # 4k+1 frames, at most the model's 97-frame window


def gpu_seconds(start, end, prompt, negative, mode, seconds, steps, guidance, width, height, seed):
    per_step = (6.0 if mode == "fast" else 12.0) * frames_of(seconds) / 73 * (int(width) * int(height)) / (832 * 480)
    return int(min(300, 45 + int(steps) * per_step))


@spaces.GPU(duration=gpu_seconds, size="xlarge")  # 14B in bf16 + the umT5 text encoder + the fp32 VAE need the card
def generate(start, end, prompt, negative, mode, seconds, steps, guidance, width, height, seed):
    """start: the first picture (path). end: the last picture (path) or empty. Returns (mp4 path, timing note)."""
    t0 = time.time()
    fast = mode == "fast"
    pipe.set_adapters(["fast"], adapter_weights=[LORA_W if fast else 0.0])
    n = frames_of(seconds)
    extra = {} if KIND == "i2v" else dict(base_num_frames=n, ar_step=0, causal_block_size=None, overlap_history=None)
    out = pipe(image=fit(start, width, height), last_image=fit(end, width, height) if end else None,
               prompt=prompt, negative_prompt=negative or None, height=int(height), width=int(width),
               num_frames=n, num_inference_steps=int(steps), guidance_scale=1.0 if fast else float(guidance),
               generator=torch.Generator("cuda").manual_seed(int(seed)), **extra).frames[0]
    path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
    export_to_video(out, path, fps=24, quality=8)
    return path, f"{KIND} {mode}: {n} frames, {int(steps)} steps, {time.time() - t0:.0f} s on the GPU"


demo = gr.Interface(
    fn=generate,
    inputs=[gr.Image(type="filepath", label="start picture"), gr.Image(type="filepath", label="end picture (optional)"),
            gr.Textbox(label="prompt"), gr.Textbox(label="negative prompt (full mode only)"),
            gr.Radio(["fast", "full"], value="fast", label="mode"), gr.Number(value=3.0, label="seconds"),
            gr.Number(value=6, precision=0, label="steps"), gr.Number(value=5.0, label="guidance (full mode)"),
            gr.Number(value=832, precision=0, label="width"), gr.Number(value=480, precision=0, label="height"),
            gr.Number(value=7, precision=0, label="seed")],
    outputs=[gr.Video(label="clip"), gr.Textbox(label="timing")],
    api_name="generate",
    title=f"SkyReels-V2 test ({KIND})",
)
demo.queue(max_size=8).launch()
