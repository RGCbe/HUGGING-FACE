"""Teach the singing voice converter (Seed-VC, 44.1 kHz singing model) the owner's own voice, from his real SPEAKING
recordings only: he does not sing (26 Nov 2026: "I dont have that skills that y I training the ai model").

    python3 train_voice.py [--steps 200] [--device cpu]       # writes ~/.cache/music/voice-train/manoj-seedvc-ft.pth

Data: his real recordings in the private dataset Rggroups/super-kural-voice (ref_en.opus, teabreak/natural.opus split
into ~10 s pieces, teabreak/mytake/*.opus), about 75 seconds. No ElevenLabs audio: its terms forbid using output to
build competing models, and his real voice is the truest teacher anyway.

Safety (CLAUDE.md, checked 26 Nov 2026):
- Seed-VC code (GPL-3.0) at the pinned commit, git-checked; the training code (train.py, optimizers.py,
  data/ft_dataset.py) was read: no network or process calls, checkpoints saved with torch.save.
- Every checkpoint is pinned and was statically scanned (tensors and dicts only), and torch.load is forced to
  weights_only=True: the singing model, RMVPE, CAMPPlus, BigVGAN, whisper-small (safetensors), OpenVoice V2's
  converter (MIT, used in training to vary the voice) and Seed-VC's speaker table se_db.pt.
- No token is sent to any public repo (token=False); HF_TOKEN only reads the owner's private voice dataset.
- The trained model is his voice: it stays in ~/.cache and his private Hugging Face repos, never in this repository.
"""
import argparse
import os
import shutil
import subprocess
import sys

HOME = os.path.expanduser("~/.cache/music/voice-train")
SEEDVC = ("https://github.com/Plachtaa/seed-vc.git", "51383efd921027683c89e5348211d93ff12ac2a8")
PINS = {  # repo: (revision, files)
    "Plachta/Seed-VC": ("257283f9f41585055e8f858fba4fd044e5caed6e",
                        ["DiT_seed_v2_uvit_whisper_base_f0_44k_bigvgan_pruned_ft_ema_v2.pth",
                         "config_dit_mel_seed_uvit_whisper_base_f0_44k.yml", "se_db.pt"]),
    "lj1995/VoiceConversionWebUI": ("e6d0c1a17da07c33557852f9dfa2bd44cc75737d", ["rmvpe.pt"]),
    "funasr/campplus": ("e4b6ede7ce16997aff4ae69fbca1f0175e2afede", ["campplus_cn_common.bin"]),
    "nvidia/bigvgan_v2_44khz_128band_512x": ("95a9d1dcb12906c03edd938d77b9333d6ded7dfb",
                                             ["config.json", "bigvgan_generator.pt"]),
    "openai/whisper-small": ("973afd24965f72e36ca33b3055d56a652f456b4d", ["*.json", "*.txt", "model.safetensors"]),
    "myshell-ai/OpenVoiceV2": ("f36e7edfe1684461a8343844af60babc2efbb727",
                               ["converter/checkpoint.pth", "converter/config.json"]),
}
VOICE_REPO = "Rggroups/super-kural-voice"
REAL = ["ref_en.opus", "teabreak/natural.opus", "teabreak/mytake/acoustic-kitty.opus",
        "teabreak/mytake/anglo-zanzibar-war.opus", "teabreak/mytake/great-moon-hoax.opus",
        "teabreak/mytake/mike-the-headless-chicken.opus"]


def seedvc_code():
    d = os.path.join(HOME, f"seed-vc-{SEEDVC[1][:8]}")
    if not os.path.exists(os.path.join(d, "train.py")):
        os.makedirs(d, exist_ok=True)
        g = ["git", "-C", d]
        subprocess.run(g + ["init", "-q"], check=True)
        subprocess.run(g + ["fetch", "-q", "--depth", "1", SEEDVC[0], SEEDVC[1]], check=True)
        subprocess.run(g + ["checkout", "-q", "FETCH_HEAD"], check=True)
    got = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout
    if got.strip() != SEEDVC[1]:
        raise SystemExit("Seed-VC commit mismatch")
    return d


def weights():
    from huggingface_hub import snapshot_download
    out = {}
    for repo, (rev, files) in PINS.items():
        out[repo] = snapshot_download(repo, revision=rev, allow_patterns=files, token=False,
                                      local_dir=os.path.join(HOME, "weights", repo.replace("/", "__")))
    return out


def dataset():
    import numpy as np
    import soundfile as sf
    from huggingface_hub import hf_hub_download
    d = os.path.join(HOME, "data")
    if os.path.isdir(d) and os.listdir(d):
        return d
    os.makedirs(d)
    for f in REAL:
        p = hf_hub_download(VOICE_REPO, f, repo_type="dataset", token=os.environ["HF_TOKEN"])
        raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", "44100",
                              "-"], check=True, capture_output=True).stdout
        a = np.frombuffer(raw, np.float32)
        piece = 44100 * 10
        name = os.path.splitext(os.path.basename(f))[0]
        for k, i in enumerate(range(0, len(a), piece)):
            seg = a[i:i + piece]
            if len(seg) >= 44100 * 2:
                sf.write(os.path.join(d, f"{name}_{k}.wav"), seg, 44100)
    print(f"training data: {len(os.listdir(d))} files of the owner's real voice")
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=200)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--batch-size", type=int, default=2)
    a = ap.parse_args()
    import torch
    import yaml
    _load = torch.load

    def safe_load(*args, **kw):
        kw["weights_only"] = True
        return _load(*args, **kw)
    torch.load = safe_load
    torch.set_num_threads(os.cpu_count() or 4)

    code, w, data = seedvc_code(), weights(), dataset()
    sv = w["Plachta/Seed-VC"]
    cfg = yaml.safe_load(open(os.path.join(sv, "config_dit_mel_seed_uvit_whisper_base_f0_44k.yml")))
    cfg["log_dir"] = os.path.join(HOME, "runs")
    cfg["model_params"]["vocoder"]["name"] = w["nvidia/bigvgan_v2_44khz_128band_512x"]
    cfg["model_params"]["speech_tokenizer"]["name"] = w["openai/whisper-small"]
    cfg_path = os.path.join(HOME, "config_ft.yml")
    yaml.safe_dump(cfg, open(cfg_path, "w"))

    sys.path.insert(0, code)
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "space"))  # the dac stub (space/dac)
    os.chdir(code)
    import hf_utils
    local = {("Plachta/Seed-VC", "se_db.pt"): os.path.join(sv, "se_db.pt"),
             ("funasr/campplus", "campplus_cn_common.bin"): os.path.join(w["funasr/campplus"], "campplus_cn_common.bin"),
             ("lj1995/VoiceConversionWebUI", "rmvpe.pt"): os.path.join(w["lj1995/VoiceConversionWebUI"], "rmvpe.pt")}
    ov = w["myshell-ai/OpenVoiceV2"]

    def pinned(repo, model_filename="pytorch_model.bin", config_filename=None):
        if repo == "myshell-ai/OpenVoiceV2":
            return os.path.join(ov, "converter/checkpoint.pth"), os.path.join(ov, "converter/config.json")
        return local[(repo, model_filename)]  # anything not pinned fails loudly instead of downloading
    hf_utils.load_custom_model_from_hf = pinned
    import train
    train.load_custom_model_from_hf = pinned
    run = "manoj"
    shutil.rmtree(os.path.join(HOME, "runs", run), ignore_errors=True)
    t = train.Trainer(config_path=cfg_path,
                      pretrained_ckpt_path=os.path.join(sv, "DiT_seed_v2_uvit_whisper_base_f0_44k_bigvgan_pruned_ft_ema_v2.pth"),
                      data_dir=data, run_name=run, batch_size=a.batch_size, steps=a.steps,
                      save_interval=max(50, a.steps // 2), max_epochs=100000, device=a.device)
    t.train()
    out = os.path.join(HOME, "manoj-seedvc-ft.pth")
    shutil.copy(os.path.join(HOME, "runs", run, "ft_model.pth"), out)
    print(f"the owner's voice model: {out}")


if __name__ == "__main__":
    main()
