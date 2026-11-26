"""2D Anime Sakuga & Continuity Pipeline (V2).

Supports Claude Code and local workflows for 'The F-Rank Tea Seller':
  python anime_v2.py t2v --prompt "..." --out shot1.mp4 [--seconds 2.5] [--seed 301]
  python anime_v2.py chain --prev shot1.mp4 --prompt "..." --out shot2.mp4 [--seconds 2.5] [--seed 302]
  python anime_v2.py fx --in shot.mp4 --out shot_fx.mp4 [--flash-at 1.2] [--shake 12]

Tokens (CLAUDE.md: HF_TOKEN goes only to the owner's own Spaces and datasets, never to third-party Spaces):
  - chain: HF_READ_TOKEN only, and only to zerogpu-aoti/wan2-2-fp8da-aoti-faster (Hugging Face's own ZeroGPU team;
    the owner chose on 19 Nov 2026 to give that one Space his read token for his GPU time). HF_TOKEN is never sent.
  - t2v: mastaP/wan22-remix-sfw-t2v belongs to another person, so it gets NO token at all (token=False: gradio_client
    would otherwise send the saved or HF_TOKEN token by itself). It runs on the anonymous free GPU time.
Never prints or logs tokens.
"""
import argparse
import os
import shutil
import subprocess
import tempfile
from gradio_client import Client, handle_file

DEFAULT_NEG = (
    "photorealistic, live action, 3D CGI, still picture, static photo, "
    "deformed hands, extra fingers, blurry, watermark, subtitles, text"
)


TRUSTED_SPACE = "zerogpu-aoti/wan2-2-fp8da-aoti-faster"  # the one non-owner Space the owner allowed his read token


def _load_token(space):
    """The token for this Space: the read-only token for TRUSTED_SPACE, and False (send nothing, not even a saved
    token) for any other Space that is not the owner's. HF_TOKEN (it can write) is never sent from here."""
    if space != TRUSTED_SPACE:
        return False
    val = (os.environ.get("HF_READ_TOKEN") or "").strip()
    if not val:
        raise RuntimeError("Set HF_READ_TOKEN (a Read-Only token) before running chain; HF_TOKEN is never sent.")
    return val


def cmd_t2v(args):
    """Generate a pure Text-to-Video 2D anime action shot (no static image anchor)."""
    space = "mastaP/wan22-remix-sfw-t2v"
    client = Client(space, token=_load_token(space))
    res = client.predict(
        prompt=args.prompt,
        negative_prompt=args.negative or DEFAULT_NEG,
        seconds=args.seconds,
        steps=args.steps,
        guidance_scale=1.0,
        seed=args.seed,
        randomize_seed=(args.seed < 0),
        api_name="/generate_video",
    )
    video_path = res[0] if isinstance(res, (list, tuple)) else res
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    shutil.copyfile(video_path, args.out)
    print(f"Saved T2V shot: {args.out}")


def cmd_chain(args):
    """Extract the exact last frame of --prev and chain the next continuous shot."""
    token = _load_token(TRUSTED_SPACE)
    with tempfile.TemporaryDirectory() as tmp:
        anchor = os.path.join(tmp, "anchor.png")
        subprocess.run(
            ["ffmpeg", "-y", "-sseof", "-0.1", "-i", args.prev, "-update", "1", "-frames:v", "1", anchor],
            check=True,
        )
        client = Client(TRUSTED_SPACE, token=token)
        res = client.predict(
            input_image=handle_file(anchor),
            prompt=args.prompt,
            steps=args.steps,
            negative_prompt=args.negative or DEFAULT_NEG,
            duration_seconds=args.seconds,
            guidance_scale=1.0,
            guidance_scale_2=1.0,
            seed=args.seed if args.seed >= 0 else 42,
            randomize_seed=(args.seed < 0),
            api_name="/generate_video",
        )
    video_path = res[0]["video"] if isinstance(res[0], dict) else res[0]
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    shutil.copyfile(video_path, args.out)
    print(f"Saved chained shot: {args.out}")


def cmd_fx(args):
    """Apply anime camera shake and optional 2-frame inverted B&W impact flash."""
    vf = [f"scale=880:508,fps=24,crop=832:480:24+{args.shake}*sin(t*48):14+{int(args.shake*0.75)}*cos(t*53)"]
    if args.flash_at is not None:
        vf.append(f"negate=enable='between(t,{args.flash_at:.2f},{args.flash_at + 0.09:.2f})'")
    vf.append("setsar=1")
    subprocess.run(
        ["ffmpeg", "-y", "-i", args.inp, "-vf", ",".join(vf), "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", args.out],
        check=True,
    )
    print(f"Saved FX shot: {args.out}")


def main():
    p = argparse.ArgumentParser(description="2D Anime Sakuga & Continuity Pipeline (V2)")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_t2v = sub.add_parser("t2v", help="Pure Text-to-Video 2D anime burst")
    p_t2v.add_argument("--prompt", required=True)
    p_t2v.add_argument("--negative", default="")
    p_t2v.add_argument("--seconds", type=float, default=2.5)
    p_t2v.add_argument("--steps", type=int, default=6)
    p_t2v.add_argument("--seed", type=int, default=-1)
    p_t2v.add_argument("--out", required=True)
    p_t2v.set_defaults(func=cmd_t2v)

    p_ch = sub.add_parser("chain", help="Chain next shot from previous clip's last frame")
    p_ch.add_argument("--prev", required=True)
    p_ch.add_argument("--prompt", required=True)
    p_ch.add_argument("--negative", default="")
    p_ch.add_argument("--seconds", type=float, default=2.5)
    p_ch.add_argument("--steps", type=int, default=6)
    p_ch.add_argument("--seed", type=int, default=-1)
    p_ch.add_argument("--out", required=True)
    p_ch.set_defaults(func=cmd_chain)

    p_fx = sub.add_parser("fx", help="Add sakuga camera shake and impact flash")
    p_fx.add_argument("--in", dest="inp", required=True)
    p_fx.add_argument("--out", required=True)
    p_fx.add_argument("--flash-at", type=float, default=None)
    p_fx.add_argument("--shake", type=int, default=14)
    p_fx.set_defaults(func=cmd_fx)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
