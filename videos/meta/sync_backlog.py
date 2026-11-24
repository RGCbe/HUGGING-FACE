#!/usr/bin/env python3
"""
sync_backlog.py - Download and queue public YouTube Shorts to Facebook & Instagram

Fetches top-performing public YouTube Shorts, normalizes audio to Stereo AAC 48k,
staggers release times across 8:30 AM & 7:30 PM IST slots, and schedules them on Meta.
"""
import argparse
import datetime as dt
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

# Load .env.local
env_path = os.path.join(ROOT, ".env.local")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

import meta

def download_video(yt_id, out_path):
    url = f"https://www.youtube.com/watch?v={yt_id}"
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "-o", out_path,
        "--no-playlist",
        url
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not os.path.exists(out_path):
        raise RuntimeError(f"yt-dlp failed for {yt_id}: {res.stderr[:200]}")
    return out_path

def schedule_video(yt_id, publish_at_iso, dry_run=False):
    print(f"\n==========================================")
    print(f"Processing YouTube ID: {yt_id} -> Schedule for {publish_at_iso}")
    print(f"==========================================")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        raw_mp4 = os.path.join(tmpdir, f"raw_{yt_id}.mp4")
        norm_mp4 = os.path.join(tmpdir, f"norm_{yt_id}.mp4")
        
        print("  1. Downloading from YouTube...")
        download_video(yt_id, raw_mp4)
        print(f"     Downloaded ({os.path.getsize(raw_mp4):,} bytes)")
        
        print("  2. Normalizing audio for Instagram (Stereo AAC 48k + faststart)...")
        norm_file = meta.normalize_for_instagram(raw_mp4)
        print(f"     Normalized ({os.path.getsize(norm_file):,} bytes)")
        
        print("  3. Registering entry in Meta Queue...")
        import types
        q_args = types.SimpleNamespace(
            file=norm_file,
            youtube_id=yt_id,
            kind="short",
            publish_at=publish_at_iso,
            token_env=None,
            client_id_env=None,
            client_secret_env=None
        )
        meta.cmd_queue(q_args)
        
        print("  4. Running Meta dispatcher to schedule on Facebook Page...")
        run_args = types.SimpleNamespace(
            dry_run=dry_run,
            only=[yt_id]
        )
        meta.cmd_run(run_args)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Queue backlog YouTube video to Meta")
    p.add_argument("youtube_id", help="YouTube video ID")
    p.add_argument("--publish-at", required=True, help="ISO 8601 publish time (e.g. 2026-11-25T03:00:00Z)")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    
    schedule_video(args.youtube_id, args.publish_at, args.dry_run)
