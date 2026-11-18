#!/bin/bash
# First thing a rented GridShare machine runs (its GRIDSHARE_START_CMD downloads this from the drop box).
# DROP_URL is this run's folder in the drop box: DROP_URL/NAME.
# Makes a clean Python 3.12 with uv (the gridshare/pytorch image's own torch sits on Python 3.11.0rc1, which lacks
# sys.get_int_max_str_digits, so torch._dynamo, and with it diffusers, cannot even be imported), installs PyTorch
# and the picture tools there, runs keyframes_worker.py, uploads the log, says DONE, then waits to be deleted.
D="$DROP_URL"
put() { curl -sS -m 120 -A gs-machine -X PUT --data-binary "$2" "$D/$1" >/dev/null || true; }
say() { put out/status.txt "$(date -u +%H:%M:%S) $1"; }
cd /root
say "booted: $(nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader 2>&1 | head -1); installing Python 3.12 + PyTorch"
python3 -m pip install -q uv > setup.log 2>&1 || say "uv install failed: $(tail -c 1500 setup.log)"
python3 -m uv venv -q -p 3.12 /root/venv >> setup.log 2>&1 || say "venv failed: $(tail -c 1500 setup.log)"
# 'python3 -m uv pip' installs into the Python that runs uv unless --python names the venv
python3 -m uv pip install -q --python /root/venv/bin/python torch --index-url https://download.pytorch.org/whl/cu128 >> setup.log 2>&1 \
  || say "torch install failed: $(tail -c 1500 setup.log)"
python3 -m uv pip install -q --python /root/venv/bin/python "diffusers>=0.37" "transformers>=4.56" accelerate safetensors "huggingface_hub[hf_xet]" pillow \
  >> setup.log 2>&1 || say "tools install failed: $(tail -c 1500 setup.log)"
say "installed: $(/root/venv/bin/python -c 'import sys, torch, diffusers; print(sys.version.split()[0], torch.__version__, torch.cuda.is_available(), diffusers.__version__)' 2>&1 | tail -1)"
curl -sS -m 120 -A gs-machine -o kw.py "$D/keyframes_worker.py"
/root/venv/bin/python -u kw.py > run.log 2>&1
cat setup.log >> run.log
curl -sS -m 120 -A gs-machine -X PUT --data-binary @run.log "$D/out/run.log" >/dev/null
put out/DONE done
sleep 7200
