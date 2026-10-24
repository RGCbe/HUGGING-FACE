"""Mix background music under a voiceover, ducking the music whenever the voice speaks.

    python3 mix.py VOICE MUSIC OUT [--music-gain 0.30] [--lufs -14]

The voice is first brought to -16 LUFS, so --music-gain means the same thing whatever level the voice
was recorded or generated at (with the default, the music sits about 18-20 dB under the voice). The
music gets quieter by itself under speech (sidechain compression keyed on the voice) and comes back
up in the pauses. The result is stereo, loudness-normalised (YouTube plays at about -14 LUFS), and
as long as the voice.
"""
import argparse
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument("voice")
ap.add_argument("music")
ap.add_argument("out")
ap.add_argument("--music-gain", type=float, default=0.30)
ap.add_argument("--lufs", type=float, default=-14)
a = ap.parse_args()

graph = (
    "[0:a]aformat=sample_rates=44100:channel_layouts=stereo,loudnorm=I=-16:TP=-2:LRA=11,"
    "aformat=sample_rates=44100,asplit=2[v][key];"
    f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={a.music_gain}[m];"
    "[m][key]sidechaincompress=threshold=0.02:ratio=6:attack=20:release=450[duck];"
    "[v][duck]amix=inputs=2:duration=first:normalize=0,"
    f"loudnorm=I={a.lufs}:TP=-1.5:LRA=11[out]"
)
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", a.voice, "-i", a.music,
                "-filter_complex", graph, "-map", "[out]", "-ar", "44100", "-c:a", "aac", "-b:a", "192k", a.out],
               check=True)
print("wrote", a.out)
