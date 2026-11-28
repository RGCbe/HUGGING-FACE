"""Manga panels on ZeroGPU: Animagine XL 4.0, with an optional reference picture (IP-Adapter) that keeps a
character's face and clothes the same from panel to panel.

The model stays loaded in the Space, so nothing is downloaded per panel. Called from build scripts with
gradio_client: Client("Rggroups/manga-panels", token=...).predict(..., api_name="/draw").
"""
import gradio as gr
import spaces
import torch
from diffusers import EulerAncestralDiscreteScheduler, StableDiffusionXLPipeline
from PIL import Image
from transformers import CLIPVisionModelWithProjection

NEGATIVE = ("lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, "
            "worst quality, low quality, low score, bad score, average score, signature, watermark, username, blurry")
QUALITY = ", masterpiece, high score, great score, absurdres"

encoder = CLIPVisionModelWithProjection.from_pretrained("h94/IP-Adapter", subfolder="models/image_encoder",
                                                        torch_dtype=torch.float16)
pipe = StableDiffusionXLPipeline.from_pretrained("cagliostrolab/animagine-xl-4.0", image_encoder=encoder,
                                                 torch_dtype=torch.float16, use_safetensors=True)
pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
pipe.load_ip_adapter("h94/IP-Adapter", subfolder="sdxl_models", weight_name="ip-adapter-plus_sdxl_vit-h.safetensors")
pipe.to("cuda")
BLANK = Image.new("RGB", (224, 224), "white")


def seconds(prompt, negative, seed, width, height, steps, cfg, ref, ref_scale):
    return int(15 + 0.4 * steps)


@spaces.GPU(duration=seconds)
def draw(prompt, negative, seed, width, height, steps, cfg, ref, ref_scale):
    """One panel. ref is a character sheet or earlier panel to copy; ref_scale 0.4-0.7 keeps the look, 0 ignores it."""
    pipe.set_ip_adapter_scale(float(ref_scale) if ref is not None else 0.0)
    return pipe(prompt=prompt + QUALITY, negative_prompt=negative or NEGATIVE, width=int(width), height=int(height),
                num_inference_steps=int(steps), guidance_scale=float(cfg),
                ip_adapter_image=ref.convert("RGB") if ref is not None else BLANK,
                generator=torch.Generator("cuda").manual_seed(int(seed))).images[0]


demo = gr.Interface(
    fn=draw,
    inputs=[gr.Textbox(label="Prompt (Danbooru tags)"), gr.Textbox(label="Negative prompt", value=NEGATIVE),
            gr.Number(label="Seed", value=7, precision=0), gr.Slider(512, 1536, 832, step=64, label="Width"),
            gr.Slider(512, 1536, 1216, step=64, label="Height"), gr.Slider(10, 50, 28, step=1, label="Steps"),
            gr.Slider(1, 12, 5, step=0.5, label="Guidance"), gr.Image(type="pil", label="Reference (optional)"),
            gr.Slider(0, 1, 0.55, step=0.05, label="Reference strength")],
    outputs=gr.Image(type="pil", format="png", label="Panel"),
    title="Manga panels",
    api_name="draw",
)
demo.queue().launch()
