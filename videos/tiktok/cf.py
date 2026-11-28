"""The Cloudflare API calls deploy.py and tiktok_queue.py share (standard library only).

The key is CF_WORKERS_TOKEN (a Cloudflare "Edit Cloudflare Workers" API token) and the account is CF_ACCOUNT_ID,
both from the cloud environment's settings. The key is never printed.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.cloudflare.com/client/v4"
WORKER = "tea-break-uploader"
NAMESPACE = "tea-break-uploader"
LEGAL = "https://rggroups-tea-break-uploader.static.hf.space"
MiB = 1024 * 1024


def env(name):
    v = os.environ.get(name, "").strip()
    if not v:
        sys.exit(f"{name} is not set: add it in the cloud environment's settings (a new session picks it up). "
                 "Never paste it into the chat.")
    return v


def account():
    return env("CF_ACCOUNT_ID")


def call(method, path, body=None, raw=None, content_type="application/json", ok404=False):
    data = raw if raw is not None else (None if body is None else json.dumps(body).encode())
    req = urllib.request.Request(API + path, data=data, method=method,
                                 headers={"Authorization": f"Bearer {env('CF_WORKERS_TOKEN')}", "Content-Type": content_type})
    try:
        r = urllib.request.urlopen(req, timeout=300).read()
    except urllib.error.HTTPError as e:
        detail = e.read()[:400].decode("utf-8", "replace")
        if ok404 and e.code == 404:
            return None
        sys.exit(f"Cloudflare {method} {path.split('?')[0]}: HTTP {e.code} {detail}")
    try:
        return json.loads(r)
    except ValueError:
        return r


def namespace_id(create=False):
    page = 1
    while True:
        r = call("GET", f"/accounts/{account()}/storage/kv/namespaces?per_page=100&page={page}")
        for ns in r["result"]:
            if ns["title"] == NAMESPACE:
                return ns["id"]
        if len(r["result"]) < 100:
            break
        page += 1
    if not create:
        sys.exit(f"no KV namespace {NAMESPACE!r} yet: run deploy.py first")
    return call("POST", f"/accounts/{account()}/storage/kv/namespaces", {"title": NAMESPACE})["result"]["id"]


def kv_put(ns, key, value: bytes, content_type="application/octet-stream"):
    call("PUT", f"/accounts/{account()}/storage/kv/namespaces/{ns}/values/{urllib.parse.quote(key, safe='')}",
         raw=value, content_type=content_type)


def kv_get(ns, key):
    req = urllib.request.Request(
        API + f"/accounts/{account()}/storage/kv/namespaces/{ns}/values/{urllib.parse.quote(key, safe='')}",
        headers={"Authorization": f"Bearer {env('CF_WORKERS_TOKEN')}"})
    try:
        return urllib.request.urlopen(req, timeout=120).read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def kv_delete(ns, key):
    call("DELETE", f"/accounts/{account()}/storage/kv/namespaces/{ns}/values/{urllib.parse.quote(key, safe='')}", ok404=True)


def kv_keys(ns, prefix=""):
    keys, cursor = [], ""
    while True:
        q = urllib.parse.urlencode({"prefix": prefix, "limit": 1000, **({"cursor": cursor} if cursor else {})})
        r = call("GET", f"/accounts/{account()}/storage/kv/namespaces/{ns}/keys?{q}")
        keys += [k["name"] for k in r["result"]]
        cursor = (r.get("result_info") or {}).get("cursor")
        if not cursor:
            return keys


def subdomain():
    r = call("GET", f"/accounts/{account()}/workers/subdomain", ok404=True)
    return (r or {}).get("result", {}).get("subdomain") if r else None


def base_url():
    sub = subdomain()
    if not sub:
        sys.exit("this Cloudflare account has no workers.dev address yet: open Workers & Pages once in the "
                 "Cloudflare dashboard (it creates one), then run this again")
    return f"https://{WORKER}.{sub}.workers.dev"
