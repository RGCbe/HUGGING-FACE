"""Mirror Tea Break with Manoj YouTube videos to the Facebook Page and Instagram.

    python3 videos/meta/meta.py check
    python3 videos/meta/meta.py queue YOUTUBE_ID FILE.mp4 [--kind short|long] [--token-env NAME]
                                      [--client-id-env NAME] [--client-secret-env NAME]
    python3 videos/meta/meta.py run [--dry-run] [--only YOUTUBE_ID]
    python3 videos/meta/meta.py status

check   read-only: the token's user, the Page, the Instagram link, Instagram's publishing quota and
        the token's expiry. Prints no keys.
queue   reads the video's title, description, publish time, privacy and language from YouTube and
        stores the mp4 and an entry (entries/ID.json) in the PRIVATE dataset config.json
        "queue_dataset". kind: short if the video is vertical and at most 90 s, else long.
run     posts every queued video that is not done yet:
        Facebook   a Short as a Page Reel, a full video as a Page video; scheduled for the YouTube
                   publish time when that is more than 15 minutes away, else published now.
        Instagram  a Reel, only once the YouTube publish time has passed (Instagram cannot schedule).
        Each platform is marked done in the entry, with its id, so nothing is posted twice; a
        failure is recorded and retried on the next run.
status  prints the queue.

Keys (environment only, never printed, logged or stored):
  META_PAGE_TOKEN  a long-lived user token of the "Tea Break Poster" app. The Page token is fetched
                   from it at run time and kept in memory. Meta keys go only to graph.facebook.com,
                   graph-video.facebook.com and rupload.facebook.com.
  HF_TOKEN         sent only to the owner's own Rggroups datasets.
  YT_*             the Tea Break YouTube login (read-only use here), sent only to Google.
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(HERE, "config.json")))
GV = CFG["graph_version"]
GRAPH = f"https://graph.facebook.com/{GV}"
GRAPH_VIDEO = f"https://graph-video.facebook.com/{GV}"


class MetaError(RuntimeError):
    pass


def now():
    return dt.datetime.now(dt.timezone.utc)


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_time(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


# ---------------------------------------------------------------- Meta HTTP (keys only to Meta hosts)

def user_token():
    t = os.environ.get(CFG["token_env"], "").strip()
    if not t:
        sys.exit(f"{CFG['token_env']} is not set")
    return t


def _scrub(text, *tokens):
    for t in tokens:
        if t:
            text = text.replace(t, "<key>")
    return text


def meta_request(method, url, token, params=None, body=None, headers=None, auth="Bearer", timeout=300):
    host = urllib.parse.urlparse(url).hostname
    if host not in CFG["meta_hosts"]:
        raise MetaError(f"refusing to send a Meta key to {host}")
    data = None
    h = {"Authorization": f"{auth} {token}"}
    h.update(headers or {})
    if params is not None and method == "GET":
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    elif params is not None:
        data = urllib.parse.urlencode(params).encode()
        h["Content-Type"] = "application/x-www-form-urlencoded"
    if body is not None:
        data = body
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        try:
            j = json.loads(raw)
            err = j.get("error") or {}
            if err:
                msg = f"{err.get('type', '')} {err.get('code', '')}/{err.get('error_subcode', '')}: " \
                      f"{err.get('error_user_msg') or err.get('message', '')}"
            else:  # rupload answers with {"debug_info": {...}} instead
                msg = json.dumps(j, ensure_ascii=False)[:500]
        except ValueError:
            msg = raw[:500]
        raise MetaError(_scrub(f"HTTP {e.code} from {host}{urllib.parse.urlparse(url).path}: {msg}", token)) from None
    except urllib.error.URLError as e:
        raise MetaError(f"network error talking to {host}: {e.reason}") from None
    try:
        return json.loads(raw)
    except ValueError:
        return {"raw": raw[:300]}


def graph(method, path, token, **params):
    return meta_request(method, f"{GRAPH}/{path.lstrip('/')}", token, params=params)


def page_token(utok):
    d = graph("GET", CFG["page_id"], utok, fields="access_token,name")
    if not d.get("access_token"):
        raise MetaError("no Page token came back: is the user still an admin of the Page?")
    return d["access_token"]


# ---------------------------------------------------------------- Hugging Face queue (private dataset)

def hf():
    from huggingface_hub import HfApi
    tok = os.environ.get("HF_TOKEN", "").strip()
    if not tok:
        sys.exit("HF_TOKEN is not set")
    repo = CFG["queue_dataset"]
    if repo.split("/")[0] != CFG["dataset_owner"]:
        sys.exit(f"queue dataset {repo} is not the owner's")
    return HfApi(token=tok), repo


def ensure_private(api, repo, create=False):
    from huggingface_hub.errors import RepositoryNotFoundError
    try:
        info = api.repo_info(repo, repo_type="dataset")
    except RepositoryNotFoundError:
        if not create:
            sys.exit(f"queue dataset {repo} does not exist yet: queue a video first")
        api.create_repo(repo, repo_type="dataset", private=True)
        info = api.repo_info(repo, repo_type="dataset")
    if not info.private:
        sys.exit(f"refusing: {repo} is not private")


def read_entry(api, repo, yid):
    from huggingface_hub.errors import EntryNotFoundError
    try:
        with tempfile.TemporaryDirectory() as d:
            p = api.hf_hub_download(repo, f"entries/{yid}.json", repo_type="dataset", local_dir=d,
                                    force_download=True)
            return json.load(open(p))
    except EntryNotFoundError:
        return None


def write_entry(api, repo, e, msg):
    e["updated_at"] = iso(now())
    api.upload_file(path_or_fileobj=json.dumps(e, indent=1, ensure_ascii=False).encode(),
                    path_in_repo=f"entries/{e['youtube_id']}.json", repo_id=repo, repo_type="dataset",
                    commit_message=msg)


def list_entries(api, repo):
    ids = sorted(f[len("entries/"):-5] for f in api.list_repo_files(repo, repo_type="dataset")
                 if f.startswith("entries/") and f.endswith(".json"))
    return [read_entry(api, repo, i) for i in ids]


# ---------------------------------------------------------------- YouTube (read-only)

def youtube_video(yid, token_env, id_env, secret_env):
    sys.path.insert(0, os.path.join(HERE, "..", "doodle"))
    from upload import access_token  # videos/doodle/upload.py
    tok = access_token(token_env, id_env, secret_env)
    req = urllib.request.Request(
        "https://www.googleapis.com/youtube/v3/videos?" + urllib.parse.urlencode(
            {"part": "snippet,status,contentDetails", "id": yid}),
        headers={"Authorization": f"Bearer {tok}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        items = json.load(r).get("items", [])
    if not items:
        raise SystemExit(f"YouTube video {yid} not found on this channel")
    v = items[0]
    sn, st = v["snippet"], v["status"]
    privacy = st.get("privacyStatus")
    publish_at = st.get("publishAt") if privacy == "private" else sn.get("publishedAt")
    return {"title": sn.get("title", ""), "description": sn.get("description", ""),
            "language": sn.get("defaultAudioLanguage") or sn.get("defaultLanguage") or "",
            "privacy": privacy, "publish_at": publish_at, "channel": sn.get("channelTitle", "")}


def yt_publish_state(info):
    """(time it is or goes public, or None if it is not set to go public)."""
    if info["privacy"] == "public":
        return parse_time(info["publish_at"]) or now()
    if info["privacy"] == "private" and info.get("publish_at"):
        return parse_time(info["publish_at"])
    return None


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:stream_side_data=rotation:format=duration", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    s = d["streams"][0]
    w, h = s["width"], s["height"]
    rot = next((abs(int(x.get("rotation", 0))) for x in s.get("side_data_list", []) if "rotation" in x), 0)
    if rot in (90, 270):
        w, h = h, w
    return {"width": w, "height": h, "duration": float(d["format"]["duration"])}


# ---------------------------------------------------------------- captions

def clean_text(title, description):
    title = " ".join(w for w in title.split() if w.lower() != "#shorts").strip()
    lines = [l for l in description.splitlines()
             if not any(l.strip().startswith(p) for p in CFG["drop_description_lines"])]
    body = "\n".join(lines).strip()
    while "\n\n\n" in body:
        body = body.replace("\n\n\n", "\n\n")
    return title, body


def fb_caption(e):
    title, body = clean_text(e["title"], e["description"])
    link = f"https://youtu.be/{e['youtube_id']}"
    parts = [title, body] if body else [title]
    text = "\n\n".join(parts)
    if link not in text:
        text += f"\n\n{link}"
    return text


def ig_caption(e):
    import re
    title, body = clean_text(e["title"], e["description"])
    body = re.sub(r"\S*(https?://|youtu\.be/|www\.)\S*", "", body)
    body = "\n".join(l.rstrip() for l in body.splitlines()).strip()
    text = "\n\n".join(p for p in (title, body) if p)
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    seen = 0

    def keep(m):
        nonlocal seen
        seen += 1
        return m.group(0) if seen <= CFG["ig_hashtags_max"] else ""
    text = re.sub(r"#\w+", keep, text)
    limit = CFG["ig_caption_max"]
    if len(text) > limit:
        text = text[:limit - 1].rsplit(" ", 1)[0] + "…"
    return text.strip()


# ---------------------------------------------------------------- Facebook

def fb_when(e):
    pub = parse_time(e["publish_at"])
    if pub and pub > now() + dt.timedelta(minutes=CFG["schedule_min_minutes"]):
        return int(pub.timestamp())
    return None


def fb_post_reel(ptok, e, path):
    size = os.path.getsize(path)
    start = graph("POST", f"{CFG['page_id']}/video_reels", ptok, upload_phase="start")
    vid = start["video_id"]
    yield {"video_id": vid, "status": "uploading"}
    up = meta_request("POST", start.get("upload_url") or f"https://rupload.facebook.com/video-upload/{GV}/{vid}",
                      ptok, body=open(path, "rb").read(), auth="OAuth",
                      headers={"offset": "0", "file_size": str(size), "Content-Type": "application/octet-stream"},
                      timeout=1800)
    if not up.get("success"):
        raise MetaError(f"Reel upload did not succeed: {up}")
    when = fb_when(e)
    params = {"upload_phase": "finish", "video_id": vid, "description": fb_caption(e),
              "video_state": "SCHEDULED" if when else "PUBLISHED"}
    if when:
        params["scheduled_publish_time"] = str(when)
    fin = graph("POST", f"{CFG['page_id']}/video_reels", ptok, **params)
    if not fin.get("success"):
        raise MetaError(f"Reel finish did not succeed: {fin}")
    yield {"video_id": vid, "status": "scheduled" if when else "published",
           "scheduled_for": iso(dt.datetime.fromtimestamp(when, dt.timezone.utc)) if when else None}


def _multipart(fields, file_field=None, chunk=None):
    b = uuid.uuid4().hex
    out = []
    for k, v in fields.items():
        out.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    if file_field:
        out.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{file_field}\"; filename=\"chunk\"\r\n"
                   f"Content-Type: application/octet-stream\r\n\r\n".encode() + chunk + b"\r\n")
    out.append(f"--{b}--\r\n".encode())
    return b"".join(out), f"multipart/form-data; boundary={b}"


def fb_post_video(ptok, e, path):
    """A full video as a Page video (resumable upload on graph-video.facebook.com)."""
    size = os.path.getsize(path)
    url = f"{GRAPH_VIDEO}/{CFG['page_id']}/videos"
    start = meta_request("POST", url, ptok, params={"upload_phase": "start", "file_size": str(size)})
    sid, vid = start["upload_session_id"], start["video_id"]
    yield {"video_id": vid, "status": "uploading"}
    s, end = int(start["start_offset"]), int(start["end_offset"])
    with open(path, "rb") as f:
        while s < end:
            f.seek(s)
            body, ctype = _multipart({"upload_phase": "transfer", "upload_session_id": sid, "start_offset": str(s)},
                                     "video_file_chunk", f.read(end - s))
            r = meta_request("POST", url, ptok, body=body, headers={"Content-Type": ctype}, timeout=1800)
            s, end = int(r["start_offset"]), int(r["end_offset"])
    when = fb_when(e)
    title, _ = clean_text(e["title"], "")
    params = {"upload_phase": "finish", "upload_session_id": sid, "title": title[:255], "description": fb_caption(e)}
    if when:
        params.update(published="false", scheduled_publish_time=str(when))
    fin = meta_request("POST", url, ptok, params=params)
    if not fin.get("success"):
        raise MetaError(f"video finish did not succeed: {fin}")
    yield {"video_id": vid, "status": "scheduled" if when else "published",
           "scheduled_for": iso(dt.datetime.fromtimestamp(when, dt.timezone.utc)) if when else None}


def fb_video_info(ptok, vid):
    return graph("GET", vid, ptok, fields="id,permalink_url,status,published,scheduled_publish_time,created_time,source")


def fb_already_done(ptok, vid):
    """True if an earlier, interrupted run already finished (published or scheduled) this Facebook video."""
    try:
        d = fb_video_info(ptok, vid)
    except MetaError:
        return False
    pub = ((d.get("status") or {}).get("publishing_phase") or {}).get("publish_status")
    return bool(d.get("published") or d.get("scheduled_publish_time") or pub in ("published", "scheduled"))


# ---------------------------------------------------------------- Instagram

def ig_post_reel(utok, e, path, fb_source=None):
    """A Reel by resumable upload; if Instagram's upload server refuses the bytes, Instagram fetches the
    already-posted Facebook copy instead (fb_source: a function that returns its fbcdn address)."""
    ig = CFG["ig_user_id"]
    c = graph("POST", f"{ig}/media", utok, media_type="REELS", upload_type="resumable",
              caption=ig_caption(e), share_to_feed="true")
    cid, uri = c["id"], c.get("uri")
    yield {"container_id": cid, "status": "uploading"}
    if not uri or urllib.parse.urlparse(uri).hostname != "rupload.facebook.com":
        raise MetaError("unexpected upload address for the Instagram Reel")
    try:
        up = meta_request("POST", uri, utok, body=open(path, "rb").read(), auth="OAuth", timeout=1800,
                          headers={"offset": "0", "file_size": str(os.path.getsize(path)),
                                   "Content-Type": "application/octet-stream"})
        if up.get("success") is False:
            raise MetaError(f"Instagram upload did not succeed: {up}")
        ig_wait(utok, cid)
    except MetaError as x:
        src = fb_source() if fb_source else None
        if not src or urllib.parse.urlparse(src).hostname.split(".")[-2:] != ["fbcdn", "net"]:
            raise
        print(f"  Instagram upload refused ({x}); letting Instagram fetch the Facebook copy")
        c = graph("POST", f"{ig}/media", utok, media_type="REELS", video_url=src,
                  caption=ig_caption(e), share_to_feed="true")
        cid = c["id"]
        yield {"container_id": cid, "status": "uploading", "via": "facebook copy"}
        ig_wait(utok, cid)
    m = graph("POST", f"{ig}/media_publish", utok, creation_id=cid)
    yield {"container_id": cid, "media_id": m["id"], "status": "published"}


def ig_wait(utok, cid, limit=900):
    t0 = time.time()
    while True:
        s = graph("GET", cid, utok, fields="status_code,status")
        code = s.get("status_code")
        if code in ("FINISHED", "PUBLISHED"):
            return code
        if code in ("ERROR", "EXPIRED"):
            raise MetaError(f"Instagram could not process the video: {code} {s.get('status', '')}")
        if time.time() - t0 > limit:
            raise MetaError(f"Instagram still processing after {limit} s ({code}); will retry next run")
        time.sleep(10)


def ig_find_published(utok, cid, caption):
    """An interrupted run may have published the container already: find that post instead of posting again."""
    try:
        if graph("GET", cid, utok, fields="status_code").get("status_code") != "PUBLISHED":
            return None
    except MetaError:
        return None
    media = graph("GET", f"{CFG['ig_user_id']}/media", utok, fields="id,caption,timestamp", limit="25")
    for m in media.get("data", []):
        if (m.get("caption") or "").strip() == caption.strip():
            return m["id"]
    return "unknown"


# ---------------------------------------------------------------- commands

def cmd_check(_):
    utok = user_token()
    ok = True
    me = graph("GET", "me", utok, fields="id,name")
    print(f"user: {me.get('name')} ({me.get('id')})")
    dbg = graph("GET", "debug_token", utok, input_token=utok).get("data", {})
    exp = dbg.get("expires_at", 0)
    dax = dbg.get("data_access_expires_at", 0)
    print(f"token: valid={dbg.get('is_valid')} app={dbg.get('application')} ({dbg.get('app_id')}) type={dbg.get('type')}")
    print(f"  expires: {'never' if not exp else iso(dt.datetime.fromtimestamp(exp, dt.timezone.utc))}; "
          f"data access until {iso(dt.datetime.fromtimestamp(dax, dt.timezone.utc)) if dax else '?'}")
    need = {"pages_show_list", "pages_read_engagement", "pages_manage_posts", "publish_video",
            "instagram_basic", "instagram_content_publish"}
    missing = need - set(dbg.get("scopes", []))
    print(f"  scopes needed: {'all present' if not missing else 'MISSING ' + ', '.join(sorted(missing))}")
    ok &= bool(dbg.get("is_valid")) and not missing and str(dbg.get("app_id")) == CFG["app_id"]
    if dax and dax < time.time() + 14 * 86400:
        print("  WARNING: data access ends within 14 days: the owner must log in to the app again")
    page = graph("GET", CFG["page_id"], utok, fields="id,name,instagram_business_account{id,username}")
    igb = page.get("instagram_business_account") or {}
    print(f"page: {page.get('name')} ({page.get('id')}); Instagram: @{igb.get('username')} ({igb.get('id')})")
    ok &= igb.get("id") == CFG["ig_user_id"]
    ptok = page_token(utok)
    print("page token: fetched (kept in memory)")
    del ptok
    lim = graph("GET", f"{CFG['ig_user_id']}/content_publishing_limit", utok, fields="config,quota_usage")
    d = (lim.get("data") or [{}])[0]
    print(f"instagram publishing: {d.get('quota_usage')} of {(d.get('config') or {}).get('quota_total')} used in 24 h")
    print("CHECK PASSED" if ok else "CHECK FAILED")
    sys.exit(0 if ok else 1)


def cmd_queue(a):
    if not os.path.isfile(a.file):
        sys.exit(f"no such file: {a.file}")
    yc = CFG["youtube"]
    info = youtube_video(a.youtube_id, a.token_env or yc["refresh_token_env"],
                         a.client_id_env or yc["client_id_env"], a.client_secret_env or yc["client_secret_env"])
    p = probe(a.file)
    kind = a.kind or ("short" if p["height"] > p["width"] and p["duration"] <= CFG["short_max_seconds"] else "long")
    if p["duration"] > 900:
        print("  note: longer than 15 minutes: Instagram will refuse it as a Reel")
    api, repo = hf()
    ensure_private(api, repo, create=True)
    old = read_entry(api, repo, a.youtube_id) or {}
    e = {"youtube_id": a.youtube_id, "url": f"https://youtu.be/{a.youtube_id}", "kind": kind,
         "video": f"videos/{a.youtube_id}.mp4", **info, **p,
         "queued_at": old.get("queued_at", iso(now())),
         "facebook": old.get("facebook", {"status": "pending"}),
         "instagram": old.get("instagram", {"status": "pending"})}
    if old.get("video") and old.get("size") == os.path.getsize(a.file):
        print("  video already stored")
    else:
        api.upload_file(path_or_fileobj=a.file, path_in_repo=e["video"], repo_id=repo, repo_type="dataset",
                        commit_message=f"video for {a.youtube_id}")
    e["size"] = os.path.getsize(a.file)
    write_entry(api, repo, e, f"queue {a.youtube_id}")
    print(f"queued {a.youtube_id} ({kind}, {p['width']}x{p['height']}, {p['duration']:.0f} s, {info['language']}, "
          f"{info['privacy']}, public at {info['publish_at']}): {info['title']}")


def refresh_from_youtube(e):
    yc = CFG["youtube"]
    if not all(os.environ.get(yc[k]) for k in ("refresh_token_env", "client_id_env", "client_secret_env")):
        return False
    try:
        info = youtube_video(e["youtube_id"], yc["refresh_token_env"], yc["client_id_env"], yc["client_secret_env"])
    except (urllib.error.URLError, SystemExit, KeyError) as x:
        print(f"  (could not re-read YouTube, using the stored times: {x})")
        return False
    changed = any(e.get(k) != info[k] for k in ("privacy", "publish_at"))
    e.update({k: info[k] for k in ("privacy", "publish_at")})
    return changed


def cmd_run(a):
    utok = user_token()
    api, repo = hf()
    ensure_private(api, repo)
    ptok = None
    failed = 0
    entries = [e for e in list_entries(api, repo) if e and (not a.only or e["youtube_id"] in a.only)]
    for e in entries:
        yid = e["youtube_id"]
        fb, ig = e.get("facebook", {}), e.get("instagram", {})
        if fb.get("status") in ("published", "scheduled") and ig.get("status") == "published":
            continue
        refresh_from_youtube(e)
        pub = yt_publish_state(e)
        print(f"\n{yid} ({e['kind']}, {e.get('language')}): {e['title']}")
        if pub is None:
            print(f"  not set to go public on YouTube ({e.get('privacy')}): waiting")
            continue
        print(f"  YouTube public at {iso(pub)}")
        path = None

        def video_file():
            nonlocal path
            if not path:
                d = tempfile.mkdtemp(prefix="meta-")
                path = api.hf_hub_download(repo, e["video"], repo_type="dataset", local_dir=d)
            return path

        # Facebook
        if fb.get("status") not in ("published", "scheduled"):
            if fb.get("video_id") and fb.get("status") in ("uploading", "failed"):
                ptok = ptok or page_token(utok)
                if fb_already_done(ptok, fb["video_id"]):
                    fb["status"] = "published" if not fb.get("scheduled_for") else "scheduled"
                    print(f"  Facebook: an earlier run already finished {fb['video_id']}")
            if fb.get("status") not in ("published", "scheduled"):
                when = fb_when(e)
                what = "Reel" if e["kind"] == "short" else "video"
                print(f"  Facebook {what}: " + (f"schedule for {iso(dt.datetime.fromtimestamp(when, dt.timezone.utc))}"
                                                 if when else "publish now"))
                if not a.dry_run:
                    try:
                        ptok = ptok or page_token(utok)
                        post = fb_post_reel if e["kind"] == "short" else fb_post_video
                        for step in post(ptok, e, video_file()):
                            fb = e["facebook"] = {**step, "at": iso(now()), "type": what.lower()}
                            write_entry(api, repo, e, f"facebook {step['status']} {yid}")
                        info = fb_video_info(ptok, fb["video_id"])
                        fb["permalink"] = info.get("permalink_url") and (
                            "https://www.facebook.com" + info["permalink_url"]
                            if info["permalink_url"].startswith("/") else info["permalink_url"])
                        write_entry(api, repo, e, f"facebook link {yid}")
                        print(f"  Facebook {fb['status']}: {fb['video_id']} {fb.get('permalink') or ''}")
                    except (MetaError, KeyError) as x:
                        failed += 1
                        fb = e["facebook"] = {**e.get("facebook", {}), "status": "failed", "error": str(x)[:500],
                                              "at": iso(now())}
                        write_entry(api, repo, e, f"facebook failed {yid}")
                        print(f"  Facebook FAILED: {x}")

        # Instagram
        if ig.get("status") != "published":
            if pub > now():
                print(f"  Instagram: waits until {iso(pub)} (Instagram cannot schedule)")
            else:
                print("  Instagram Reel: publish now")
                if not a.dry_run:
                    try:
                        if ig.get("container_id"):
                            mid = ig_find_published(utok, ig["container_id"], ig_caption(e))
                            if mid:
                                ig = e["instagram"] = {**ig, "status": "published", "media_id": mid}
                                print(f"  Instagram: an earlier run already published it ({mid})")
                        if ig.get("status") != "published":
                            fbv = e.get("facebook", {}).get("video_id") if e.get("facebook", {}).get(
                                "status") in ("published", "scheduled") else None

                            def fb_source():
                                nonlocal ptok
                                if not fbv:
                                    return None
                                ptok = ptok or page_token(utok)
                                return fb_video_info(ptok, fbv).get("source")
                            for step in ig_post_reel(utok, e, video_file(), fb_source):
                                ig = e["instagram"] = {**step, "at": iso(now())}
                                write_entry(api, repo, e, f"instagram {step['status']} {yid}")
                        if ig.get("media_id") not in (None, "unknown"):
                            ig["permalink"] = graph("GET", ig["media_id"], utok, fields="permalink").get("permalink")
                        write_entry(api, repo, e, f"instagram link {yid}")
                        print(f"  Instagram published: {ig.get('media_id')} {ig.get('permalink') or ''}")
                    except (MetaError, KeyError) as x:
                        failed += 1
                        ig = e["instagram"] = {**e.get("instagram", {}), "status": "failed", "error": str(x)[:500],
                                               "at": iso(now())}
                        write_entry(api, repo, e, f"instagram failed {yid}")
                        print(f"  Instagram FAILED: {x}")
    if a.dry_run:
        print("\nDry run: nothing was posted.")
    sys.exit(1 if failed else 0)


def cmd_status(_):
    api, repo = hf()
    ensure_private(api, repo)
    for e in list_entries(api, repo):
        if not e:
            continue
        fb, ig = e.get("facebook", {}), e.get("instagram", {})
        print(f"{e['youtube_id']} {e['kind']:5} {e.get('language', ''):3} public {e.get('publish_at')} | "
              f"FB {fb.get('status')} {fb.get('permalink') or fb.get('video_id') or ''} | "
              f"IG {ig.get('status')} {ig.get('permalink') or ig.get('media_id') or ''} | {e['title'][:50]}")


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    q = sub.add_parser("queue")
    q.add_argument("youtube_id")
    q.add_argument("file")
    q.add_argument("--kind", choices=["short", "long"])
    q.add_argument("--token-env")
    q.add_argument("--client-id-env")
    q.add_argument("--client-secret-env")
    r = sub.add_parser("run")
    r.add_argument("--dry-run", action="store_true")
    r.add_argument("--only", nargs="*")
    sub.add_parser("status")
    a = p.parse_args()
    {"check": cmd_check, "queue": cmd_queue, "run": cmd_run, "status": cmd_status}[a.cmd](a)


if __name__ == "__main__":
    main()
