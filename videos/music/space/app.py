"""Music on the owner's own private ZeroGPU Space (Rggroups/music): songs and voice conversion.

Two API endpoints, called from videos/music/song.py with the owner's HF_TOKEN (Gradio's client):

    /song   ACE-Step 1.5: a full song (music + sung vocals) from a style caption and lyrics.
            The XL turbo DiT (4B) composes the audio; the 4B "5Hz" language model plans it first.
    /voice  Seed-VC (singing model, 44.1 kHz, pitch-aware): a sung vocal re-voiced with the timbre of a short
            reference recording, keeping the melody; optionally with a voice model learned by /learn.
    /learn  Seed-VC fine-tuning on one person's voice from short clips (speech is enough), saved by name.
    /repaint ACE-Step sings one part of a song again (a punch-in for a line whose words came out wrong).

Every model is downloaded at a pinned revision and read before use (CLAUDE.md, 25 Nov 2026):
- ACE-Step code (MIT) is the official Space's code at a pinned revision, minus its UI, training and API-server files.
  Its weights are safetensors; its one small pickle (silence_latent.pt) holds only tensors.
  Its custom modeling code (trust_remote_code) is fixed by the pinned revision and was read: torch, transformers
  and einops only, no file, network or process calls.
- Seed-VC code (GPL-3.0) is the GitHub repository at a pinned commit, only its modules/ folder.
  Its checkpoints (.pth/.pt/.bin) were scanned: tensors and dicts only.
- Every torch.load below runs with weights_only=True (forced here), so a checkpoint cannot run code.
- No flash-attention wheels from third-party releases and no `kernels` library (it downloads compiled code at run time).
- No token is sent anywhere: all the models are public, and this Space holds no secrets.
"""
import os
import sys
import json
import time
import tempfile

os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

import spaces  # before torch, for ZeroGPU
import numpy as np
import torch

_torch_load = torch.load


def _safe_load(*args, **kwargs):
    kwargs["weights_only"] = True  # tensors and plain containers only, whatever the caller asked
    return _torch_load(*args, **kwargs)


torch.load = _safe_load

import gradio as gr
import soundfile as sf
from huggingface_hub import snapshot_download

HERE = os.path.dirname(os.path.abspath(__file__))
DEV = os.environ.get("MUSIC_DEVICE", "cuda")  # "cpu" only for a local test of the voice part
SONGS = os.environ.get("MUSIC_SONGS", "1") == "1"  # 0: skip ACE-Step (local test of the voice part)
STORE = os.path.join(HERE, "store")
CK = os.path.join(STORE, "checkpoints")
sys.path.insert(0, os.path.join(HERE, "seedvc"))

# ---- pinned model revisions (read 25 Nov 2026) ----
ACE_UNIFIED = ("ACE-Step/Ace-Step1.5", "19671f406d603126926c1b7e2adc169acbcade22")       # VAE + text encoder
ACE_DIT = ("ACE-Step/acestep-v15-xl-turbo", "d4a0b288b83ebb7e25a8c0b32c573c22e134e8ee")  # 4B DiT, turbo
ACE_LM = ("ACE-Step/acestep-5Hz-lm-4B", "0a3ec94b557aea7d508da38b31cfe7341f6ff737")      # 4B planner LM
SVC = ("Plachta/Seed-VC", "257283f9f41585055e8f858fba4fd044e5caed6e")
SVC_DIT = "DiT_seed_v2_uvit_whisper_base_f0_44k_bigvgan_pruned_ft_ema_v2.pth"
SVC_CFG = "config_dit_mel_seed_uvit_whisper_base_f0_44k.yml"
RMVPE = ("lj1995/VoiceConversionWebUI", "e6d0c1a17da07c33557852f9dfa2bd44cc75737d")
CAMPPLUS = ("funasr/campplus", "e4b6ede7ce16997aff4ae69fbca1f0175e2afede")
BIGVGAN = ("nvidia/bigvgan_v2_44khz_128band_512x", "95a9d1dcb12906c03edd938d77b9333d6ded7dfb")
WHISPER = ("openai/whisper-small", "973afd24965f72e36ca33b3055d56a652f456b4d")
OPENVOICE = ("myshell-ai/OpenVoiceV2", "f36e7edfe1684461a8343844af60babc2efbb727")  # MIT; varies the voice in training


def fetch(repo_rev, local_dir, allow=None):
    repo, rev = repo_rev
    return snapshot_download(repo, revision=rev, local_dir=local_dir, allow_patterns=allow, token=False)


t0 = time.time()
if SONGS:
    fetch(ACE_UNIFIED, CK, ["vae/*", "Qwen3-Embedding-0.6B/*", "acestep-v15-turbo/config.json"])  # folder must exist
    fetch(ACE_DIT, os.path.join(CK, "acestep-v15-xl-turbo"))
    fetch(ACE_LM, os.path.join(CK, "acestep-5Hz-lm-4B"))
SV = os.path.join(STORE, "seedvc")
fetch(SVC, SV, [SVC_DIT, SVC_CFG, "se_db.pt"])
fetch(OPENVOICE, os.path.join(SV, "openvoice"), ["converter/checkpoint.pth", "converter/config.json"])
VOICES = os.path.join(STORE, "voices")  # voice models learned here (/learn), by name
os.makedirs(VOICES, exist_ok=True)
fetch(RMVPE, SV, ["rmvpe.pt"])
fetch(CAMPPLUS, SV, ["campplus_cn_common.bin"])
fetch(BIGVGAN, os.path.join(SV, "bigvgan"), ["config.json", "bigvgan_generator.pt"])
fetch(WHISPER, os.path.join(SV, "whisper-small"), ["*.json", "*.txt", "model.safetensors"])
print(f"models downloaded in {time.time() - t0:.0f} s", flush=True)

# ---- ACE-Step ----
if SONGS:
    from acestep.handler import AceStepHandler
    from acestep.llm_inference import LLMHandler
    from acestep.inference import GenerationParams, GenerationConfig, generate_music

    dit = AceStepHandler(persistent_storage_path=STORE)
    status, ok = dit.initialize_service(project_root=HERE, config_path="acestep-v15-xl-turbo", device="cuda",
                                        use_flash_attention=False, compile_model=False, offload_to_cpu=False,
                                        offload_dit_to_cpu=False)
    print(status, flush=True)
    if not ok:
        raise SystemExit("DiT failed to load")
    lm = LLMHandler(persistent_storage_path=STORE)
    lm_status, lm_ok = lm.initialize(checkpoint_dir=CK, lm_model_path="acestep-5Hz-lm-4B", backend="pt", device="cuda",
                                     offload_to_cpu=False, dtype=dit.dtype)
    print(lm_status, flush=True)
    if not lm_ok:
        raise SystemExit("LM failed to load")

# ---- Seed-VC (singing, f0) ----
import yaml
import librosa
import torchaudio
from modules.commons import build_model, load_checkpoint, recursive_munch
from modules.rmvpe import RMVPE as Rmvpe
from modules.campplus.DTDNN import CAMPPlus
from modules.bigvgan import bigvgan
from modules.audio import mel_spectrogram
from transformers import AutoFeatureExtractor, WhisperModel

cfg = yaml.safe_load(open(os.path.join(SV, SVC_CFG)))
mp = recursive_munch(cfg["model_params"])
mp.dit_type = "DiT"
vc = build_model(mp, stage="DiT")
vc, _, _, _ = load_checkpoint(vc, None, os.path.join(SV, SVC_DIT), load_only_params=True, ignore_modules=[],
                              is_distributed=False)
for k in vc:
    vc[k].eval()
    vc[k].to(DEV)
vc.cfm.estimator.setup_caches(max_batch_size=1, max_seq_length=8192)
f0_model = Rmvpe(os.path.join(SV, "rmvpe.pt"), is_half=False, device=DEV)
campplus = CAMPPlus(feat_dim=80, embedding_size=192)
campplus.load_state_dict(torch.load(os.path.join(SV, "campplus_cn_common.bin"), map_location="cpu"))
campplus.eval().to(DEV)
vocoder = bigvgan.BigVGAN.from_pretrained(os.path.join(SV, "bigvgan"), use_cuda_kernel=False)
vocoder.remove_weight_norm()
vocoder = vocoder.eval().to(DEV)
whisper = WhisperModel.from_pretrained(os.path.join(SV, "whisper-small"),
                                       torch_dtype=torch.float16 if DEV == "cuda" else torch.float32).to(DEV)
del whisper.decoder
whisper_fx = AutoFeatureExtractor.from_pretrained(os.path.join(SV, "whisper-small"))
sp = cfg["preprocess_params"]["spect_params"]
MEL = {"n_fft": sp["n_fft"], "win_size": sp["win_length"], "hop_size": sp["hop_length"], "num_mels": sp["n_mels"],
       "sampling_rate": cfg["preprocess_params"]["sr"], "fmin": sp.get("fmin", 0),
       "fmax": None if sp.get("fmax", "None") == "None" else 8000, "center": False}
print(f"all models ready in {time.time() - t0:.0f} s", flush=True)


# ---- /song ----
def song_seconds(caption, lyrics, duration, seed, bpm, keyscale, language, lm_temperature):
    return int(min(290, 70 + float(duration) * 0.7))


@spaces.GPU(duration=song_seconds)
def song(caption, lyrics, duration, seed, bpm, keyscale, language, lm_temperature):
    """One song. Returns (audio file, settings and the language model's plan as JSON)."""
    seed = int(seed)
    torch.manual_seed(seed)
    np.random.seed(seed % (2 ** 32))
    params = GenerationParams(caption=caption, lyrics=lyrics, duration=float(duration), seed=seed,
                              bpm=int(bpm) if bpm else None, keyscale=keyscale or "", timesignature="4",
                              vocal_language=language or "unknown", inference_steps=8, shift=3.0, thinking=True,
                              lm_temperature=float(lm_temperature))
    config = GenerationConfig(batch_size=1, use_random_seed=False, seeds=[seed], audio_format="flac")
    out = tempfile.mkdtemp()
    t = time.time()
    res = generate_music(dit, lm, params, config, save_dir=out)
    if not res.success:
        raise gr.Error(f"song failed: {res.error}")
    a = res.audios[0]
    path = os.path.join(out, f"song_{seed}.flac")
    sf.write(path, a["tensor"].numpy().T, a["sample_rate"])
    p = a.get("params", {})
    info = {"seed": seed, "seconds": round(time.time() - t, 1), "sample_rate": a["sample_rate"],
            "bpm": p.get("bpm"), "keyscale": p.get("keyscale"), "duration": p.get("duration"),
            "status": res.status_message, "lm": (res.extra_outputs or {}).get("lm_metadata")}
    return path, json.dumps(info, ensure_ascii=False, default=str)


# ---- /repaint: sing one part again ----
def repaint_seconds(src, caption, lyrics, start, end, seed, language, bpm):
    return int(min(200, 45 + max(1.0, float(end) - float(start)) * 1.5))


@spaces.GPU(duration=repaint_seconds)
def repaint(src, caption, lyrics, start, end, seed, language, bpm):
    """Sing start..end seconds of a song again (the rest stays as it was): a studio punch-in for a line whose words
    came out wrong. The same caption and lyrics as the song; returns the whole song with the new part."""
    from acestep.constants import TASK_INSTRUCTIONS
    seed = int(seed)
    torch.manual_seed(seed)
    params = GenerationParams(task_type="repaint", instruction=TASK_INSTRUCTIONS["repaint"], src_audio=src,
                              repainting_start=float(start), repainting_end=float(end), caption=caption,
                              lyrics=lyrics, seed=seed, bpm=int(bpm) if bpm else None, timesignature="4",
                              vocal_language=language or "unknown", inference_steps=8, shift=3.0, thinking=False)
    config = GenerationConfig(batch_size=1, use_random_seed=False, seeds=[seed], audio_format="flac")
    out = tempfile.mkdtemp()
    res = generate_music(dit, lm, params, config, save_dir=out)
    if not res.success:
        raise gr.Error(f"repaint failed: {res.error}")
    a = res.audios[0]
    path = os.path.join(out, f"repaint_{seed}.flac")
    sf.write(path, a["tensor"].numpy().T, a["sample_rate"])
    return path


# ---- /voice ----
def semantic(w16):
    x = whisper_fx([w16.squeeze(0).cpu().numpy()], return_tensors="pt", return_attention_mask=True)
    feats = whisper._mask_input_features(x.input_features, attention_mask=x.attention_mask).to(DEV)
    with torch.no_grad():
        o = whisper.encoder(feats.to(whisper.encoder.dtype), head_mask=None, output_attentions=False,
                            output_hidden_states=False, return_dict=True)
    return o.last_hidden_state.to(torch.float32)[:, :w16.size(-1) // 320 + 1]


def semantic_long(w16):
    if w16.size(-1) <= 16000 * 30:
        return semantic(w16)
    parts, buf, pos, ov = [], None, 0, 5
    while pos < w16.size(-1):
        chunk = w16[:, pos:pos + 16000 * 30] if buf is None else torch.cat(
            [buf, w16[:, pos:pos + 16000 * (30 - ov)]], dim=-1)
        s = semantic(chunk)
        parts.append(s if pos == 0 else s[:, 50 * ov:])
        buf = chunk[:, -16000 * ov:]
        pos += 30 * 16000 if pos == 0 else chunk.size(-1) - 16000 * ov
    return torch.cat(parts, dim=1)


def crossfade(a, b, n):
    fo, fi = np.cos(np.linspace(0, np.pi / 2, n)) ** 2, np.cos(np.linspace(np.pi / 2, 0, n)) ** 2
    m = min(n, len(b))
    b[:m] = b[:m] * fi[:m] + (a[-n:] * fo)[:m]
    return b


def voice_model(name):
    """The base singing model, or one fine-tuned on a person's voice by /learn (VOICES/NAME.pth)."""
    path = os.path.join(VOICES, f"{name}.pth") if name and name != "base" else None
    if not path:
        return vc
    if not os.path.exists(path):
        raise gr.Error(f"no voice model named {name}: run /learn first")
    m = build_model(mp, stage="DiT")
    m, _, _, _ = load_checkpoint(m, None, path, load_only_params=True, ignore_modules=[], is_distributed=False)
    for k in m:
        m[k].eval()
        m[k].to(DEV)
    m.cfm.estimator.setup_caches(max_batch_size=1, max_seq_length=8192)
    return m


def voice_seconds(source, reference, steps, cfg_rate, semitones, model="base"):
    try:
        secs = sf.info(source).duration
    except Exception:
        secs = 200
    return int(min(290, 40 + secs * (0.25 + int(steps) / 60)))


@spaces.GPU(duration=voice_seconds)
@torch.no_grad()
def voice(source, reference, steps, cfg_rate, semitones, model="base"):
    """Re-voice a sung vocal (source) with the timbre of a reference voice (5-25 s of clean speech or singing).
    The melody is kept (no automatic pitch matching); semitones moves it up or down. model: "base", or the name of a
    voice model learned with /learn."""
    vcm = voice_model(model)
    sr, hop = 44100, 512
    src = torch.tensor(librosa.load(source, sr=sr)[0]).unsqueeze(0).float().to(DEV)
    ref = torch.tensor(librosa.load(reference, sr=sr)[0][:sr * 25]).unsqueeze(0).float().to(DEV)
    src16 = torchaudio.functional.resample(src, sr, 16000)
    ref16 = torchaudio.functional.resample(ref, sr, 16000)
    s_alt, s_ori = semantic_long(src16), semantic(ref16)
    mel, mel2 = mel_spectrogram(src, **MEL), mel_spectrogram(ref, **MEL)
    feat2 = torchaudio.compliance.kaldi.fbank(ref16, num_mel_bins=80, dither=0, sample_frequency=16000)
    style2 = campplus((feat2 - feat2.mean(dim=0, keepdim=True)).unsqueeze(0))
    f0_ori = torch.from_numpy(f0_model.infer_from_audio(ref16[0], thred=0.03)).to(DEV)[None]
    f0_alt = torch.from_numpy(f0_model.infer_from_audio(src16[0], thred=0.03)).to(DEV)[None]
    f0_shift = f0_alt.clone()
    if int(semitones):
        f0_shift[f0_alt > 1] = f0_alt[f0_alt > 1] * 2 ** (int(semitones) / 12)
    cond, *_ = vcm.length_regulator(s_alt, ylens=torch.LongTensor([mel.size(2)]).to(DEV), n_quantizers=3,
                                   f0=f0_shift)
    prompt, *_ = vcm.length_regulator(s_ori, ylens=torch.LongTensor([mel2.size(2)]).to(DEV), n_quantizers=3,
                                     f0=f0_ori)
    window = sr // hop * 30 - mel2.size(2)
    ov_f, ov_w = 16, 16 * hop
    done, chunks, prev = 0, [], None
    while done < cond.size(1):
        c = torch.cat([prompt, cond[:, done:done + window]], dim=1)
        last = done + window >= cond.size(1)
        tgt = vcm.cfm.inference(c, torch.LongTensor([c.size(1)]).to(DEV), mel2, style2, None, int(steps),
                               inference_cfg_rate=float(cfg_rate))[:, :, mel2.size(-1):]
        w = vocoder(tgt.float()).squeeze().cpu().numpy()
        if prev is None:
            if last:
                chunks.append(w)
                break
            chunks.append(w[:-ov_w])
        elif last:
            chunks.append(crossfade(prev, w, ov_w))
            break
        else:
            chunks.append(crossfade(prev, w[:-ov_w], ov_w))
        prev = w[-ov_w:]
        done += tgt.size(2) - ov_f
    path = os.path.join(tempfile.mkdtemp(), "voice.wav")
    sf.write(path, np.concatenate(chunks), sr)
    return path


# ---- /learn: fine-tune the singing model on one person's voice ----
def learn_seconds(files, steps, name):
    return int(min(290, 80 + int(steps) * 0.8))


@spaces.GPU(duration=learn_seconds)
def learn(files, steps, name):
    """Fine-tune the singing model on one person's voice from 1-30 s clips (speech is enough). Saves VOICES/NAME.pth
    for /voice and returns it. Seed-VC's own training code (train.py) with every checkpoint pinned and loaded
    weights-only; OpenVoice V2 varies the voice during training so the model learns timbre, not words."""
    import importlib
    import re
    import shutil
    name = re.sub(r"[^a-z0-9_-]", "", str(name).lower()) or "voice"
    data = tempfile.mkdtemp()
    for i, f in enumerate(files or []):
        a = librosa.load(f if isinstance(f, str) else f.name, sr=44100)[0]
        if 44100 <= len(a) <= 44100 * 30:
            sf.write(os.path.join(data, f"{i:03d}.wav"), a, 44100)
    if not os.listdir(data):
        raise gr.Error("no clips between 1 and 30 seconds")
    c = yaml.safe_load(open(os.path.join(SV, SVC_CFG)))
    c["log_dir"] = tempfile.mkdtemp()
    c["model_params"]["vocoder"]["name"] = os.path.join(SV, "bigvgan")
    c["model_params"]["speech_tokenizer"]["name"] = os.path.join(SV, "whisper-small")
    cpath = os.path.join(data, "..", f"cfg_{name}.yml")
    yaml.safe_dump(c, open(cpath, "w"))
    local = {"se_db.pt": os.path.join(SV, "se_db.pt"), "campplus_cn_common.bin": os.path.join(SV, "campplus_cn_common.bin"),
             "rmvpe.pt": os.path.join(SV, "rmvpe.pt")}

    def pinned(repo, model_filename="pytorch_model.bin", config_filename=None):
        if repo == OPENVOICE[0]:
            return (os.path.join(SV, "openvoice", "converter", "checkpoint.pth"),
                    os.path.join(SV, "openvoice", "converter", "config.json"))
        return local[model_filename]  # anything not pinned fails instead of downloading
    import hf_utils
    hf_utils.load_custom_model_from_hf = pinned
    sv_train = importlib.import_module("train")
    sv_train.load_custom_model_from_hf = pinned
    t = time.time()
    tr = sv_train.Trainer(config_path=cpath, pretrained_ckpt_path=os.path.join(SV, SVC_DIT), data_dir=data, run_name=name,
                          batch_size=2, steps=int(steps), save_interval=10 ** 9, max_epochs=100000, device="cuda")
    tr.train()
    out = os.path.join(VOICES, f"{name}.pth")
    shutil.copy(os.path.join(c["log_dir"], name, "ft_model.pth"), out)
    print(f"learned {name}: {len(os.listdir(data))} clips, {int(steps)} steps, {time.time() - t:.0f} s", flush=True)
    return out


with gr.Blocks(title="Music (private)") as demo:
    gr.Markdown("Private music API for Manoj's channels: ACE-Step 1.5 songs and Seed-VC singing voice conversion.")
    with gr.Tab("Song"):
        cap, lyr = gr.Textbox(label="Style caption", lines=3), gr.Textbox(label="Lyrics", lines=12)
        with gr.Row():
            dur = gr.Number(label="Seconds", value=180)
            sd = gr.Number(label="Seed", value=1, precision=0)
            bp = gr.Number(label="BPM (0 = let the model choose)", value=0, precision=0)
            ks = gr.Textbox(label="Key (blank = model chooses)", value="")
            lang = gr.Textbox(label="Vocal language code", value="ta")
            temp = gr.Number(label="LM temperature", value=0.85)
        go = gr.Button("Make the song")
        a_out, i_out = gr.Audio(type="filepath", label="Song"), gr.Textbox(label="Info")
        go.click(song, [cap, lyr, dur, sd, bp, ks, lang, temp], [a_out, i_out], api_name="song")
    with gr.Tab("Repaint"):
        rp_src = gr.Audio(type="filepath", label="Song")
        rp_cap, rp_lyr = gr.Textbox(label="Style caption", lines=2), gr.Textbox(label="Lyrics", lines=6)
        with gr.Row():
            rp_s = gr.Number(label="From (s)", value=0)
            rp_e = gr.Number(label="To (s)", value=10)
            rp_seed = gr.Number(label="Seed", value=1, precision=0)
            rp_lang = gr.Textbox(label="Vocal language code", value="ta")
            rp_bpm = gr.Number(label="BPM", value=0, precision=0)
        rp_go = gr.Button("Sing this part again")
        rp_out = gr.Audio(type="filepath", label="Song with the new part")
        rp_go.click(repaint, [rp_src, rp_cap, rp_lyr, rp_s, rp_e, rp_seed, rp_lang, rp_bpm], rp_out, api_name="repaint")
    with gr.Tab("Voice"):
        s_in, r_in = gr.Audio(type="filepath", label="Sung vocal"), gr.Audio(type="filepath", label="Reference voice")
        with gr.Row():
            st = gr.Number(label="Diffusion steps", value=30, precision=0)
            cr = gr.Number(label="CFG rate", value=0.7)
            semi = gr.Number(label="Semitones", value=0, precision=0)
            vm = gr.Textbox(label="Voice model (base, or a learned name)", value="base")
        go2 = gr.Button("Convert")
        v_out = gr.Audio(type="filepath", label="Converted vocal")
        go2.click(voice, [s_in, r_in, st, cr, semi, vm], v_out, api_name="voice")
    with gr.Tab("Learn a voice"):
        clips = gr.File(label="Clips of the voice (1-30 s each)", file_count="multiple")
        with gr.Row():
            lsteps = gr.Number(label="Steps", value=200, precision=0)
            lname = gr.Textbox(label="Name", value="manoj")
        go3 = gr.Button("Learn")
        l_out = gr.File(label="Voice model")
        go3.click(learn, [clips, lsteps, lname], l_out, api_name="learn")

if os.environ.get("MUSIC_TEST") is None:
    demo.queue(max_size=8).launch()
