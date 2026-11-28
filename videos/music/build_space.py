"""Build the owner's private ZeroGPU music Space (Rggroups/music) from pinned, already-read sources, and upload it.

    python3 build_space.py            # create the Space if needed (private, ZeroGPU), upload, wait until running
    python3 build_space.py status

What goes in (read 25 Nov 2026; see the safety notes at the top of space/app.py):
- space/ from this repo: app.py, requirements.txt, README.md, and the dac/ stub.
- ACE-Step 1.5 code (MIT): the acestep/ package of the official Space ACE-Step/Ace-Step-v1.5 at a pinned revision,
  without its UI, training, API-server and nano-vllm files (we run the plain PyTorch path).
- Seed-VC code (GPL-3.0): modules/ and the fine-tuning code (train.py, optimizers.py, hf_utils.py,
  data/ft_dataset.py) of github.com/Plachtaa/seed-vc at a pinned commit (git checks the content).
The Space is refused if it exists and is not private. Uses HF_TOKEN (the owner's own Space only).
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time

from huggingface_hub import HfApi, snapshot_download

SPACE = "Rggroups/music"
ACE_CODE = ("ACE-Step/Ace-Step-v1.5", "7403460e9b34972f760317b56048f6cb9d4a3a11")
ACE_LEFT_OUT = ("acestep/gradio_ui", "acestep/training", "acestep/api_server.py", "acestep/third_parts")
SEEDVC = ("https://github.com/Plachtaa/seed-vc.git", "51383efd921027683c89e5348211d93ff12ac2a8")
HERE = os.path.dirname(os.path.abspath(__file__))


def api():
    return HfApi(token=os.environ["HF_TOKEN"])


def stage(a):
    try:
        rt = a.get_space_runtime(SPACE)
        return rt.stage, rt.hardware
    except Exception as e:  # noqa: BLE001
        return f"unknown ({e.__class__.__name__})", None


def assemble(d):
    for f in ("app.py", "requirements.txt", "README.md"):
        shutil.copy(os.path.join(HERE, "space", f), d)
    ace = snapshot_download(ACE_CODE[0], repo_type="space", revision=ACE_CODE[1], token=False,
                            local_dir=os.path.join(d, "_ace"), allow_patterns=["acestep/**", "LICENSE"])
    for p in ACE_LEFT_OUT:
        full = os.path.join(ace, p)
        if os.path.isdir(full):
            shutil.rmtree(full)
        elif os.path.exists(full):
            os.remove(full)
    shutil.move(os.path.join(ace, "acestep"), os.path.join(d, "acestep"))
    shutil.move(os.path.join(ace, "LICENSE"), os.path.join(d, "LICENSE-ACE-Step"))
    shutil.rmtree(ace)
    sv = os.path.join(d, "_seedvc")
    os.makedirs(sv)
    git = ["git", "-C", sv]
    subprocess.run(git + ["init", "-q"], check=True)
    subprocess.run(git + ["fetch", "-q", "--depth", "1", SEEDVC[0], SEEDVC[1]], check=True)
    subprocess.run(git + ["checkout", "-q", "FETCH_HEAD"], check=True)
    got = subprocess.run(git + ["rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    if got != SEEDVC[1]:
        raise SystemExit(f"Seed-VC commit mismatch: {got}")
    os.makedirs(os.path.join(d, "seedvc"))
    shutil.move(os.path.join(sv, "modules"), os.path.join(d, "seedvc", "modules"))
    for f in ("train.py", "optimizers.py", "hf_utils.py"):  # the fine-tuning code (read 26 Nov 2026), for /learn
        shutil.move(os.path.join(sv, f), os.path.join(d, "seedvc", f))
    os.makedirs(os.path.join(d, "seedvc", "data"))
    shutil.move(os.path.join(sv, "data", "ft_dataset.py"), os.path.join(d, "seedvc", "data", "ft_dataset.py"))
    shutil.move(os.path.join(sv, "LICENSE"), os.path.join(d, "LICENSE-Seed-VC"))
    shutil.rmtree(sv)
    shutil.copytree(os.path.join(HERE, "space", "dac"), os.path.join(d, "seedvc", "dac"))
    for root, dirs, _ in os.walk(d):
        for x in [x for x in dirs if x == "__pycache__"]:
            shutil.rmtree(os.path.join(root, x))


def wait_running(a, minutes=60):
    end = time.time() + minutes * 60
    last = None
    while time.time() < end:
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


def main():
    a = api()
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        print(SPACE, *stage(a))
        return
    if a.repo_exists(SPACE, repo_type="space"):
        if not a.space_info(SPACE).private:
            raise SystemExit(f"{SPACE} exists and is not private: refusing to upload")
    else:
        a.create_repo(SPACE, repo_type="space", space_sdk="gradio", private=True, space_hardware="zero-a10g")
        print(f"created {SPACE} (private, ZeroGPU)")
    with tempfile.TemporaryDirectory() as d:
        assemble(d)
        a.upload_folder(repo_id=SPACE, repo_type="space", folder_path=d, commit_message="build from pinned sources",
                        delete_patterns=["acestep/**", "seedvc/**"])
    time.sleep(20)
    sys.exit(0 if wait_running(a) else 1)


if __name__ == "__main__":
    main()
