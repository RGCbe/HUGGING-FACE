"""Put a finished vertical video in the Tea Break Uploader's queue, so the owner can send it to his TikTok inbox.

    python3 tiktok_queue.py add VIDEO.mp4 --name pig-war --title "The Pig War (1859)" --caption "In 1859, ..."
    python3 tiktok_queue.py list
    python3 tiktok_queue.py remove pig-war

The video is stored in the Worker's KV namespace as TikTok's own upload chunks (one KV value per chunk, each at
most 24 MiB, as TikTok's Media Transfer Guide asks: chunks of 5-64 MB, the last one up to twice the chunk size),
so the Worker can send each chunk with a single read. The Worker deletes the chunks once TikTok has the video.
Videos have the owner's voice, so they go only here (private) and to his TikTok inbox, never into the repo.
"""
import argparse
import json
import os
import re
import sys

import cf

MAX_SINGLE = 24 * cf.MiB  # a video up to this size goes in one chunk (TikTok allows up to 64 MB; KV values up to 25 MiB)
CHUNK = 12 * cf.MiB       # otherwise 12 MiB chunks, so the last one (up to 2 x 12 MiB) still fits in one KV value


def plan(size):
    if size <= MAX_SINGLE:
        return size, 1
    return CHUNK, size // CHUNK


def add(a):
    if not re.fullmatch(r"[a-z0-9-]{1,60}", a.name):
        sys.exit("--name: lowercase letters, digits and dashes only")
    ns = cf.namespace_id()
    size = os.path.getsize(a.video)
    chunk, count = plan(size)
    with open(a.video, "rb") as f:
        for k in range(count):
            part = f.read(chunk) if k < count - 1 else f.read()
            cf.kv_put(ns, f"v:{a.name}:{k}", part)
            print(f"  part {k + 1}/{count}: {len(part) / cf.MiB:.1f} MiB", flush=True)
    meta = {"title": a.title, "caption": a.caption, "size": size, "chunk": chunk, "count": count}
    cf.kv_put(ns, f"q:{a.name}", json.dumps(meta, ensure_ascii=False).encode(), "application/json")
    cf.kv_delete(ns, f"sent:{a.name}")
    print(f"queued {a.name}: {size / cf.MiB:.1f} MiB in {count} chunk(s); send it from {cf.base_url()}/")


def show(_):
    ns = cf.namespace_id()
    for key in cf.kv_keys(ns, "q:"):
        name = key[2:]
        meta = json.loads(cf.kv_get(ns, key) or b"{}")
        sent = cf.kv_get(ns, f"sent:{name}")
        print(f"{name}: {meta.get('title')} ({meta.get('size', 0) / cf.MiB:.0f} MiB) "
              f"{'sent ' + json.loads(sent).get('status', '') if sent else 'waiting'}")


def remove(a):
    ns = cf.namespace_id()
    for key in [f"q:{a.name}", f"sent:{a.name}"] + cf.kv_keys(ns, f"v:{a.name}:"):
        cf.kv_delete(ns, key)
    print(f"removed {a.name}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("add")
    p.add_argument("video")
    p.add_argument("--name", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--caption", required=True)
    sub.add_parser("list")
    p = sub.add_parser("remove")
    p.add_argument("name")
    a = ap.parse_args()
    {"add": add, "list": show, "remove": remove}[a.cmd](a)


if __name__ == "__main__":
    main()
