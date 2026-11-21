"""The private drop box (a Cloudflare Worker + KV namespace "gs-dropbox") that GridShare machines use for files.

    python3 dropbox.py deploy             create or update the Worker; make a new secret key if there is none
    python3 dropbox.py url                print nothing secret: only whether the drop box answers
    python3 dropbox.py teardown           delete the Worker and its KV namespace (all files in it)

As a module: base() gives the drop box's address with its key (keep it out of logs and git), put(name, bytes),
get(name), names(prefix). The key lives only in ~/.cache/gs-dropbox.key (outside git) and in the Worker's secret.
Uses CF_ACCOUNT_ID and CF_WORKERS_TOKEN, like videos/tiktok/deploy.py.
"""
import json
import os
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://api.cloudflare.com/client/v4"
NAME = "gs-dropbox"
KEY_FILE = os.path.expanduser("~/.cache/gs-dropbox.key")
UA = {"User-Agent": "gs-dropbox-client/1.0"}  # Cloudflare refuses Python's default User-Agent (403)


def env(name):
    v = os.environ.get(name, "").strip()
    if not v:
        sys.exit(f"{name} is not set (cloud environment settings)")
    return v


def call(method, path, body=None, raw=None, content_type="application/json", ok404=False):
    data = raw if raw is not None else (None if body is None else json.dumps(body).encode())
    req = urllib.request.Request(API + path, data=data, method=method,
                                 headers={"Authorization": f"Bearer {env('CF_WORKERS_TOKEN')}", "Content-Type": content_type})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=120).read())
    except urllib.error.HTTPError as e:
        if ok404 and e.code == 404:
            return None
        sys.exit(f"Cloudflare {method} {path.split('?')[0]}: HTTP {e.code} {e.read()[:300].decode('utf-8', 'replace')}")


def acct():
    return env("CF_ACCOUNT_ID")


def namespace(create=False):
    r = call("GET", f"/accounts/{acct()}/storage/kv/namespaces?per_page=100")
    for ns in r["result"]:
        if ns["title"] == NAME:
            return ns["id"]
    if create:
        return call("POST", f"/accounts/{acct()}/storage/kv/namespaces", {"title": NAME})["result"]["id"]
    return None


def key():
    if not os.path.exists(KEY_FILE):
        sys.exit("no drop box key: run dropbox.py deploy first")
    return open(KEY_FILE).read().strip()


def base():
    sub = call("GET", f"/accounts/{acct()}/workers/subdomain")["result"]["subdomain"]
    return f"https://{NAME}.{sub}.workers.dev/{key()}"


def deploy():
    os.makedirs(os.path.dirname(KEY_FILE), exist_ok=True)
    if not os.path.exists(KEY_FILE):
        with open(os.open(KEY_FILE, os.O_WRONLY | os.O_CREAT, 0o600), "w") as f:
            f.write(secrets.token_hex(24))
    ns = namespace(create=True)
    meta = {"main_module": "worker.js", "compatibility_date": "2026-10-01",
            "bindings": [{"type": "kv_namespace", "name": "DROP", "namespace_id": ns},
                         {"type": "secret_text", "name": "DROP_KEY", "text": key()}]}
    b = uuid.uuid4().hex
    script = open(os.path.join(HERE, "dropbox_worker.js"), "rb").read()
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"metadata\"; filename=\"metadata.json\"\r\n"
            f"Content-Type: application/json\r\n\r\n{json.dumps(meta)}\r\n"
            f"--{b}\r\nContent-Disposition: form-data; name=\"worker.js\"; filename=\"worker.js\"\r\n"
            f"Content-Type: application/javascript+module\r\n\r\n").encode() + script + f"\r\n--{b}--\r\n".encode()
    call("PUT", f"/accounts/{acct()}/workers/scripts/{NAME}", raw=body, content_type=f"multipart/form-data; boundary={b}")
    call("POST", f"/accounts/{acct()}/workers/scripts/{NAME}/subdomain", {"enabled": True, "previews_enabled": False})
    print("deployed the drop box worker")


def put(name, data: bytes, content_type="application/octet-stream"):
    req = urllib.request.Request(f"{base()}/files/{urllib.parse.quote(name)}", data=data, method="PUT",
                                 headers={"Content-Type": content_type, **UA})
    urllib.request.urlopen(req, timeout=300).read()


def get(name):
    try:
        return urllib.request.urlopen(urllib.request.Request(f"{base()}/files/{urllib.parse.quote(name)}", headers=UA), timeout=300).read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def names(prefix=""):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"{base()}/list?prefix={urllib.parse.quote(prefix)}", headers=UA), timeout=60).read())


def teardown():
    call("DELETE", f"/accounts/{acct()}/workers/scripts/{NAME}", ok404=True)
    ns = namespace()
    if ns:
        call("DELETE", f"/accounts/{acct()}/storage/kv/namespaces/{ns}", ok404=True)
    if os.path.exists(KEY_FILE):
        os.remove(KEY_FILE)
    print("deleted the drop box worker, its files and its key")


if __name__ == "__main__":
    cmd = sys.argv[1:2] or ["url"]
    if cmd == ["deploy"]:
        deploy()
    elif cmd == ["teardown"]:
        teardown()
    else:
        put("ping.txt", b"pong")
        print("drop box answers:", get("ping.txt") == b"pong", "| files:", len(names()))
