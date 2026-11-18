"""Animate an episode's approved keyframes into video clips on a rented GridShare GPU (Wan 2.2 TI2V-5B).

    python3 clips.py run SHOTS.json KEYFRAMES_DIR OUT_DIR --only S09,S31 [--takes 1] [--steps 30] [--size 1280x704]
                     [--node ID] [--max-min 120]

Each AI shot's approved keyframe (KEYFRAMES_DIR/SNN.jpg) and its "motion" line from the shot list go to the
machine through the private drop box; clips come back as OUT_DIR/SNN_a.mp4. Frames follow the shot length
(24 fps, 4k+1 frames as Wan needs). The machine is always ended at the end (see keyframes.watch).
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dropbox  # noqa: E402
import keyframes  # noqa: E402

STYLE = ("Photorealistic live-action movie scene, real people, natural human motion, cinematic lighting, smooth camera "
         "movement, the faces stay exactly the same. ")
NEGATIVE = ("cartoon, anime, illustration, drawing, 3d render, static, still picture, blurry, low quality, deformed, "
            "disfigured, extra fingers, poorly drawn hands, poorly drawn face, morphing face, changing face, flicker, "
            "watermark, text, subtitles, extra people")


def frames_for(seconds, fps=24):
    n = int(round(seconds * fps))
    return max(33, min(121, n - (n - 1) % 4))  # Wan wants 4k+1 frames; 121 = 5 s is its longest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "job"])
    ap.add_argument("shots")
    ap.add_argument("keyframes_dir")
    ap.add_argument("out_dir")
    ap.add_argument("--only")
    ap.add_argument("--takes", type=int, default=1)
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--size", default="1280x704")
    ap.add_argument("--also-size", help="test: also make every clip at this size (named NAME_lo)")
    ap.add_argument("--node")
    ap.add_argument("--max-rate", type=float, default=35)
    ap.add_argument("--max-min", type=float, default=120)
    a = ap.parse_args()
    w, h = map(int, a.size.split("x"))
    d = json.load(open(a.shots))
    only = set(a.only.split(",")) if a.only else None
    clips, files = [], []
    for s in d["shots"]:
        if s.get("kind") != "ai" or (only and s["id"] not in only):
            continue
        kf = os.path.join(a.keyframes_dir, f"{s['id']}.jpg")
        if not os.path.exists(kf):
            print(f"{s['id']}: no approved keyframe yet, skipped")
            continue
        files.append((f"keyframes/{s['id']}.jpg", kf))
        for k in range(a.takes):
            clips.append({"name": f"{s['id']}_{'abc'[k]}", "image": f"keyframes/{s['id']}.jpg", "seed": 1 + k,
                          "frames": frames_for(s["seconds"] + 0.5), "prompt": STYLE + s["motion"] + "."})
    if a.also_size:
        w2, h2 = map(int, a.also_size.split("x"))
        clips += [dict(c, name=c["name"] + "_lo", width=w2, height=h2) for c in clips]
    os.makedirs(a.out_dir, exist_ok=True)
    clips = [c for c in clips if not os.path.exists(os.path.join(a.out_dir, c["name"] + ".mp4"))]
    job = {"model": "Wan-AI/Wan2.2-TI2V-5B-Diffusers", "width": w, "height": h, "fps": 24, "steps": a.steps,
           "guidance": 5.0, "negative": NEGATIVE, "clips": clips}
    if a.cmd == "job" or not clips:
        print(json.dumps(job, indent=1)[:3000])
        return
    run_id = "clips-" + time.strftime("%Y%m%d-%H%M%S")
    dropbox.put(f"{run_id}/job.json", json.dumps(job).encode(), "application/json")
    for name, path in files:
        dropbox.put(f"{run_id}/{name}", open(path, "rb").read(), "image/jpeg")
    for f in ("boot.sh", "clips_worker.py"):
        dropbox.put(f"{run_id}/{f}", open(os.path.join(HERE, f), "rb").read())
    env = {"DROP_URL": f"{dropbox.base()}/files/{run_id}", "WORKER": "clips_worker.py", "NVIDIA_DRIVER_CAPABILITIES": "all",
           "GRIDSHARE_START_CMD": "bash -c 'curl -fsS -A gs-machine \"$DROP_URL/boot.sh\" | bash'"}
    body = {"image": "gridshare/pytorch:latest", "label": "wan-clips", "gpu_count": 1, "disk_gb": 80, "job_type": "ondemand",
            "exposed_ports": [], "env": env, "reliability_tier": "bronze"}
    if a.node:
        body["node_id"] = body["preferred_node_id"] = a.node
    print(f"{len(clips)} clips, {len(files)} keyframes, run {run_id}", flush=True)
    inst = keyframes.gs("POST", "/v1/instances/", body)
    iid = inst["id"]
    print(f"machine {iid[:8]} {inst.get('status')} at ₹{inst.get('rate_per_hr_inr')}/hour", flush=True)
    if (inst.get("rate_per_hr_inr") or 0) > a.max_rate or (a.node and keyframes.gs("GET", f"/v1/instances/{iid}").get("node_id") != a.node):
        print("not the chosen machine or too expensive: stopping")
        return keyframes.delete(iid, run_id, a.out_dir, set())
    keyframes.watch(iid, run_id, a.out_dir, a.max_min)


if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGTERM, lambda *_: sys.exit("terminated"))
    main()
