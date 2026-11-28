"""Put the Tea Break Uploader (worker.js) online as a Cloudflare Worker, or update it.

    python3 deploy.py [--verify TIKTOK_SIGNATURE_FILE]

Creates the KV namespace if needed, uploads worker.js with its bindings (the KV namespace, BASE_URL, LEGAL_URL),
keeps the secrets the owner added in the Cloudflare dashboard (TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET), and
turns on its workers.dev address. --verify serves TikTok's URL-prefix signature file (tiktokXXXX.txt) at the
site's root, for "Verify URL properties" in the TikTok developer portal.
"""
import argparse
import json
import os
import uuid

import cf

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", help="TikTok's signature file for the URL-prefix check")
    a = ap.parse_args()
    base = cf.base_url()
    ns = cf.namespace_id(create=True)
    bindings = [{"type": "kv_namespace", "name": "TB", "namespace_id": ns},
                {"type": "plain_text", "name": "BASE_URL", "text": base},
                {"type": "plain_text", "name": "LEGAL_URL", "text": cf.LEGAL}]
    if a.verify:
        content = open(a.verify, encoding="utf-8").read().strip()
        name = os.path.basename(a.verify)
        name = name[name.index("tiktok"):] if "tiktok" in name else name  # uploads may get a prefix
        bindings.append({"type": "plain_text", "name": "TIKTOK_VERIFY", "text": f"{name}={content}"})
        print(f"serving {base}/{name}")
    meta = {"main_module": "worker.js", "compatibility_date": "2026-10-01", "bindings": bindings,
            "keep_bindings": ["secret_text"]}
    boundary = uuid.uuid4().hex
    script = open(os.path.join(HERE, "worker.js"), "rb").read()
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"metadata\"; filename=\"metadata.json\"\r\n"
            f"Content-Type: application/json\r\n\r\n{json.dumps(meta)}\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"worker.js\"; filename=\"worker.js\"\r\n"
            f"Content-Type: application/javascript+module\r\n\r\n").encode() + script + f"\r\n--{boundary}--\r\n".encode()
    cf.call("PUT", f"/accounts/{cf.account()}/workers/scripts/{cf.WORKER}", raw=body,
            content_type=f"multipart/form-data; boundary={boundary}")
    cf.call("POST", f"/accounts/{cf.account()}/workers/scripts/{cf.WORKER}/subdomain",
            {"enabled": True, "previews_enabled": False})
    print(f"deployed: {base}/ (redirect URI {base}/callback)")


if __name__ == "__main__":
    main()
