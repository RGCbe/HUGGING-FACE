"""Upload a finished video (and its Shorts) to YouTube with all the details filled in.

    python3 upload.py UPLOAD_JSON [--dry-run]

Reads the title, description, tags, category, audience, AI-content label and thumbnail from
UPLOAD_JSON and uploads each file with the YouTube Data API (resumable upload, standard library
only). Videos go up as PRIVATE unless the JSON says otherwise, so you can watch them in YouTube
Studio before anyone else sees them. Google also keeps API uploads private on new API projects
until the project passes its audit.

Credentials come from environment variables, never from the repo:
  YT_CLIENT_ID, YT_CLIENT_SECRET   an OAuth client from your Google Cloud project
  YT_REFRESH_TOKEN                 a refresh token for your channel, scope youtube.upload
Without them (or with --dry-run) nothing is sent; it prints what it would upload.
File paths in UPLOAD_JSON may use environment variables, e.g. "$OUT_DIR/video.mp4".
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://www.googleapis.com/upload/youtube/v3"
CHUNK = 8 * 1024 * 1024


def access_token():
    body = urllib.parse.urlencode({
        "client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", data=body, timeout=60) as r:
        return json.load(r)["access_token"]


def metadata(v, defaults):
    d = dict(defaults, **v)
    status = {
        "privacyStatus": d.get("privacy", "private"),
        "selfDeclaredMadeForKids": d.get("made_for_kids", False),
        "containsSyntheticMedia": d.get("ai_content", True),
    }
    if d.get("publish_at"):  # scheduled: must be private until then
        status["privacyStatus"] = "private"
        status["publishAt"] = d["publish_at"]
    return {
        "snippet": {
            "title": d["title"],
            "description": d.get("description", ""),
            "tags": d.get("tags", []),
            "categoryId": str(d.get("category_id", 27)),
            "defaultLanguage": d.get("language", "en"),
            "defaultAudioLanguage": d.get("language", "en"),
        },
        "status": status,
    }


def start_upload(token, meta, path):
    size = os.path.getsize(path)
    req = urllib.request.Request(
        f"{API}/videos?uploadType=resumable&part=snippet,status",
        data=json.dumps(meta).encode(), method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=UTF-8",
                 "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.headers["Location"]


def send_file(token, session, path):
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        pos = 0
        while True:
            chunk = f.read(CHUNK)
            end = pos + len(chunk) - 1
            req = urllib.request.Request(session, data=chunk, method="PUT", headers={
                "Authorization": f"Bearer {token}", "Content-Length": str(len(chunk)),
                "Content-Range": f"bytes {pos}-{end}/{size}"})
            try:
                with urllib.request.urlopen(req, timeout=600) as r:
                    return json.load(r)  # the last chunk returns the video resource
            except urllib.error.HTTPError as e:
                if e.code != 308:  # 308 = chunk received, send the next one
                    raise
            pos = end + 1
            print(f"  {pos * 100 // size}% uploaded", flush=True)


def upload_video(token, meta, path):
    try:
        session = start_upload(token, meta, path)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        if "containsSyntheticMedia" not in detail:
            raise RuntimeError(detail) from e
        # Older API versions reject the AI-content field: upload without it and say so.
        print("  note: the API did not accept the AI-content label; tick it in YouTube Studio")
        meta["status"].pop("containsSyntheticMedia")
        session = start_upload(token, meta, path)
    return send_file(token, session, path)


def set_thumbnail(token, video_id, image):
    req = urllib.request.Request(f"{API}/thumbnails/set?videoId={video_id}", data=open(image, "rb").read(),
                                 method="POST", headers={"Authorization": f"Bearer {token}",
                                                         "Content-Type": "image/jpeg"})
    try:
        urllib.request.urlopen(req, timeout=120).read()
        return True
    except urllib.error.HTTPError as e:
        print(f"  thumbnail not set ({e.code}): custom thumbnails need a phone-verified channel. "
              "Add it in YouTube Studio.")
        return False


def main():
    spec_path = sys.argv[1]
    dry = "--dry-run" in sys.argv or not all(os.environ.get(k) for k in
                                             ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"))
    spec = json.load(open(spec_path))
    defaults = spec.get("defaults", {})
    token = None if dry else access_token()
    results = []
    for v in spec["videos"]:
        path = os.path.expandvars(v["file"])
        meta = metadata(v, defaults)
        print(f"\n{v['title']}\n  file: {path} ({os.path.getsize(path) / 1e6:.1f} MB)")
        print(f"  {meta['status']['privacyStatus']}, made for kids: {meta['status']['selfDeclaredMadeForKids']}, "
              f"AI content: {meta['status'].get('containsSyntheticMedia')}, {len(meta['snippet']['tags'])} tags")
        if dry:
            continue
        video = upload_video(token, meta, path)
        url = f"https://youtu.be/{video['id']}"
        print(f"  uploaded: {url}")
        thumb = os.path.expandvars(v["thumbnail"]) if v.get("thumbnail") else None
        if thumb:
            set_thumbnail(token, video["id"], thumb)
        results.append({"title": v["title"], "id": video["id"], "url": url, "privacy": meta["status"]["privacyStatus"],
                        "publish_at": meta["status"].get("publishAt")})
    if dry:
        print("\nDry run: nothing was uploaded." + ("" if "--dry-run" in sys.argv else
              " Set YT_CLIENT_ID, YT_CLIENT_SECRET and YT_REFRESH_TOKEN to upload."))
    else:
        out = os.path.splitext(spec_path)[0] + ".results.json"
        json.dump(results, open(out, "w"), indent=1)
        print(f"\nDone. Video links saved to {out}.")
        for r in results:
            when = (f"private until {r['publish_at']}, then public" if r["publish_at"] else r["privacy"])
            print(f"  {r['url']}  {when}")
        if any(r["privacy"] == "private" and not r["publish_at"] for r in results):
            print("Private videos stay private: open YouTube Studio to check and publish them.")


if __name__ == "__main__":
    main()
