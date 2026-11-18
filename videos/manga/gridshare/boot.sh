#!/bin/bash
# First thing a rented GridShare machine runs (its GRIDSHARE_START_CMD downloads this from the drop box).
# DROP_URL is this run's folder in the drop box: DROP_URL/NAME.
# Installs the picture tools, runs keyframes_worker.py, uploads the log, says DONE, then waits to be deleted.
D="$DROP_URL"
put() { curl -sS -m 120 -A gs-machine -X PUT --data-binary "$2" "$D/$1" >/dev/null || true; }
cd /root
put out/status.txt "$(date -u +%H:%M:%S) booted: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>&1 | head -1)"
python3 -m pip install -q -U "diffusers>=0.37" "transformers>=4.56" accelerate safetensors "huggingface_hub[hf_xet]" pillow \
  > pip.log 2>&1 || put out/status.txt "pip failed: $(tail -c 1500 pip.log)"
curl -sS -m 120 -A gs-machine -o kw.py "$D/keyframes_worker.py"
python3 -u kw.py > run.log 2>&1
curl -sS -m 120 -A gs-machine -X PUT --data-binary @run.log "$D/out/run.log" >/dev/null
put out/DONE done
sleep 7200
