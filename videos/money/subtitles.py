"""Upload a Short's Tamil and English subtitles (build.py's WORK/out/subs_ta.srt and subs_en.srt) to YouTube.

    python3 videos/money/subtitles.py VIDEO_ID WORK/out

Uses the Tea Break channel's key (config.json "channel"), which needs the youtube.force-ssl permission (the owner
re-made the key with it on 27 Nov 2026). A language that already has our track (same name, not YouTube's automatic
one) is skipped, so a rerun adds nothing twice. If the key lacks the permission, it says so and exits 0: subtitles
are not essential (YouTube makes automatic Tamil captions, and its English auto-dub brings its own).
"""
import json
import os
import sys
import urllib.error
import urllib.request
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "doodle"))
from upload import access_token  # noqa: E402

CH = json.load(open(os.path.join(HERE, "config.json")))["channel"]
TRACKS = [("ta", "தமிழ்", "subs_ta.srt"), ("en", "English", "subs_en.srt")]


def main():
    video, folder = sys.argv[1], sys.argv[2]
    tok = access_token(CH["refresh_token_env"], CH["client_id_env"], CH["client_secret_env"])
    auth = {"Authorization": f"Bearer {tok}"}
    try:
        req = urllib.request.Request(f"https://www.googleapis.com/youtube/v3/captions?part=snippet&videoId={video}",
                                     headers=auth)
        have = json.load(urllib.request.urlopen(req, timeout=60)).get("items", [])
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        if "insufficientPermissions" in body or e.code == 403:
            print("subtitles skipped: the Tea Break key lacks the youtube.force-ssl permission (the owner re-makes it "
                  "in the OAuth Playground with that scope)")
            return
        raise SystemExit(f"HTTP {e.code}: {body[:400]}")
    for lang, name, fname in TRACKS:
        path = os.path.join(folder, fname)
        if not os.path.exists(path):
            continue
        if any(i["snippet"]["language"] == lang and i["snippet"]["name"] == name and i["snippet"]["trackKind"] != "asr"
               for i in have):
            print(f"{lang}: already there")
            continue
        b = uuid.uuid4().hex
        meta = json.dumps({"snippet": {"videoId": video, "language": lang, "name": name, "isDraft": False}}).encode()
        body = (f"--{b}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode() + meta +
                f"\r\n--{b}\r\nContent-Type: application/x-subrip\r\n\r\n".encode() + open(path, "rb").read() +
                f"\r\n--{b}--\r\n".encode())
        req = urllib.request.Request("https://www.googleapis.com/upload/youtube/v3/captions?part=snippet&uploadType=multipart",
                                     data=body, method="POST",
                                     headers=dict(auth, **{"Content-Type": f"multipart/related; boundary={b}"}))
        try:
            r = json.load(urllib.request.urlopen(req, timeout=120))
            print(f"{lang}: uploaded ({r['snippet']['name']})")
        except urllib.error.HTTPError as e:
            print(f"{lang}: HTTP {e.code}: {e.read().decode(errors='replace')[:300]}")


if __name__ == "__main__":
    main()
