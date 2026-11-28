# Working on your own computer (local Claude Code)

This guide sets up the project on your computer so a local Claude Code session can continue the work, and shows
how to hand the work back to the cloud session. It takes about 30 minutes the first time.

The work lives in two places, and both your computer and the cloud use them:

| What | Where |
|---|---|
| Scripts, story files, logs | GitHub: `RGCbe/HUGGING-FACE`, branch `claude/youtube-agent-skill-48ifal` |
| Pictures, clips, voices (big or private files) | Your private Hugging Face dataset `Rggroups/frank-ep01-work` |

---

## 1. One-time setup

### A. Windows: use Ubuntu inside Windows (WSL)
The video tools (ffmpeg, the music synthesizer) are easiest on Linux. On Windows:

1. Open **PowerShell as Administrator** and run: `wsl --install -d Ubuntu`
2. Restart the computer, open **Ubuntu** from the Start menu, and make a user name and password.
3. Do every step below **inside the Ubuntu window**.

(Mac: use the Terminal and Homebrew instead of `apt`; Linux: just open a terminal.)

### B. Install the tools (in Ubuntu)
```bash
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv ffmpeg fluidsynth fluid-soundfont-gm fonts-dejavu
```

### C. Install Claude Code
Install the **Claude desktop app** from https://claude.ai/download (it includes Claude Code), or the terminal
version from the official guide: https://code.claude.com/docs . Sign in with your Claude account.

### D. Get the project
```bash
cd ~
git clone https://github.com/RGCbe/HUGGING-FACE.git
cd HUGGING-FACE
git checkout claude/youtube-agent-skill-48ifal
python3 -m venv .venv
source .venv/bin/activate
pip install huggingface_hub gradio_client pillow numpy soundfile reportlab
pip install -r videos/kural/requirements-eleven.txt -r videos/kural/requirements-whisper.txt
```

### E. Your keys (never in chat, never on GitHub)
Create a file named `.env.local` in the `HUGGING-FACE` folder. Git ignores this file, so it never goes to GitHub.
Put one key per line (only the ones you use):
```
HF_TOKEN=hf_...            # Hugging Face token that can write to your own repos (pictures, clips, your Spaces)
HF_READ_TOKEN=hf_...       # your read-only Hugging Face token (zerogpu-clips)
ELEVENLABS_API_KEY=...     # ElevenLabs > Profile > API keys
CF_ACCOUNT_ID=...          # Cloudflare dashboard (free picture model)
CF_API_TOKEN=...           # Cloudflare "Workers AI" API token
```
Load them each time you open a new terminal:
```bash
cd ~/HUGGING-FACE && source .venv/bin/activate && set -a && source .env.local && set +a
```
(Where to find a key: Hugging Face > Settings > Access Tokens; ElevenLabs > Profile; Cloudflare > My Profile >
API Tokens. You can make a new key instead of copying the cloud one; the cloud keeps its own.)

### F. Download the episode's working files
```bash
cd ~/HUGGING-FACE/videos/manga
python3 work_backup.py pull f-rank/ep01/anime
```
This brings the 48 approved pictures, the clips made so far, the voices and the sound effects.

---

## 2. Start the local Claude Code session
Open the `HUGGING-FACE` folder in Claude Code (desktop app: choose the folder; terminal: run `claude` inside it).
Paste this as your first message:

> Read videos/manga/LOCAL_SETUP.md, videos/manga/f-rank/STATUS.md and videos/manga/f-rank/ep01/anime/LOG.md.
> We are on branch claude/youtube-agent-skill-48ifal. Keys are in .env.local (never print them). Then continue
> with: [what you want to do]

---

## 3. Rules while you work locally
- **Push before you switch** (see section 4). Anything not pushed stays only on your computer.
- **One place at a time.** Don't edit the same files locally and in the cloud at the same moment.
- **GPU minutes are shared.** Your 40 PRO minutes a day are used by both. The cloud's daily clip run starts at
  10:10 UTC (3:40 pm India time); don't start a clip run locally at the same time.
- **Never put keys or voice files on GitHub.** Voices and clips go only to the private dataset (step 4).

---

## 4. Hand the work back to the cloud
```bash
cd ~/HUGGING-FACE
git add -A && git commit -m "what I changed" && git push
cd videos/manga && python3 work_backup.py push f-rank/ep01/anime
```
Then, in the cloud chat, say: **"pull your local changes"**. The cloud session downloads them (`git pull` and
`work_backup.py pull`) and carries on from there.
