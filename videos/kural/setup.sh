#!/usr/bin/env bash
# Get a fresh cloud container ready to make Super Kural videos, then write the settings make.py
# reads to $KURAL_HOME/env.sh (source it). Safe to run again: finished steps are skipped.
#
# Needs: uv, ffmpeg, node with Playwright (all present in Claude Code cloud containers), and
# HF_TOKEN, a read token for the private Hugging Face dataset in config.json "voice_repo" that holds
# the voice sample (ref_en.opus) and the three approved fixed clips (intro.opus, says.opus, outro.opus).
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
home=${KURAL_HOME:-$HOME/.cache/super-kural}
mkdir -p "$home/voice" "$home/work" "$home/out" "$home/hf"

if [ ! -x "$home/tts/bin/python" ]; then
  echo "installing the voice model's Python packages (a few minutes)"
  uv venv -q --python 3.11 "$home/tts"
  VIRTUAL_ENV="$home/tts" uv pip install -q --no-deps --index-strategy unsafe-best-match \
    --extra-index-url https://download.pytorch.org/whl/cpu -r "$here/requirements-tts.txt"
fi
if [ ! -x "$home/whisper/bin/python" ]; then
  echo "installing the listening model's Python packages"
  uv venv -q --python 3.13 "$home/whisper"
  VIRTUAL_ENV="$home/whisper" uv pip install -q --no-deps -r "$here/requirements-whisper.txt"
fi

repo=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['voice_repo'])" "$here/config.json")
for f in ref_en intro says outro; do
  [ -s "$home/voice/$f.wav" ] && continue
  if [ -z "${HF_TOKEN:-}" ]; then
    echo "HF_TOKEN is not set: add a Hugging Face read token for $repo to the environment settings" >&2
    exit 3
  fi
  curl -fsSL -H "Authorization: Bearer $HF_TOKEN" -o "$home/voice/$f.opus" \
    "https://huggingface.co/datasets/$repo/resolve/main/$f.opus"
  ffmpeg -nostdin -v error -y -i "$home/voice/$f.opus" -ar 24000 -ac 1 "$home/voice/$f.wav"
done

playwright=${PLAYWRIGHT_MODULE:-$(npm root -g)/playwright}
[ -d "$playwright" ] || { echo "Playwright not found at $playwright" >&2; exit 4; }

cat > "$home/env.sh" <<EOF
export KURAL_HOME="$home"
export KURAL_WORK="$home/work"
export KURAL_OUT="$home/out"
export VOICE_REF="$home/voice/ref_en.wav"
export FIXED_DIR="$home/voice"
export TTS_PY="$home/tts/bin/python"
export WHISPER_PY="$home/whisper/bin/python"
export HF_HOME="$home/hf"
export PLAYWRIGHT_MODULE="$playwright"
EOF
echo "ready: source $home/env.sh"
