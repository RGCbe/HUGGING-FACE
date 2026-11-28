"""Make the SkyReels takes for the Vaibhav video: 2 per approved start picture (seeds 7 and 21), skipping takes that
exist, stopping when the owner's daily ZeroGPU time runs out (run it again the next day and it carries on).

    python3 skyreels_batch.py                 # every picture in skyreels_prompts.json
    python3 skyreels_batch.py c02 c03 p02b    # only these

Needs HF_TOKEN in the environment (sent only to the owner's own private Space Rggroups/skyreels, through
videos/manga/skyreels_clips.py). The Space must be RUNNING: if it is PAUSED, restart it from its Settings page or with
HfApi().restart_space("Rggroups/skyreels"). Start pictures are read from ~/.cache/music/vaibhav-video/animeA and the takes
written to ~/.cache/music/vaibhav-video/skyreels (restore both from the private dataset first: HANDOVER.md).
A prompt entry may name another picture with "picture" (p02b is a remake of p02).
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PICS = os.path.expanduser("~/.cache/music/vaibhav-video/animeA")
OUT = os.path.expanduser("~/.cache/music/vaibhav-video/skyreels")
prompts = json.load(open(os.path.join(HERE, "skyreels_prompts.json")))["pictures"]
chosen = json.load(open(os.path.join(HERE, "pictures_chosen.json")))["pictures"]
names = sys.argv[1:] or list(prompts)
unknown = [n for n in names if n not in prompts]
if unknown:
    sys.exit(f"no prompt for: {unknown}")
missing = [n for n in names if prompts[n].get("picture", n) not in chosen]
if missing:
    sys.exit(f"start picture not approved yet: {missing}")
jobs = [(n, s) for n in names for s in (7, 21) if not os.path.exists(f"{OUT}/{n}_s{s}.mp4")]
print(f"{len(jobs)} takes to make", flush=True)
for n, seed in jobs:
    t0 = time.time()
    pic = prompts[n].get("picture", n)
    p = subprocess.run([sys.executable, "skyreels_clips.py", "clip", f"{PICS}/{pic}.png", f"{OUT}/{n}_s{seed}.mp4",
                        "--prompt", prompts[n]["prompt"], "--mode", "fast", "--steps", "4", "--size", "960x544",
                        "--seconds", str(prompts[n]["seconds"]), "--seed", str(seed)],
                       cwd=os.path.join(REPO, "videos", "manga"), capture_output=True, text=True)
    out = (p.stdout + p.stderr).strip()
    if p.returncode == 0:
        print(f"made {n}_s{seed} in {time.time() - t0:.0f} s: {out.splitlines()[-1][:160]}", flush=True)
        continue
    low = out.lower()
    if any(k in low for k in ("quota", "gpu task aborted", "exceeded", "zerogpu", "no gpu was available")):
        print(f"GPU time used up at {n}_s{seed}: stopping; run again tomorrow. ({out.splitlines()[-1][:200]})", flush=True)
        break
    if "paused" in low:
        sys.exit("the Space Rggroups/skyreels is PAUSED: restart it first (see the top of this file)")
    print(f"FAILED {n}_s{seed}: {out[-400:]}", flush=True)
    if "Traceback" in out and ("Connection" in out or "timed out" in out):
        time.sleep(60)
done = sorted(f for f in os.listdir(OUT) if f.endswith(".mp4") and "_s" in f and not f.startswith("S"))
print(f"done: {len(done)} takes exist: {' '.join(done)}", flush=True)
