"""Builds f-rank/ep05/episode.json: Episode 5, "The Second Recipe"."""
import json

ARJUN = ("1boy, male focus, solo, young man, dark-skinned male, dark skin, brown skin, short black hair, messy hair, "
         "brown eyes, white kurta, red sash, red string bracelet")
VIKTOR = "1boy, male focus, solo, adult, tall, blonde hair, short hair, slicked back hair, blue eyes, silver armor, black cape"
MEERA = ("1girl, solo, young woman, dark-skinned female, brown skin, long black hair, single braid over shoulder, "
         "brown eyes, white robe, gold trim, holding staff with crystal, healer")
PAATI = ("1girl, solo, elderly woman, old woman, grandmother, about 70 years old, wrinkled face, deep wrinkles, "
         "grey hair in a bun, white cotton sari covering her body down to her feet, wooden walking stick")
LIEUT = ("1boy, solo, adult man in a black suit and black sunglasses, slicked back black hair, red lotus pin on his "
         "chest, black tie")
GOONS = "several big men in red armor with red lotus symbols on their chests"
BOSS = "1girl, solo, woman seen from behind, long black hair in a low bun, red blazer, red lotus earrings"

L, P, S = (1216, 832), (832, 1216), (1024, 1024)
PAATI_REF = "../ep03/out/img/p29.png"
LIEUT_REF = "../ep03/out/img/p12.png"


def panel(name, prompt, size, before=None, after=None, bubbles=None, sfx=None, status=None, ref=None, ref_scale=None,
          gap=None, seed=7):
    p = {"name": name, "prompt": prompt, "seed": seed, "w": size[0], "h": size[1]}
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
YOUNG_QUEEN = ("old faded sepia photograph, a young woman in a white sari holding a steel tea kettle, smiling, standing "
               "next to a little girl with long black hair and a red ribbon holding a small steel cup, worn photo edges")
eps = [
    panel("p01", "scenery, morning, a small tea stall with its metal shutter pulled down, a long line of hunters in "
          "armor waiting in the street in front of it, a giant glowing blue portal in the distance, soft morning light",
          L, before=nar("The next morning."), after=nar("For the first time, the tea stall did not open.")),
    panel("p02", "several hunters in armor standing in a line in a street, disappointed, comedy, one big man holding an "
          "empty small steel cup, sweatdrops, morning, upper body", L,
          bubbles=[b("CLOSED?!", *LEFT, 0.2, [0.36, 0.34], size=30),
                   b("But I have a dungeon at nine!", *RIGHT, 0.3, [0.66, 0.36], size=24)]),
    panel("p03", f"{ARJUN}, and an old woman with grey hair in a bun and a white sari, crouching side by side at a "
          "small clay stove in a tiny courtyard behind a tea stall, two small steel pots side by side on the fire, "
          "steam, morning light, from the side", L, before=nar("Behind the stall..."),
          bubbles=[b("Two pots, beta. Two recipes.", *RIGHT, 0.3, [0.64, 0.38])]),
    panel("p04", f"{PAATI}, close-up, face focus, serious, holding up one finger, steam, morning light", S,
          ref=PAATI_REF, ref_scale=0.55,
          bubbles=[b("The first recipe pours YOUR life into the glass. Strong. But it empties you.", *LEFT, 0.38,
                     [0.45, 0.32], size=22)]),
    panel("p05", f"{ARJUN}, curious, leaning forward, eager, morning light, upper body", S,
          ref="../ref/arjun_face.jpg", ref_scale=0.55,
          bubbles=[b("And the second one?", *RIGHT, 0.28, [0.58, 0.3])]),
    panel("p06", f"{PAATI}, holding up a single small green cardamom pod between two fingers, gentle smile, soft "
          "morning light, upper body", S, ref=PAATI_REF, ref_scale=0.5,
          bubbles=[b("The second one gives nothing. It wakes up the fire that's already inside them.", *LEFT, 0.38,
                     [0.45, 0.3], size=22)]),
    panel("p07", f"{ARJUN}, thoughtful, hand on his chin, looking at a steaming steel pot, morning, upper body", S,
          ref="../ref/arjun_face.jpg", ref_scale=0.55,
          bubbles=[b("...Inside them?", *RIGHT, 0.26, [0.58, 0.3], "thought")]),
    panel("p08", f"{ARJUN}, panicking, a steel pot on a small clay stove boiling over wildly, white foam spilling "
          "everywhere, comedy, motion lines, morning", L, ref="../ref/arjun.jpg", ref_scale=0.4,
          before=nar("Attempt one."), sfx=[fx("BLUB BLUB BLUB", 0.74, 0.16, 84, 6)]),
    panel("p09", f"{VIKTOR}, sitting on a small wooden stool, holding a small steel cup, hiccupping, cheeks puffed, "
          "comedy, sweatdrop, a tray of empty steel cups beside him, morning", S, ref="../ref/viktor.jpg",
          ref_scale=0.5, before=nar("Attempt six. Volunteer: Viktor Hale."),
          sfx=[fx("HIC!", 0.82, 0.78, 100, 8)],
          bubbles=[b("Why... do I smell... flowers?", *LEFT, 0.3, [0.42, 0.32])]),
    panel("p10", f"{VIKTOR}, his blonde hair standing straight up, crackling sparks of static electricity around his "
          "head, shocked face, comedy, morning, upper body", S, ref="../ref/viktor.jpg", ref_scale=0.45,
          before=nar("Attempt nineteen."), sfx=[fx("bzzt", 0.82, 0.8, 90, -6)]),
    panel("p11", f"{MEERA}, laughing, covering her mouth with one hand, holding her staff, morning light, upper body",
          S, ref="../ref/meera.jpg", ref_scale=0.5,
          bubbles=[b("Should I heal that... or film it?", *RIGHT, 0.3, [0.58, 0.3])]),
    panel("p12", f"{ARJUN}, sitting on the ground, head in his hands, frustrated, tired, a steel pot beside him, "
          "morning", S, ref="../ref/arjun_face.jpg", ref_scale=0.5,
          bubbles=[b("I can't do it, Paati. The first recipe was easy!", *LEFT, 0.34, [0.42, 0.3], size=24)]),
    panel("p13", f"{PAATI}, sitting on a low wooden stool, kind smile, warm morning light, upper body", S,
          ref=PAATI_REF, ref_scale=0.5,
          bubbles=[b("The first was easy because it was about you. This one is about them.", *RIGHT, 0.36,
                     [0.56, 0.3], size=22)]),
    panel("p14", f"{PAATI}, close-up, face focus, wise, tapping her ear with one finger, soft light", S, ref=PAATI_REF,
          ref_scale=0.55,
          bubbles=[b("Don't push into the pot, beta. Listen to who you're making it for.", *LEFT, 0.36, [0.45, 0.3],
                     size=22)]),
    panel("p15", f"{ARJUN}, eyes closed, calm, gently stirring a steel pot, soft steam swirling, faint warm glow, "
          "quiet, peaceful, upper body", L, ref="../ref/arjun_face.jpg", ref_scale=0.45,
          before=nar("Attempt twenty."),
          bubbles=[b("Viktor. Loud. Scared of looking weak. Hasn't slept since the live stream.", *RIGHT, 0.36,
                     [0.62, 0.34], "thought", size=22)]),
    panel("p16", "close-up of hands pouring tea from a steel pot into a small steel cup, a long thin stream of tea, "
          "steam, warm light, gentle", S,
          bubbles=[b("For you, Viktor. Less sugar.", *LEFT, 0.3, [0.4, 0.3])]),
    panel("p17", f"{VIKTOR}, drinking from a small steel cup, a soft blue glow rising from his chest, surprised, eyes "
          "wide, morning light", P, ref="../ref/viktor.jpg", ref_scale=0.45,
          sfx=[fx("fwoosh...", 0.74, 0.86, 90, -6)]),
    panel("p18", f"{VIKTOR}, looking down at his own open hands glowing soft blue, amazed, moved, emotional, upper "
          "body", S, ref="../ref/viktor.jpg", ref_scale=0.5,
          bubbles=[b("This isn't your power...", *LEFT, 0.3, [0.42, 0.3]),
                   b("...It's mine.", 0.78, 0.56, 0.22, [0.68, 0.66], size=26)]),
    panel("p19", f"{MEERA}, gentle smile, looking at someone off to the side, morning light, upper body", S,
          ref="../ref/meera_face.jpg", ref_scale=0.55,
          bubbles=[b("And you, Arjun? How do you feel?", *RIGHT, 0.3, [0.58, 0.3])]),
    panel("p20", f"{ARJUN}, stretching both arms up, energetic, big smile, bright morning light, upper body", S,
          ref="../ref/arjun.jpg", ref_scale=0.5,
          bubbles=[b("...Not tired at all!", *LEFT, 0.28, [0.42, 0.3], size=26)]),
    panel("p21", f"{PAATI}, grinning, thumbs up, wink, playful, morning light, upper body", S, ref=PAATI_REF,
          ref_scale=0.5,
          bubbles=[b("Costs you nothing. That's the second recipe.", *RIGHT, 0.32, [0.58, 0.3])]),
    panel("p22", f"{ARJUN}, lifting the metal shutter of a small tea stall, smiling, a long line of hunters in armor "
          "cheering in front of the stall, bright noon sunlight, wide shot", L, ref="../ref/arjun.jpg", ref_scale=0.35,
          before=nar("Noon."),
          bubbles=[b("Sorry for the wait! New recipe today!", *LEFT, 0.34, [0.4, 0.34], size=24)]),
    panel("p23", "a big bearded hunter in heavy armor holding a small steel cup of tea, suspicious squint, comedy, "
          "noon, upper body", S,
          bubbles=[b("Same price?", *LEFT, 0.22, [0.38, 0.3]),
                   b("Ten rupees a glass.", 0.76, 0.6, 0.28, [0.96, 0.72], size=24)]),
    panel("p24", "many hunters in armor drinking tea from small steel cups in a busy street, each person glowing a "
          "different colour, red glow, blue glow, green glow, purple glow, white glow, joyful, laughing, wide shot, "
          "noon", L, after=nar("Every glass glowed a different colour. Their own.")),
    panel("p25", "scenery, night, a very tall dark glass skyscraper towering over a glowing city, red lights at its "
          "top, ominous, low angle", P, before=nar("That night. Red Lotus Tower.")),
    panel("p26", f"{BOSS}, sitting at a dark desk, opening a small old wooden box, dark office, red light, "
          "mysterious", L),
    panel("p27", f"{YOUNG_QUEEN}, held between two fingers with red nails, red lotus ring, dark office, red light", S,
          before=nar("An old photograph.")),
    panel("p28", "close-up of a woman's mouth with red lipstick, a cold small smile, the rest of her face in deep "
          "shadow, red lotus earring, dark, red light, dramatic", L,
          bubbles=[b("Hello again...", *LEFT, 0.26, [0.4, 0.4]),
                   b("...Teacher.", 0.78, 0.6, 0.22, [0.62, 0.62], size=28)]),
    panel("p29", "no humans, giant glowing portal at night, a giant red eye with a slit pupil inside the portal, wide "
          "open, cracks spreading through the air around the portal like broken glass, red lightning, ominous, city "
          "skyline, small tea stall far below", L,
          before=nar("And deep inside the Gate..."), after=nar("...the eye had stopped watching. It was counting."),
          sfx=[fx("KRRRK", 0.8, 0.14, 110, 8, "#ff5a4f")],
          status=[{"title": "[ WARNING ]", "x": 0.5, "y": 0.82, "w": 0.7, "lines": ["Gate Break in 7 days."]}]),
    {"name": "end", "card": "To be continued", "h": 360},
]
json.dump(eps, open("episode.json", "w"), indent=1, ensure_ascii=False)
print(len(eps), "items")
