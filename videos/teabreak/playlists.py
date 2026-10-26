"""The channel's playlists: create the ones in config.json that have no id yet, or add videos to one.

    python3 playlists.py                        create each playlist in config.json "playlists" without
                                                an "id" (public), and write its id into config.json
    python3 playlists.py add KEY VIDEO_ID ...   add videos to the playlist config.json calls KEY

build.py upload puts a new long video in "long" and in the playlists its topic lists in
topics.json ("playlists": ["wars"]), and each Short in "shorts". Uses the channel's YouTube key
(YT_CLIENT_ID, YT_CLIENT_SECRET and the refresh token named in config.json).
"""
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "doodle"))
from upload import access_token, add_to_playlist  # noqa: E402

CONFIG = os.path.join(HERE, "config.json")
cfg = json.load(open(CONFIG))
token = access_token(cfg["channel"]["refresh_token_env"])


def create(p):
    body = {"snippet": {"title": p["title"], "description": p["description"], "defaultLanguage": "en"},
            "status": {"privacyStatus": "public"}}
    req = urllib.request.Request("https://www.googleapis.com/youtube/v3/playlists?part=snippet,status",
                                 data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=60))["id"]


if sys.argv[1:2] == ["add"]:
    playlist = cfg["playlists"][sys.argv[2]]
    for video in sys.argv[3:]:
        if add_to_playlist(token, playlist["id"], video):
            print(f"added {video} to {playlist['title']}")
else:
    for key, p in cfg["playlists"].items():
        if not p.get("id"):
            p["id"] = create(p)
            print(f"created {key}: {p['title']} https://www.youtube.com/playlist?list={p['id']}")
    text = json.dumps(cfg, indent=2, ensure_ascii=False).replace('[\n    "Monday",\n    "Wednesday"\n  ]',
                                                                 '["Monday", "Wednesday"]')
    open(CONFIG, "w").write(text + "\n")
