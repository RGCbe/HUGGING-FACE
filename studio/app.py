"""Private Studio: images and writing about fictional adults, on ZeroGPU.

Two Apache-2.0 models do the work:
- Chroma1-HD makes the images.
- Qwen3.5-4B (heretic) writes text, and looks at every image to check that
  nobody in it appears to be under 18.

Every prompt and every result goes through safety.py first.
"""

import os
import random
import tempfile
import uuid

import spaces  # must be imported before torch on ZeroGPU
import gradio as gr
import torch
from diffusers import ChromaPipeline
from PIL.PngImagePlugin import PngInfo
from transformers import AutoModelForImageTextToText, AutoProcessor

import safety

# Set STUDIO_IMAGE_MODEL to an empty string to run the studio without the image model.
IMAGE_MODEL = os.environ.get("STUDIO_IMAGE_MODEL", "lodestones/Chroma1-HD")
TEXT_MODEL = os.environ.get("STUDIO_TEXT_MODEL", "MuXodious/Qwen3.5-4B-SOMPOA-heresy-v2")
DEVICE = os.environ.get("STUDIO_DEVICE", "cuda")

SIZES = {
    "Square (1024 × 1024)": (1024, 1024),
    "Portrait (832 × 1216)": (832, 1216),
    "Landscape (1216 × 832)": (1216, 832),
}
LENGTHS = {"Short": 160, "Medium": 400, "Long": 900}
TASKS = {
    "Caption": "Write one short, catchy social media caption (one or two sentences) for this: {request}",
    "Post description": "Write a post description of about 80 words for this: {request}",
    "Character bio": "Write a short profile bio for this fictional adult character: {request}",
    "Short story": "Write a short story based on this idea: {request}",
    "Anything else": "{request}",
}
AGE_CHECK_MAX_SIDE = 640

# ZeroGPU wants models placed on cuda when the module loads, not inside @spaces.GPU.
processor = AutoProcessor.from_pretrained(TEXT_MODEL)
text_model = AutoModelForImageTextToText.from_pretrained(TEXT_MODEL, dtype=torch.bfloat16).to(DEVICE)
pipe = ChromaPipeline.from_pretrained(IMAGE_MODEL, torch_dtype=torch.bfloat16).to(DEVICE) if IMAGE_MODEL else None


def _ask(messages, max_new_tokens, temperature=0.0):
    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
        enable_thinking=False,
    ).to(text_model.device)
    sampling = {"do_sample": True, "temperature": temperature, "top_p": 0.95} if temperature else {"do_sample": False}
    output = text_model.generate(**inputs, max_new_tokens=max_new_tokens, **sampling)
    return processor.decode(output[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()


def _nobody_looks_underage(image):
    small = image.copy()
    small.thumbnail((AGE_CHECK_MAX_SIDE, AGE_CHECK_MAX_SIDE))
    answer = _ask(
        [{"role": "user", "content": [
            {"type": "image", "image": small},
            {"type": "text", "text": safety.AGE_CHECK_QUESTION},
        ]}],
        max_new_tokens=4,
    )
    return safety.image_passes_age_check(answer)


def _save_png(image, seed):
    info = PngInfo()
    info.add_text("ai_generated", "true")
    info.add_text("generator", f"{IMAGE_MODEL} (seed {seed})")
    path = os.path.join(tempfile.gettempdir(), f"studio-{uuid.uuid4().hex}.png")
    image.save(path, pnginfo=info)
    return path


def _image_seconds(prompt, size, steps, guidance, seed):
    return int(20 + steps * 2)


@spaces.GPU(duration=_image_seconds)
def _make_image(prompt, size, steps, guidance, seed):
    width, height = SIZES[size]
    image = pipe(
        prompt=prompt + safety.ADULT_SUFFIX,
        negative_prompt=safety.NEGATIVE_PROMPT,
        width=width,
        height=height,
        num_inference_steps=int(steps),
        guidance_scale=float(guidance),
        generator=torch.Generator("cpu").manual_seed(seed),
    ).images[0]
    return image if _nobody_looks_underage(image) else None


def generate_image(prompt, size, steps, guidance, seed):
    if pipe is None:
        return None, "The image model is turned off in this copy of the studio."
    verdict = safety.check_prompt(prompt)
    if not verdict.allowed:
        return None, verdict.reason
    seed = random.randint(0, 2**31 - 1) if seed is None or seed < 0 else int(seed)
    image = _make_image(prompt, size, steps, guidance, seed)
    if image is None:
        return None, (
            "Blocked: the safety check thought someone in the image might look under 18, "
            "so the image was discarded. Try describing the people as clearly older."
        )
    return _save_png(image, seed), f"Done (seed {seed}). The file is labelled as AI-generated."


def _text_seconds(task, request, length):
    return int(15 + LENGTHS[length] / 8)


@spaces.GPU(duration=_text_seconds)
def _write(task, request, length):
    messages = [
        {"role": "system", "content": [{"type": "text", "text": safety.WRITER_SYSTEM_PROMPT}]},
        {"role": "user", "content": [{"type": "text", "text": TASKS[task].format(request=request)}]},
    ]
    return _ask(messages, LENGTHS[length], temperature=0.8)


def write_text(task, request, length):
    verdict = safety.check_prompt(request)
    if not verdict.allowed:
        return verdict.reason
    text = _write(task, request, length)
    verdict = safety.check_generated_text(text)
    return text if verdict.allowed else verdict.reason


RULES = """
# Private Studio
Images and writing for an adults-only project. **Fictional adults only.**

- Prompts that mention or hint at anyone under 18, or at a real person, are blocked.
- A second AI checks every image. If anyone in it might look under 18, the image is discarded.
- Images are saved with an "AI-generated" label inside the file. Label them as AI wherever you post them.
- Each image uses roughly 30–60 seconds of your daily GPU time; a piece of writing uses 10–60 seconds.
"""

with gr.Blocks(title="Private Studio") as demo:
    gr.Markdown(RULES)

    with gr.Tab("Images"):
        with gr.Row():
            with gr.Column():
                prompt = gr.Textbox(
                    label="Describe the image",
                    lines=4,
                    placeholder="Portrait of a woman in her thirties with curly red hair, soft window light, film photo",
                )
                size = gr.Dropdown(list(SIZES), value=next(iter(SIZES)), label="Size")
                with gr.Accordion("Advanced", open=False):
                    steps = gr.Slider(10, 50, value=30, step=1, label="Steps (more detail, but more GPU time)")
                    guidance = gr.Slider(1.0, 7.0, value=3.0, step=0.5, label="How closely to follow the prompt")
                    seed = gr.Number(value=-1, precision=0, label="Seed (-1 for random)")
                image_button = gr.Button("Generate image", variant="primary")
            with gr.Column():
                image_out = gr.Image(label="Result", type="filepath")
                image_status = gr.Markdown()
        image_button.click(generate_image, [prompt, size, steps, guidance, seed], [image_out, image_status])

    with gr.Tab("Writing"):
        with gr.Row():
            with gr.Column():
                task = gr.Dropdown(list(TASKS), value="Caption", label="What to write")
                request = gr.Textbox(
                    label="Describe what you want",
                    lines=4,
                    placeholder="A caption for a beach photo of a confident woman in her thirties",
                )
                length = gr.Radio(list(LENGTHS), value="Short", label="Length")
                write_button = gr.Button("Write", variant="primary")
            with gr.Column():
                text_out = gr.Textbox(label="Result", lines=16)
        write_button.click(write_text, [task, request, length], text_out)

if __name__ == "__main__":
    demo.launch()
