"""SkyReels-V2 clips on the owner's own private ZeroGPU Space (Rggroups/skyreels): a TEST beside Wan 2.1.

    python3 skyreels_clips.py deploy                       # create (private) or update the Space, wait until running
    python3 skyreels_clips.py status
    python3 skyreels_clips.py clip START.png OUT.mp4 --prompt "..." [--end END.png] [--mode fast|full] [--steps 6]
                              [--seconds 3] [--guidance 5] [--negative "..."] [--seed 7] [--size 832x480]

The Space (spaces/skyreels/app.py) runs SkyReels-V2-DF-14B-540P through diffusers: a start picture, or a start AND an
end picture (key poses at both ends), to a clip at 24 fps. "fast" uses the CausVid speed LoRA with guidance off (the
negative prompt is ignored), "full" uses guidance and more steps (much more GPU time).
Where data goes: the pictures and prompts only to the owner's own private Space, with HF_TOKEN (CLAUDE.md).
Each call is logged to OUT's folder in skyreels_log.jsonl.
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SPACE = "Rggroups/skyreels"
SRC = os.path.join(HERE, "spaces", "skyreels")


def api():
    from huggingface_hub import HfApi
    return HfApi(token=os.environ["HF_TOKEN"])


def stage(a):
    rt = a.get_space_runtime(SPACE)
    return rt.stage, rt.hardware


def wait_running(a, minutes=60):
    last = None
    for _ in range(minutes * 2):
        st, hw = stage(a)
        if st != last:
            print(f"{SPACE}: {st} ({hw})", flush=True)
            last = st
        if st == "RUNNING":
            return True
        if st in ("BUILD_ERROR", "RUNTIME_ERROR", "CONFIG_ERROR"):
            return False
        time.sleep(30)
    return False


def deploy():
    a = api()
    if a.repo_exists(SPACE, repo_type="space"):
        if not a.space_info(SPACE).private:
            raise SystemExit(f"{SPACE} exists and is not private: refusing to upload")
    else:
        a.create_repo(SPACE, repo_type="space", space_sdk="gradio", private=True, space_hardware="zero-a10g")
        print(f"created {SPACE} (private, ZeroGPU)")
    a.upload_folder(repo_id=SPACE, repo_type="space", folder_path=SRC, commit_message="SkyReels-V2 test app (pinned)")
    time.sleep(20)
    sys.exit(0 if wait_running(a) else 1)


def clip(a):
    from gradio_client import Client, handle_file
    client = Client(SPACE, token=os.environ["HF_TOKEN"], verbose=False)  # the owner's own private Space only
    w, h = (int(x) for x in a.size.split("x"))
    t0 = time.time()
    video, note = client.predict(handle_file(a.start), handle_file(a.end) if a.end else None, a.prompt,
                                 a.negative or "", a.mode, a.seconds, a.steps, a.guidance, w, h, a.seed,
                                 api_name="/generate")
    src = video["video"] if isinstance(video, dict) else video
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    shutil.copy(src, a.out)
    rec = {"out": os.path.basename(a.out), "start": os.path.basename(a.start), "end": a.end and os.path.basename(a.end),
           "mode": a.mode, "steps": a.steps, "seconds": a.seconds, "seed": a.seed, "size": a.size, "prompt": a.prompt,
           "negative": a.negative, "note": note, "wall_s": round(time.time() - t0)}
    with open(os.path.join(os.path.dirname(os.path.abspath(a.out)), "skyreels_log.jsonl"), "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"{a.out}: {note} (wall {rec['wall_s']} s)")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("deploy")
    sub.add_parser("status")
    c = sub.add_parser("clip")
    c.add_argument("start")
    c.add_argument("out")
    c.add_argument("--prompt", required=True)
    c.add_argument("--end")
    c.add_argument("--mode", choices=["fast", "full"], default="fast")
    c.add_argument("--steps", type=int, default=6)
    c.add_argument("--seconds", type=float, default=3.0)
    c.add_argument("--guidance", type=float, default=5.0)
    c.add_argument("--negative", default="")
    c.add_argument("--seed", type=int, default=7)
    c.add_argument("--size", default="832x480")
    a = ap.parse_args()
    if a.cmd == "deploy":
        deploy()
    elif a.cmd == "status":
        print(SPACE, *stage(api()))
    else:
        clip(a)


if __name__ == "__main__":
    main()
