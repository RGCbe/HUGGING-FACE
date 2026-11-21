"""The owner's voice made clear on phone speakers, shared by every video builder (mix.py, lore_video.py).

Measured on 21 Nov 2026 against a Tamil Marvel Shorts channel whose audio the owner's friend found clearer
(Tharamana Talks): our ElevenLabs voice had 62-70% of its energy at 150-500 Hz (boom that a phone speaker cannot
play) and only 17-20% at 500-2,000 Hz, where speech is understood; theirs had 49% there and almost no bass. It also
paused a third of the time. The owner heard the result of the settings below ("B") and chose it: "B ok".

  VOICE_CLEAR       ffmpeg filters: bass below 170 Hz off, the 150-350 Hz boom down 9 dB, the 1.2 kHz speech range up
                    7 dB, a little 2.8 kHz bite, and a gentle compressor so every word is equally loud
  shorten_pauses()  pauses inside a voice piece longer than 0.32 s become 0.22 s (only where the timing is not tied
                    to pictures cued by the words: lore_video.py, not a doodle video whose boards follow the voice)
"""
import numpy as np

VOICE_CLEAR = ("highpass=f=170,lowshelf=f=350:g=-9,equalizer=f=1200:t=q:w=1.2:g=7,equalizer=f=2800:t=q:w=1.2:g=2,"
               "acompressor=threshold=-22dB:ratio=3:attack=5:release=90:makeup=6")


def shorten_pauses(a, sr, keep=0.22, longer=0.32):
    """a (mono float array) with every quiet stretch longer than `longer` seconds cut to `keep` seconds; the
    silence at the very start and end is left alone."""
    w = int(0.01 * sr)
    if len(a) < 3 * w:
        return a
    lv = np.array([np.sqrt(np.mean(a[i:i + w] ** 2)) for i in range(0, len(a) - w + 1, w)])
    quiet = lv < max(lv.max() * 0.03, 0.002)
    out, i, n = [], 0, len(quiet)
    while i < n:
        j = i
        while j < n and quiet[j] == quiet[i]:
            j += 1
        piece = a[i * w: j * w if j < n else len(a)]
        if quiet[i] and 0 < i and j < n and (j - i) * 0.01 > longer:
            piece = piece[: int(keep * sr)]
        out.append(piece)
        i = j
    return np.concatenate(out)
