"""Make a song in the owner's own voice: takes on our private music Space, the lead re-voiced, mixed and checked.

    python3 song.py SONG.json takes          # the takes (one per seed) from the Space's /song
    python3 song.py SONG.json stems          # split each take into vocals and the rest (HDemucs, on this machine)
    python3 song.py SONG.json check          # how clearly each take sings the lyrics (faster-whisper), ranked
    python3 song.py SONG.json voice [N]      # the best N takes (default 2): vocals re-voiced with the owner's voice
    python3 song.py SONG.json spoken         # the spoken intro and outro in the owner's ElevenLabs voice
    python3 song.py SONG.json mix            # the finals: re-voiced vocal + band + spoken parts, mastered
    python3 song.py SONG.json save           # everything to the private dataset Rggroups/music-work/SLUG/

Work files stay in ~/.cache/music/SLUG/ (never in this public repo: they hold the owner's voice).

Where data goes (CLAUDE.md):
- Lyrics, style and the owner's reference voice go only to the owner's own private Space Rggroups/music, with HF_TOKEN.
- The spoken parts' text goes only to ElevenLabs' own API, with its key.
- The finals go only to the owner's private dataset (refused if it is not private).
- The separation model (torchaudio's HDemucs, trained on MUSDB-HQ + extra) loads in PyTorch's safe weights-only mode.
- Gradio's client analytics are turned off.
"""
import difflib
import json
import os
import re
import subprocess
import sys

import numpy as np
import soundfile as sf

os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
HERE = os.path.dirname(os.path.abspath(__file__))
SPACE = "Rggroups/music"
DATASET = "Rggroups/music-work"
VOICE_REPO = "Rggroups/super-kural-voice"
REFERENCE = "teabreak/natural.opus"  # the owner talking naturally, ~30 s of his real voice (not ElevenLabs)
SR = 44100


def work(song):
    d = os.path.expanduser(os.path.join("~/.cache/music", song["slug"]))
    os.makedirs(d, exist_ok=True)
    return d


def client():
    from gradio_client import Client
    return Client(SPACE, token=os.environ["HF_TOKEN"], analytics_enabled=False, verbose=False)


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *args], check=True)


def load(path, sr=SR, mono=False):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1" if mono else "2",
                          "-ar", str(sr), "-"], check=True, capture_output=True).stdout
    a = np.frombuffer(raw, np.float32)
    return a if mono else a.reshape(-1, 2)


def takes(song):
    d, c = work(song), None
    for seed in song["seeds"]:
        out = os.path.join(d, f"take_{seed}.flac")
        if os.path.exists(out):
            continue
        c = c or client()
        print(f"take {seed}: composing ...", flush=True)
        path, info = c.predict(song["caption"], song["lyrics"], song["duration"], seed, song.get("bpm", 0),
                               song.get("keyscale", ""), song["language"], song.get("lm_temperature", 0.85),
                               api_name="/song")
        ffmpeg("-i", path, out)
        with open(os.path.join(d, f"take_{seed}.json"), "w") as f:
            f.write(info)
        i = json.loads(info)
        print(f"take {seed}: {i.get('duration')} s, {i.get('bpm')} BPM, {i.get('keyscale')}, made in {i['seconds']} s")


def stems(song):
    import torch
    import torchaudio
    from torchaudio.pipelines import HDEMUCS_HIGH_MUSDB_PLUS as bundle
    d = work(song)
    model = None
    for seed in song["seeds"]:
        src = os.path.join(d, f"take_{seed}.flac")
        voc, band = os.path.join(d, f"take_{seed}.vocals.wav"), os.path.join(d, f"take_{seed}.band.wav")
        if not os.path.exists(src) or os.path.exists(voc):
            continue
        if model is None:
            torch.set_num_threads(os.cpu_count() or 4)
            model = bundle.get_model()  # torch.load with PyTorch's default weights_only=True
        x = torch.from_numpy(load(src).T.copy())
        ref = x.mean(0)
        x = (x - ref.mean()) / (ref.std() + 1e-8)
        seg, ov = SR * 10, SR
        out = torch.zeros(4, 2, x.shape[1])
        weight = torch.zeros(x.shape[1])
        fade = torch.ones(seg)
        fade[:ov] = torch.linspace(0, 1, ov)
        fade[-ov:] = torch.linspace(1, 0, ov)
        with torch.no_grad():
            for start in range(0, x.shape[1], seg - ov):
                chunk = x[:, start:start + seg]
                n = chunk.shape[1]
                y = model(torch.nn.functional.pad(chunk, (0, seg - n))[None])[0][:, :, :n]
                w = fade[:n].clone()
                if start == 0:
                    w[:min(ov, n)] = 1
                out[:, :, start:start + n] += y * w
                weight[start:start + n] += w
                if start + seg >= x.shape[1]:
                    break
        out = out / weight.clamp(min=1e-6) * (ref.std() + 1e-8) + ref.mean()
        v = out[list(model.sources).index("vocals")]
        rest = out.sum(0) - v
        sf.write(voc, v.T.numpy(), SR)
        sf.write(band, rest.T.numpy(), SR)
        print(f"take {seed}: split")


def norm_text(s):
    s = re.sub(r"\[[^\]]*\]", " ", s)
    s = re.sub(r"[()!?,.…:;'\"-]", " ", s)
    return re.sub(r"\s+", "", s)


def check(song):
    from faster_whisper import WhisperModel
    d = work(song)
    model = WhisperModel(song.get("check_model", "medium"), device="cpu", compute_type="int8")
    want = norm_text(song["lyrics"])
    rows = []
    for seed in song["seeds"]:
        voc = os.path.join(d, f"take_{seed}.vocals.wav")
        if not os.path.exists(voc):
            continue
        cache = os.path.join(d, f"take_{seed}.heard.txt")
        if not os.path.exists(cache):
            segs, _ = model.transcribe(load(voc, 16000, mono=True), language=song["language"], beam_size=5,
                                       vad_filter=True, condition_on_previous_text=False)
            with open(cache, "w") as f:
                f.write("\n".join(f"{s.start:.1f}\t{s.end:.1f}\t{s.text.strip()}" for s in segs))
        heard = open(cache).read()
        got = norm_text(" ".join(l.split("\t")[-1] for l in heard.splitlines()))
        sm = difflib.SequenceMatcher(None, want, got, autojunk=False)
        matched = sum(b.size for b in sm.get_matching_blocks())
        full = load(os.path.join(d, f"take_{seed}.flac"))
        peak = float(np.abs(full).max())
        info = json.load(open(os.path.join(d, f"take_{seed}.json")))
        rows.append({"seed": seed, "lyrics_heard": round(matched / max(1, len(want)), 3), "peak": round(peak, 3),
                     "seconds": round(len(full) / SR, 1), "bpm": info.get("bpm"), "key": info.get("keyscale")})
    rows.sort(key=lambda r: -r["lyrics_heard"])
    with open(os.path.join(d, "check.json"), "w") as f:
        json.dump(rows, f, indent=1, ensure_ascii=False)
    for r in rows:
        print(r)
    return rows


def reference(song):
    from huggingface_hub import hf_hub_download
    d = work(song)
    ref = os.path.join(d, "reference.wav")
    if not os.path.exists(ref):
        p = hf_hub_download(VOICE_REPO, REFERENCE, repo_type="dataset", token=os.environ["HF_TOKEN"])
        a = load(p, SR, mono=True)
        # the clearest 15 s: Seed-VC gives each chunk 30 s minus the reference, so a shorter reference = longer chunks
        win, hop = SR * 15, SR // 2
        rms = [float(np.sqrt(np.mean(a[i:i + win] ** 2))) for i in range(0, max(1, len(a) - win), hop)]
        loud = [float(np.mean(np.abs(a[i:i + win]) < 0.01)) for i in range(0, max(1, len(a) - win), hop)]
        best = int(np.argmax([r * (1 - q) for r, q in zip(rms, loud)])) * hop
        sf.write(ref, a[best:best + win], SR)
    return ref


def voice(song, n=2):
    from gradio_client import handle_file
    d = work(song)
    rows = json.load(open(os.path.join(d, "check.json")))[:n]
    ref, c = reference(song), None
    for r in rows:
        seed = r["seed"]
        out = os.path.join(d, f"take_{seed}.vocals.manoj.wav")
        if os.path.exists(out):
            continue
        c = c or client()
        print(f"take {seed}: re-voicing ...", flush=True)
        path = c.predict(handle_file(os.path.join(d, f"take_{seed}.vocals.wav")), handle_file(ref),
                         song.get("vc_steps", 30), song.get("vc_cfg", 0.7), song.get("vc_semitones", 0),
                         api_name="/voice")
        ffmpeg("-i", path, "-ar", str(SR), "-ac", "1", out)
        print(f"take {seed}: re-voiced")


def spoken(song):
    sys.path.insert(0, os.path.join(HERE, "..", "manga"))
    import voices
    cfg = json.load(open(os.path.join(HERE, "..", "teabreak", "config.json")))["eleven"]
    key = os.environ["ELEVENLABS_API_KEY"]
    vid = voices.voices(key)[cfg["voice"]]
    d = work(song)
    for part in ("intro", "outro"):
        out = os.path.join(d, f"spoken_{part}.wav")
        if os.path.exists(out):
            continue
        pcm = voices.speak(key, vid, song[f"spoken_{part}"], cfg, seed=song.get("spoken_seed", 7))
        raw = os.path.join(d, f"spoken_{part}.raw.wav")
        voices.write(raw, pcm)
        ffmpeg("-i", raw, "-ar", str(SR), "-ac", "1", out)
        os.remove(raw)
        print(f"spoken {part}: {sf.info(out).duration:.1f} s")


def first_voice(v, thr=0.06):
    """Seconds until the vocal stem first stays loud for half a second (the singing starts)."""
    e = np.sqrt(np.convolve(v ** 2, np.ones(SR // 10) / (SR // 10), mode="same"))
    loud = e > thr * e.max()
    run = SR // 2
    for i in range(0, len(loud) - run, SR // 20):
        if loud[i:i + run].mean() > 0.8:
            return i / SR
    return 0.0


def mix(song):
    d = work(song)
    rows = json.load(open(os.path.join(d, "check.json")))
    intro, outro = (load(os.path.join(d, f"spoken_{p}.wav"), mono=True) for p in ("intro", "outro"))
    for r in rows:
        seed = r["seed"]
        conv = os.path.join(d, f"take_{seed}.vocals.manoj.wav")
        if not os.path.exists(conv):
            continue
        band = load(os.path.join(d, f"take_{seed}.band.wav"))
        orig = load(os.path.join(d, f"take_{seed}.vocals.wav"))
        new = load(conv, mono=True)
        n = min(len(band), len(orig), len(new))
        band, orig, new = band[:n], orig[:n], new[:n]
        # the owner's voice leads; the generated vocal stays underneath, quiet, so the gang chorus and the crowd
        # keep their size (Seed-VC turns a crowd into one voice)
        level = np.sqrt(np.mean(orig.mean(1) ** 2)) / max(1e-6, np.sqrt(np.mean(new ** 2)))  # as loud as the original
        lead = (new * level * song.get("lead_gain", 1.0))[:, None] * np.ones(2, np.float32)
        body = band + lead + orig * song.get("orig_under", 0.25)
        # the spoken intro over the instrumental opening, before the first sung line; the music dips under it
        start = first_voice(orig.mean(1))
        pre = max(0.0, len(intro) / SR + 0.8 - start)  # seconds of opening to add if the intro is longer
        if pre > 0:
            loop = body[: int(SR * max(1.0, min(start, 4.0)))]
            reps = int(np.ceil(pre * SR / len(loop)))
            body = np.concatenate([np.tile(loop, (reps, 1))[: int(pre * SR)], body])
        duck = np.ones(len(body))
        il = len(intro) + SR // 2
        duck[:il] = 0.45
        duck[il:il + SR] = np.linspace(0.45, 1, min(SR, len(duck) - il))
        body = body * duck[:, None]
        body[SR // 4: SR // 4 + len(intro)] += intro[:, None] * 0.9
        # the spoken outro after the music ends, over its tail
        tail = SR * 2
        total = np.zeros((len(body) + len(outro) + tail, 2), np.float32)
        total[: len(body)] = body
        at = len(body) - SR // 2
        total[at: at + len(outro)] += outro[:, None] * 0.9
        pre_master = os.path.join(d, f"final_{seed}.premaster.wav")
        sf.write(pre_master, total, SR)
        out = os.path.join(d, f"final_{seed}.wav")
        ffmpeg("-i", pre_master, "-af", "loudnorm=I=-14:TP=-1.0:LRA=11", "-ar", str(SR), out)
        os.remove(pre_master)
        ffmpeg("-i", out, "-c:a", "libmp3lame", "-b:a", "320k", os.path.join(d, f"final_{seed}.mp3"))
        a = load(out)
        print(f"final {seed}: {len(a) / SR:.1f} s, peak {np.abs(a).max():.3f}, intro starts the singing at "
              f"{start + pre:.1f} s")


def save(song):
    from huggingface_hub import HfApi
    api = HfApi(token=os.environ["HF_TOKEN"])
    if api.repo_exists(DATASET, repo_type="dataset"):
        if not api.dataset_info(DATASET).private:
            raise SystemExit(f"{DATASET} is not private: refusing to upload")
    else:
        api.create_repo(DATASET, repo_type="dataset", private=True)
    d = work(song)
    with open(os.path.join(d, "song.json"), "w") as f:
        json.dump(song, f, indent=1, ensure_ascii=False)
    api.upload_folder(repo_id=DATASET, repo_type="dataset", folder_path=d, path_in_repo=song["slug"],
                      allow_patterns=["*.flac", "*.wav", "*.mp3", "*.json", "*.txt"],
                      commit_message=f"{song['slug']}: takes, stems, re-voiced vocals and finals")
    print(f"saved to {DATASET}/{song['slug']}")


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    song = json.load(open(sys.argv[1]))
    step = sys.argv[2]
    if step == "voice":
        voice(song, int(sys.argv[3]) if len(sys.argv) > 3 else 2)
    elif step in ("takes", "stems", "check", "spoken", "mix", "save"):
        globals()[step](song)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
