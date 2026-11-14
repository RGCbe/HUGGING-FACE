"""Mix background music under a voiceover, ducking the music whenever the voice speaks.

    python3 mix.py VOICE MUSIC OUT [--music-gain 0.30] [--lufs -14] [--events EVENTS.json] [--sfx-gain 0.5]
                   [--stings STINGS.wav] [--sting-gain 0.35] [--plain-voice]

The voice is first cleaned up for phone speakers (VOICE_POLISH: a gentle noise reduction, less boom,
more of the 3-5 kHz clarity the cloned voice lacks, compression so it sounds louder and closer, and a
soft gate so the room hiss in the pauses drops away; --plain-voice skips it), then brought to -16
LUFS, so --music-gain means the same thing whatever level the voice was recorded or generated at
(with the default, the music sits about 18-20 dB under the voice). The music gets quieter by itself
under speech (sidechain compression keyed on the voice) and comes back up in the pauses. The result
is stereo, loudness-normalised (YouTube plays at about -14 LUFS), and as long as the voice.

--events takes render.mjs --events output: the sound effects (pops, stamps, whooshes, dings; see
sfx.py) are added at --sfx-gain, and at each punchline the music stops from a moment before it
until just after, so the joke lands in silence. --stings takes score.py's musical hits, which are
added at --sting-gain after the ducking and the punchline pauses, so nothing cuts them.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sfx  # noqa: E402

PUNCH_BEFORE, PUNCH_AFTER, RAMP = 0.9, 0.5, 0.12  # seconds of silence around a punchline, and the fade
VOICE_POLISH = ("afftdn=nr=10:nf=-50:tn=1,highpass=f=90,lowshelf=f=180:g=-4,equalizer=f=3000:t=q:w=1.2:g=8,"
                "highshelf=f=5000:g=4,acompressor=threshold=-24dB:ratio=4:attack=4:release=60:makeup=3,"
                "agate=threshold=0.02:ratio=3:attack=5:release=150:range=0.1")  # owner's pick, 30 Oct 2026

ap = argparse.ArgumentParser()
ap.add_argument("voice")
ap.add_argument("music")
ap.add_argument("out")
ap.add_argument("--music-gain", type=float, default=0.30)
ap.add_argument("--lufs", type=float, default=-14)
ap.add_argument("--events")
ap.add_argument("--sfx-gain", type=float, default=0.5)
ap.add_argument("--stings")
ap.add_argument("--sting-gain", type=float, default=0.35)
ap.add_argument("--plain-voice", action="store_true")
a = ap.parse_args()

events = json.load(open(a.events)) if a.events else []
punches = [e["t"] for e in events if e["kind"] == "punch"]
music = f"volume={a.music_gain}"
if punches:
    # 1 - (how far into a pause t is), each pause ramping down and back up over RAMP seconds
    gaps = [f"min((t-{p - PUNCH_BEFORE:.3f})/{RAMP},({p + PUNCH_AFTER:.3f}-t)/{RAMP})" for p in punches]
    deepest = gaps[0]
    for g in gaps[1:]:
        deepest = f"max({deepest},{g})"
    music += f",volume='1-clip({deepest},0,1)':eval=frame"

inputs = ["-i", a.voice, "-i", a.music]
graph = (
    "[0:a]aformat=sample_rates=44100:channel_layouts=stereo," + ("" if a.plain_voice else VOICE_POLISH + ",") +
    "loudnorm=I=-16:TP=-2:LRA=11,"
    "aformat=sample_rates=44100,asplit=2[v][key];"
    f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,{music}[m];"
    "[m][key]sidechaincompress=threshold=0.02:ratio=6:attack=20:release=450[duck];"
)
with tempfile.TemporaryDirectory() as tmp:
    layers = ["[v]", "[duck]"]
    if any(e["kind"] in sfx.SOUNDS for e in events):
        seconds = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                        a.voice], check=True, capture_output=True, text=True).stdout)
        effects = os.path.join(tmp, "sfx.wav")
        sfx.write(effects, sfx.track(events, seconds))
        inputs += ["-i", effects]
        graph += f"[{len(inputs) // 2 - 1}:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={a.sfx_gain}[fx];"
        layers.append("[fx]")
    if a.stings:
        inputs += ["-i", a.stings]
        graph += f"[{len(inputs) // 2 - 1}:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={a.sting_gain}[st];"
        layers.append("[st]")
    graph += f"{''.join(layers)}amix=inputs={len(layers)}:duration=first:normalize=0,"
    graph += f"loudnorm=I={a.lufs}:TP=-1.5:LRA=11[out]"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *inputs,
                    "-filter_complex", graph, "-map", "[out]", "-ar", "44100", "-c:a", "aac", "-b:a", "192k", a.out],
                   check=True)
print("wrote", a.out)
