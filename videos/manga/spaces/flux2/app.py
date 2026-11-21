"""Pictures on the owner's own private ZeroGPU Space (Rggroups/pictures): FLUX.2 [klein] 4B (Apache-2.0).

The same model the free picture service (Cloudflare Workers AI, @cf/black-forest-labs/flux-2-klein-4b) runs, so the
pictures look the same: text to image, and editing with up to three reference pictures (image 0 = the picture to
change or the main reference, images 1-2 = more references such as a face). The model stays loaded in the Space.
Called from videos/doodle/imagegen.py --engine own (Gradio's REST API, api_name "/generate").
"""
import gradio as gr
import spaces
import torch
from diffusers import Flux2KleinPipeline
from PIL import Image

pipe = Flux2KleinPipeline.from_pretrained("black-forest-labs/FLUX.2-klein-4B", torch_dtype=torch.bfloat16)
pipe.to("cuda")


def size16(x):
    return max(256, min(2048, int(x) // 16 * 16))


def seconds(prompt, width, height, seed, ref0, ref1, ref2):
    return 20 + 8 * sum(1 for r in (ref0, ref1, ref2) if r)


@spaces.GPU(duration=seconds)
def generate(prompt, width, height, seed, ref0, ref1, ref2):
    """One picture, 4 steps. ref0-ref2: file paths of reference pictures (image 0, 1, 2), or empty."""
    refs = [Image.open(r).convert("RGB") for r in (ref0, ref1, ref2) if r]
    return pipe(prompt=prompt, image=refs or None, width=size16(width), height=size16(height),
                guidance_scale=1.0, num_inference_steps=4,
                generator=torch.Generator("cuda").manual_seed(int(seed))).images[0]


demo = gr.Interface(
    fn=generate,
    inputs=[gr.Textbox(label="Prompt"), gr.Number(label="Width", value=928, precision=0),
            gr.Number(label="Height", value=1664, precision=0), gr.Number(label="Seed", value=7, precision=0),
            gr.Image(label="Image 0", type="filepath"), gr.Image(label="Image 1", type="filepath"),
            gr.Image(label="Image 2", type="filepath")],
    outputs=gr.Image(label="Picture", type="pil", format="png"),
    api_name="generate",
    title="Pictures (FLUX.2 klein 4B)",
)
demo.queue(max_size=20).launch()
