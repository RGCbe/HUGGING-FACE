"""The font size at which a line of text fits a width, for ffmpeg drawtext titles (Shorts, TikTok versions).

A 1080-pixel-wide vertical video cut "MIKE THE HEADLESS CHICKEN" at size 118 on both sides: this shrinks the
size until the line fits, so a long title still reads in full. PIL measures the real font; without PIL, a
cautious estimate (Patrick Hand averages about 0.52 of the font size per character).
"""


def font_size(font, text, size, width=1000, smallest=48):
    try:
        from PIL import ImageFont
        w = ImageFont.truetype(font, size).getlength(text)
    except Exception:
        w = len(text) * size * 0.52
    return size if w <= width else max(smallest, int(size * width / w))
