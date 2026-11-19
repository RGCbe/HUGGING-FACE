"""The owner's one private ZeroGPU Space (Rggroups/anime-motion) takes turns between two apps:

    wan      Wan 2.1 image-to-video, 4 steps (the motion shots; zerogpu_clips.py)
    longcat  LongCat-Video-Avatar 1.6 (the talking shots with lip-sync; lipsync_clips.py)

    python3 space_app.py status
    python3 space_app.py use wan|longcat [--force]   # switch (if needed; --force: upload again) and wait until running

Both apps come from fixed, already-read sources: the Wan app from the Space's own history (the revision it had
before the first switch), the LongCat code from a pinned revision of victor/LongCat-Video-Avatar-1.6 plus this
repo's spaces/longcat/ files. Switching rebuilds the Space (about 10-25 minutes, no GPU time). Uses HF_TOKEN.
"""
import os
import sys
import tempfile
import time

from huggingface_hub import HfApi, snapshot_download

SPACE = "Rggroups/anime-motion"
WAN_REVISION = "f4bf3375a95bed9c6b0da81e6772d43186ebf292"  # the Space with its Wan 2.1 app (19 Nov 2026)
WAN_FILES = ["app.py", "requirements.txt", "README.md"]
LONGCAT_CODE = ("victor/LongCat-Video-Avatar-1.6", "6a9839d2da84ccce5f89a25c8853419399a18d07")
LEFT_OUT = ("longcat_video/utils/prompt_enhancer.py", "longcat_video/audio_process/vocal_separator.py")
HERE = os.path.dirname(os.path.abspath(__file__))
MARK = "app_kind.txt"


def api():
    return HfApi(token=os.environ["HF_TOKEN"])


def current(a):
    files = a.list_repo_files(SPACE, repo_type="space")
    if MARK not in files:
        return "wan"
    path = a.hf_hub_download(SPACE, MARK, repo_type="space", force_download=True)
    return open(path).read().strip()


def stage(a):
    rt = a.get_space_runtime(SPACE)
    return rt.stage, rt


def wait_running(a, minutes=60):
    t0, last = time.time(), None
    while time.time() - t0 < minutes * 60:
        st, rt = stage(a)
        if st != last:
            print(f"  Space: {st}", flush=True)
            last = st
        if st == "RUNNING":
            return True
        if st in ("BUILD_ERROR", "RUNTIME_ERROR", "CONFIG_ERROR"):
            raise RuntimeError(f"the Space stopped with {st}: {getattr(rt, 'raw', {}).get('errorMessage', '')[:500]}")
        if st in ("SLEEPING", "STOPPED"):
            a.restart_space(SPACE)
        time.sleep(30)
    raise RuntimeError(f"the Space was not running after {minutes} minutes")


def use(kind, force=False):
    if kind not in ("wan", "longcat"):
        sys.exit("kind: wan or longcat")
    a = api()
    if not a.space_info(SPACE).private:
        sys.exit(f"{SPACE} is not private: not touching it")
    now = current(a)
    if now == kind and not force:
        print(f"{SPACE} already runs the {kind} app")
        return wait_running(a)
    print(f"switching {SPACE}: {now} -> {kind}" if now != kind else f"uploading the {kind} app again", flush=True)
    with tempfile.TemporaryDirectory() as d:
        if kind == "longcat":
            snapshot_download(LONGCAT_CODE[0], repo_type="space", revision=LONGCAT_CODE[1], local_dir=d,
                              allow_patterns=["longcat_video/**/*.py"])
            for p in LEFT_OUT:
                if os.path.exists(os.path.join(d, p)):
                    os.remove(os.path.join(d, p))
            src = os.path.join(HERE, "spaces", "longcat")
            for f in os.listdir(src):
                if not os.path.isfile(os.path.join(src, f)):
                    continue
                with open(os.path.join(src, f), "rb") as i, open(os.path.join(d, f), "wb") as o:
                    o.write(i.read())
            delete = None
        else:
            for f in WAN_FILES:
                p = a.hf_hub_download(SPACE, f, repo_type="space", revision=WAN_REVISION)
                with open(p, "rb") as i, open(os.path.join(d, f), "wb") as o:
                    o.write(i.read())
            delete = ["longcat_video/**", "NOTICE", "LICENSE"]
        with open(os.path.join(d, MARK), "w") as o:
            o.write(kind + "\n")
        a.upload_folder(repo_id=SPACE, repo_type="space", folder_path=d, delete_patterns=delete,
                        commit_message=f"switch to the {kind} app")
    time.sleep(20)
    return wait_running(a)


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("status", "use"):
        sys.exit(__doc__)
    a = api()
    if sys.argv[1] == "status":
        st, _ = stage(a)
        print(f"{SPACE}: {current(a)} app, {st}")
    else:
        use(sys.argv[2] if len(sys.argv) > 2 else "", force="--force" in sys.argv)
        print("running")


if __name__ == "__main__":
    main()
