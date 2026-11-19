"""Keep an episode's working files (approved keyframes, clips, voices, sound effects) safe between cloud machines.
They are not in git (out/ and voice/ are ignored, and the voices must never be public); a cloud machine is wiped when
it is replaced. So they live in a PRIVATE Hugging Face dataset on the owner's account.

    python3 work_backup.py push EPISODE_DIR [REPO]   # upload (only changed files are sent)
    python3 work_backup.py pull EPISODE_DIR [REPO]   # restore onto a fresh machine

REPO defaults to Rggroups/frank-ep01-work. Uses HF_TOKEN; refuses to push to a repo that is not private.
"""
import os
import sys

from huggingface_hub import HfApi, snapshot_download

PATTERNS = ["out/keyframes_ok/*", "out/clips/*", "out/clips_raw/*", "out/sfx/*", "out/retired/*", "voice/*",
            "out/episode_cut*_720p.mp4"]


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("push", "pull"):
        sys.exit(__doc__)
    cmd, ep = sys.argv[1], sys.argv[2]
    repo = sys.argv[3] if len(sys.argv) > 3 else "Rggroups/frank-ep01-work"
    api = HfApi(token=os.environ["HF_TOKEN"])
    if cmd == "push":
        api.create_repo(repo, repo_type="dataset", private=True, exist_ok=True)
        if not api.repo_info(repo, repo_type="dataset").private:
            sys.exit(f"{repo} is not private: not uploading")
        api.upload_folder(repo_id=repo, repo_type="dataset", folder_path=ep, allow_patterns=PATTERNS,
                          commit_message="working files")
        print(f"pushed to {repo}")
    else:
        snapshot_download(repo, repo_type="dataset", local_dir=ep, token=os.environ["HF_TOKEN"])
        print(f"restored {repo} into {ep}")


if __name__ == "__main__":
    main()
