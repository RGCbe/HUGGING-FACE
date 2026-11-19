"""Builds f-rank/ep04/episode.json: Episode 4, "The Night Shift"."""
import json

ARJUN = ("1boy, male focus, solo, young man, dark-skinned male, dark skin, brown skin, short black hair, messy hair, "
         "brown eyes, white kurta, red sash, red string bracelet")
VIKTOR = "1boy, male focus, solo, adult, tall, blonde hair, short hair, slicked back hair, blue eyes, silver armor, black cape"
MEERA = ("1girl, solo, young woman, dark-skinned female, brown skin, long black hair, single braid over shoulder, "
         "brown eyes, white robe, gold trim, holding staff with crystal, healer")
PAATI = "1girl, solo, old woman, grandmother, grey hair in a bun, white cotton sari, wrinkles, wooden walking stick"
LIEUT = ("1boy, solo, adult man in a black suit and black sunglasses, slicked back black hair, red lotus pin on his "
         "chest, black tie")
GOONS = "several big men in red armor with red lotus symbols on their chests"
BOSS = "1girl, solo, woman seen from behind, long black hair in a low bun, red blazer, red lotus earrings"

L, P, S = (1216, 832), (832, 1216), (1024, 1024)
PAATI_REF = "../ep03/out/img/p29.png"
LIEUT_REF = "../ep03/out/img/p12.png"


def panel(name, prompt, size, before=None, after=None, bubbles=None, sfx=None, status=None, ref=None, ref_scale=None,
          gap=None):
    p = {"name": name, "prompt": prompt, "seed": 7, "w": size[0], "h": size[1]}
    if ref:
        p["ref"], p["ref_scale"] = ref, ref_scale or 0.5
    for key, val in (("before", before), ("after", after), ("bubbles", bubbles), ("sfx", sfx), ("status", status),
                     ("gap", gap)):
        if val:
            p[key] = val
    return p


def nar(*texts):
    return [{"text": t} for t in texts]


def b(text, x, y, w, to=None, kind=None, size=None):
    d = {"text": text, "x": x, "y": y, "w": w}
    if to:
        d["to"] = to
    if kind:
        d["kind"] = kind
    if size:
        d["size"] = size
    return d


def fx(text, x, y, size=110, rotate=0, color=None):
    d = {"text": text, "x": x, "y": y, "size": size, "rotate": rotate}
    if color:
        d["color"] = color
    return d


LEFT, RIGHT = (0.24, 0.12), (0.76, 0.12)
eps = [
    panel("p01", "scenery, night, a small closed tea stall with its metal shutter pulled down, a single oil lamp, empty "
          "city street, a giant glowing blue portal in the distance, moonlight, quiet, peaceful", L,
          before=nar("2:13 a.m."), after=nar("Everyone sleeps eventually.")),
    panel("p02", f"{GOONS}, sneaking down a dark city street at night, crouching, tiptoeing, one of them holding a "
          "large empty sack, moonlight, comedy, stealth", L,
          before=nar("Almost everyone."), sfx=[fx("tip... tip... tip...", 0.74, 0.86, 80, -4)]),
    panel("p03", f"{ARJUN}, sleeping deeply on a thin mat in a tiny room behind a tea stall, exhausted, mouth open, "
          "drooling, a steel tea pot beside him, moonlight through a small window, comedy", L,
          ref="../ref/arjun_face.jpg", ref_scale=0.45, after=nar("214 glasses will do that to a person."),
          sfx=[fx("zzz...", 0.78, 0.2, 90, 6)]),
    panel("p04", f"{PAATI}, sitting on a low wooden stool in the dark next to a tea stall, sipping from a small steel "
          "cup, calm, one eye open, moonlight, mysterious, night", S, ref=PAATI_REF, ref_scale=0.5,
          bubbles=[b("Five... no. Six of them.", *RIGHT, 0.3, [0.58, 0.3], "thought")]),
    panel("p05", f"{LIEUT}, whispering, gesturing to men behind him, night, dark street, menacing, upper body", S,
          ref=LIEUT_REF, ref_scale=0.45,
          bubbles=[b("Grab the boy and the recipe. Quietly.", *LEFT, 0.34, [0.42, 0.28], size=24)]),
    panel("p06", "a huge man in red armor slowly lifting the metal shutter of a small tea stall at night, close-up of "
          "his hands on the shutter, creaking, suspense", L, sfx=[fx("kreeeeak...", 0.74, 0.2, 90, 6)]),
    panel("p07", f"{PAATI}, standing in the open doorway of a small tea stall in moonlight, tiny old woman in front of "
          "giant shadows of big men, calm, kind smile, full body, night", P, ref=PAATI_REF, ref_scale=0.45,
          bubbles=[b("Shop's closed, boys. Come back at six.", 0.28, 0.08, 0.4, [0.5, 0.22], size=24)]),
    panel("p08", f"{GOONS}, laughing at someone in front of them, mocking, cracking knuckles, night street, "
          "from below, menacing", L,
          bubbles=[b("Move, Grandma. This doesn't concern you.", *LEFT, 0.34, [0.42, 0.3], size=24)]),
    panel("p09", f"{PAATI}, close-up, drinking the last sip of tea from a small steel cup, eyes closed, calm, steam, "
          "moonlight, face focus", S, ref=PAATI_REF, ref_scale=0.55, sfx=[fx("sip...", 0.78, 0.82, 80, -5)],
          bubbles=[b("Hm. Cardamom.", *RIGHT, 0.26, [0.6, 0.3])]),
    panel("p10", f"{PAATI}, a huge golden aura bursting around her, grey hair glowing gold, eyes glowing gold, wind, "
          "light rays, sari fluttering, power up, dramatic, night street, from below", P, ref=PAATI_REF, ref_scale=0.4,
          sfx=[fx("VWOOM", 0.72, 0.84, 130, -8)]),
    panel("p11", f"{GOONS}, staring in shock, jaws dropped, sweating, sweatdrops, golden light on their faces, comedy, "
          "night", L,
          bubbles=[b("Since when do grandmothers GLOW?!", *LEFT, 0.32, [0.42, 0.3])]),
    panel("p12", f"{PAATI}, spinning a wooden walking stick, knocking three big men in red armor flying through the "
          "air, speed lines, golden glow, comedy action, dynamic angle, night street", L, ref=PAATI_REF,
          ref_scale=0.35, sfx=[fx("THWACK!", 0.2, 0.2, 110, -8), fx("THWACK!", 0.5, 0.12, 110, 6),
                               fx("THWACK!", 0.8, 0.22, 110, -4)]),
    panel("p13", "a big man in red armor stuck head first in a large steel milk can, legs kicking in the air, comedy, "
          "night street, tea stall in the background", S, sfx=[fx("KLANG!", 0.74, 0.18, 120, 8)]),
    panel("p14", f"{ARJUN}, waking up, sitting up on a thin mat, rubbing his eyes, messy hair, sleepy, confused, night, "
          "upper body", S, ref="../ref/arjun_face.jpg", ref_scale=0.55,
          bubbles=[b("Paati...? What's all the noise?", *RIGHT, 0.3, [0.58, 0.3])]),
    panel("p15", f"{PAATI}, sitting on top of a neat pile of six unconscious big men in red armor in the middle of a "
          "street, calmly sipping tea from a small steel cup, comedy, moonlight, wide shot", L, ref=PAATI_REF,
          ref_scale=0.35, bubbles=[b("Nothing, beta. Go back to sleep.", *RIGHT, 0.32, [0.6, 0.32])]),
    panel("p16", f"{ARJUN}, extremely shocked, jaw drop, wide-eyed, pointing, comedy, night, upper body", S,
          ref="../ref/arjun.jpg", ref_scale=0.5,
          bubbles=[b("YOU DRANK THE TEA?!", *LEFT, 0.3, [0.42, 0.3], size=28)]),
    panel("p17", f"{PAATI}, close-up, face focus, kind smile, eyes glowing faint gold, holding a small steel cup, "
          "steam, warm lamp light, mysterious", S, ref=PAATI_REF, ref_scale=0.55,
          bubbles=[b("Who do you think the first glass was for?", *RIGHT, 0.32, [0.58, 0.3])]),
    panel("p18", f"{LIEUT}, trembling, sweating, backing away, holding a phone to his ear, night street, a pile of "
          "unconscious men in red armor behind him, comedy", S, ref=LIEUT_REF, ref_scale=0.4,
          bubbles=[b("Boss... we have a problem. The grandmother.", *LEFT, 0.34, [0.42, 0.28], size=24)]),
    panel("p19", f"{BOSS}, standing at a huge dark office window at night, holding a phone to her ear, looking down at "
          "the glowing city, red light, ominous", P,
          bubbles=[b("...Describe her.", 0.28, 0.08, 0.3, [0.5, 0.22])]),
    panel("p20", f"{LIEUT}, close-up, sweating, sunglasses cracked, phone to his ear, night, face focus", S,
          ref=LIEUT_REF, ref_scale=0.5,
          bubbles=[b("Grey hair. White sari. A walking stick. She hits like an S-Rank.", *LEFT, 0.36, [0.45, 0.28],
                     size=23)]),
    panel("p21", "close-up of a woman's hand with red nails crushing a glass of water, shards flying, red lotus ring, "
          "dark office, red light, dramatic", L, sfx=[fx("KRAK!", 0.76, 0.2, 120, 8, "#ff5a4f")],
          bubbles=[b("Impossible. The Kettle Queen died thirty years ago.", *LEFT, 0.34, [0.42, 0.3], size=24)]),
    panel("p22", f"{VIKTOR}, running down a night street holding a phone on a selfie stick, live streaming, heroic, "
          "a girl in a white robe running behind him, motion lines", L, ref="../ref/viktor.jpg", ref_scale=0.4,
          before=nar("Twenty minutes later..."),
          bubbles=[b("Chat! We're here to save the tea stall! LIVE!", *LEFT, 0.34, [0.42, 0.3], size=24)]),
    panel("p23", f"{VIKTOR}, frozen in place, staring at something, sweatdrop, awkward, holding a phone on a selfie "
          "stick, night street, comedy", S, ref="../ref/viktor.jpg", ref_scale=0.5,
          bubbles=[b("...We're late, aren't we?", *RIGHT, 0.3, [0.58, 0.3])]),
    panel("p24", f"{MEERA}, bowing politely to someone, cheerful smile, night street, lamp light, upper body", S,
          ref="../ref/meera.jpg", ref_scale=0.5,
          bubbles=[b("Good evening! I'm Meera. I drink your grandson's tea every day!", *LEFT, 0.36, [0.45, 0.28],
                     size=23)]),
    panel("p25", f"{PAATI}, sharp stern look, pointing her walking stick at a phone on a selfie stick held by a blonde "
          "man in silver armor, comedy, night street", L, ref=PAATI_REF, ref_scale=0.35,
          bubbles=[b("Turn that thing off, boy.", *LEFT, 0.3, [0.42, 0.3]),
                   b("Yes, ma'am.", 0.8, 0.5, 0.2, [0.7, 0.62], size=22)]),
    panel("p26", f"{ARJUN}, and an old woman with grey hair in a bun and a white sari, sitting side by side on a wooden "
          "bench in front of a small tea stall at dawn, two small steel cups of tea, steam, soft orange sunrise, "
          "quiet, warm, from the side", L,
          before=nar("Dawn."),
          bubbles=[b("Paati. Who ARE you?", *LEFT, 0.28, [0.4, 0.36])]),
    panel("p27", f"{PAATI}, smiling at the sunrise, holding a small steel cup, gentle, peaceful, soft orange light, "
          "upper body", S, ref=PAATI_REF, ref_scale=0.55,
          bubbles=[b("Just a tea seller. Like you.", *RIGHT, 0.3, [0.58, 0.3])]),
    panel("p28", f"{PAATI}, close-up, face focus, serious, wise eyes, dawn light", S, ref=PAATI_REF, ref_scale=0.55,
          bubbles=[b("Listen, beta. The tea doesn't give power. YOU do. Every glass carries a little of your life.",
                     *LEFT, 0.38, [0.45, 0.32], size=22)]),
    panel("p29", f"{ARJUN}, looking down at his own trembling hand, faint golden glow, worried, thoughtful, dawn light, "
          "upper body", S, ref="../ref/arjun_face.jpg", ref_scale=0.6,
          bubbles=[b("A little of my life... in every glass.", *RIGHT, 0.3, [0.58, 0.3], "thought")]),
    panel("p30", f"{PAATI}, holding up two fingers, mischievous smile, wink, dawn, upper body", S, ref=PAATI_REF,
          ref_scale=0.5,
          bubbles=[b("Tomorrow I teach you the second recipe. The one that costs you nothing.", *LEFT, 0.36,
                     [0.45, 0.3], size=22)]),
    panel("p31", "no humans, giant glowing portal at dawn, a giant red eye with a slit pupil inside the portal, the eye "
          "narrowing, red lightning, ominous, city skyline, small tea stall far below", L,
          before=nar("And deep inside the Gate..."), after=nar("...the eye had seen her too."),
          status=[{"title": "[ ??? ]", "x": 0.5, "y": 0.82, "w": 0.7, "lines": ["The Kettle Queen has returned."]}]),
    {"name": "end", "card": "To be continued", "h": 360},
]
json.dump(eps, open("episode.json", "w"), indent=1, ensure_ascii=False)
print(len(eps), "items")
