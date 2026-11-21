"""Capability test: character sheets, then panels drawn with them as references (FLUX.2 klein)."""
import base64, io, json, os, sys, time, urllib.error, urllib.request, uuid
from PIL import Image

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
MODEL = "@cf/black-forest-labs/flux-2-klein-4b"
STYLE = ("Korean webtoon (manhwa) style digital illustration, clean confident line art, cel shading, vivid colours, "
         "dramatic cinematic lighting, detailed background. No text, no letters, no speech bubbles, no signature.")


def multipart(fields):
    b = uuid.uuid4().hex
    body = b""
    for k, v in fields.items():
        if isinstance(v, bytes):
            head = f'Content-Disposition: form-data; name="{k}"; filename="{k}.png"\r\nContent-Type: image/png'
        else:
            head, v = f'Content-Disposition: form-data; name="{k}"', str(v).encode()
        body += f"--{b}\r\n{head}\r\n\r\n".encode() + v + b"\r\n"
    return body + f"--{b}--\r\n".encode(), f"multipart/form-data; boundary={b}"


def small(name):
    im = Image.open(os.path.join(OUT, name + ".png")).convert("RGB")
    im.thumbnail((500, 500))
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return buf.getvalue()


def draw(name, prompt, w, h, refs=(), seed=11):
    path = os.path.join(OUT, name + ".png")
    if os.path.exists(path):
        return
    fields = {"prompt": f"{prompt} {STYLE}", "width": w, "height": h, "seed": seed}
    for i, r in enumerate(refs):
        fields[f"input_image_{i}"] = small(r)
    url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CF_ACCOUNT_ID']}/ai/run/{MODEL}"
    for attempt in range(3):
        body, ctype = multipart(dict(fields, seed=seed + 1000 * attempt))
        req = urllib.request.Request(url, data=body, method="POST",
                                     headers={"Authorization": "Bearer " + os.environ["CF_API_TOKEN"], "Content-Type": ctype})
        try:
            t = time.time()
            data = base64.b64decode(json.load(urllib.request.urlopen(req, timeout=300))["result"]["image"])
            Image.open(io.BytesIO(data)).save(path)
            print(f"{name}: {time.time() - t:.0f}s, refs {list(refs)}", flush=True)
            return
        except urllib.error.HTTPError as e:
            print(f"{name}: try {attempt + 1} failed {e.code} {e.read().decode(errors='replace')[:160]}", flush=True)
    sys.exit(f"could not draw {name}")


ARJUN = ("Arjun, an 18-year-old Indian boy with warm brown skin, messy black hair, kind brown eyes and a small scar on his left "
         "eyebrow, wearing a cream kurta with rolled-up sleeves, a brown leather apron and a red thread tied on his right wrist")
VIKTOR = ("Viktor, a tall young man with slicked-back silver hair, grey eyes and a confident smile, wearing a long black "
          "coat with gold trim and black gloves")
draw("sheet_arjun", f"Character design: full body, front view, standing straight, on a plain light grey background. {ARJUN}. "
     "He holds a steel tea kettle. Only one person.", 928, 1664)
draw("sheet_viktor", f"Character design: full body, front view, standing straight, on a plain light grey background. {VIKTOR}. "
     "Only one person.", 928, 1664)
draw("p1", "Wide establishing shot at dusk: a busy Indian city market square with a huge swirling blue magic portal gate in the "
     "middle, armed hunters in tactical gear queueing in front of it, and right beside the gate a tiny wooden tea stall with a "
     "hanging lantern and steam rising. No close-up faces.", 1664, 928)
draw("p2", "The boy from image 0, with exactly the same face, hair, clothes, apron and red wrist thread, standing behind a small "
     "wooden tea stall, smiling brightly while pouring hot chai from a steel kettle into small glass cups, steam rising. "
     "Medium shot.", 1328, 1328, ["sheet_arjun"])
draw("p3", "Close-up of the man from image 0, with exactly the same face, silver hair and black coat with gold trim, sneering "
     "and looking down with disgust at a small glass of tea in his hand.", 1328, 1328, ["sheet_viktor"])
draw("p4", "The tall man from image 0 (same silver hair and black coat) laughing and pointing at the boy from image 1 (same "
     "face, cream kurta and brown apron) who stands behind his small wooden tea stall, smiling politely. Both full figure, "
     "market street at dusk.", 1664, 928, ["sheet_viktor", "sheet_arjun"])
draw("p5", "Inside a dark glowing cave: the man from image 0 (same silver hair and black coat) holds up one open hand that "
     "shines with bright golden light, and a giant horned stone golem in front of him cracks and crumbles into harmless "
     "pebbles. His face is amazed. Dynamic fantasy shot, sparkles, no blood.", 1664, 928, ["sheet_viktor"], seed=21)
draw("p6", "Extreme close-up of the face of the boy from image 0 (same face, messy black hair, scar on the left eyebrow), "
     "a calm knowing smile, his eyes glowing faintly gold, face half in shadow, steam from a glass of tea in the foreground.",
     1328, 1328, ["sheet_arjun"])
