"""The channel's playlists: create the ones in config.json that have no id yet, or add videos to one.

    python3 playlists.py                        create each playlist in config.json "playlists" without
                                                an "id" (public), and write its id into config.json
    python3 playlists.py add KEY VIDEO_ID ...   add videos to the playlist config.json calls KEY
    python3 playlists.py sync [--apply]         put every video of the channel in the playlists it belongs in
                                                (see wanted()) and out of the others; without --apply, only list

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
    body = {"snippet": {"title": p["title"], "description": p["description"], "defaultLanguage": p.get("language", "en")},
            "status": {"privacyStatus": "public"}}
    req = urllib.request.Request("https://www.googleapis.com/youtube/v3/playlists?part=snippet,status",
                                 data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=60))["id"]


API = "https://www.googleapis.com/youtube/v3"
# a story's words in a title (English or Tamil) -> its slug in topics.json
STORIES = [("emu-war", r"emu|ஈமு"), ("pig-war", r"pig|பன்னி"), ("anglo-zanzibar-war", r"zanzibar|shortest war|navy|quick exit|38 min"),
           ("great-moon-hoax", r"moon|bat-men"), ("mike-the-headless-chicken", r"chicken|headless mike|கோழி"),
           ("acoustic-kitty", r"kitty|spy cat|cia|பூனை"), ("exploding-whale", r"whale|திமிங்கல"),
           ("wojtek-the-soldier-bear", r"wojtek|bear|கரடி"), ("dancing-plague", r"danc|red shoes|டான்ஸ்"),
           ("whisky-war", r"whisky|விஸ்கி"), ("sergeant-stubby", r"stubby|dog|நாய்"), ("tulip-mania", r"tulip|டூலிப்")]


def get(path, **params):
    import urllib.parse
    req = urllib.request.Request(f"{API}/{path}?" + urllib.parse.urlencode(params), headers={"Authorization": f"Bearer {token}"})
    return json.load(urllib.request.urlopen(req, timeout=60))


def every(path, **params):
    items, page = [], None
    while True:
        r = get(path, **params, **({"pageToken": page} if page else {}))
        items += r["items"]
        page = r.get("nextPageToken")
        if not page:
            return items


def seconds(iso):
    import re
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    return sum(int(x or 0) * k for x, k in zip(m.groups(), (3600, 60, 1)))


def wanted(v):
    """The playlists a video belongs in: English full stories in "long" and their topics' playlists, English Shorts
    in "shorts", Tamil ones in "tamil" or "shorts_ta", The F-Rank Tea Seller's reviews and Shorts in "frank"."""
    import re
    title = v["snippet"]["title"]
    low = title.lower()
    tamil = v["snippet"].get("defaultAudioLanguage", "").startswith("ta")
    short = seconds(v["contentDetails"]["duration"]) <= 180 and ("#shorts" in low or "#webtoon" in low)
    if "#webtoon" in low or "webtoon" in low or "f-rank" in low or "weakest hunter" in low:
        return {"frank"}
    if tamil:
        return {"shorts_ta"} if "#shorts" in low else {"tamil"}
    if short:
        return {"shorts"}
    if "welcome to tea break" in low:
        return {"long"}
    keys = {"long"}
    topics = {t["slug"]: t.get("playlists", []) for t in json.load(open(os.path.join(HERE, "topics.json")))}
    for slug, words in STORIES:
        if re.search(words, low):
            keys |= set(topics.get(slug, []))
            break
    return keys


def sync(apply):
    """Put every video in the playlists it belongs in, and take it out of the ones it does not (only the playlists
    in config.json; a video is never deleted, only its place in a playlist)."""
    ch = get("channels", part="contentDetails", mine="true")["items"][0]
    ids = [i["contentDetails"]["videoId"] for i in every("playlistItems", part="contentDetails", maxResults=50,
                                                           playlistId=ch["contentDetails"]["relatedPlaylists"]["uploads"])]
    videos = []
    for k in range(0, len(ids), 50):
        videos += get("videos", part="snippet,contentDetails,status", id=",".join(ids[k:k + 50]))["items"]
    managed = {key: p for key, p in cfg["playlists"].items() if p.get("id")}
    inside = {key: {i["contentDetails"]["videoId"]: i["id"] for i in every("playlistItems", part="contentDetails", maxResults=50,
                                                                             playlistId=p["id"])} for key, p in managed.items()}
    changes = 0
    # in release order (a scheduled video by its publish time), so each playlist plays oldest to newest
    release = lambda v: (0 if "welcome" in v["snippet"]["title"].lower() or "இப்போ தமிழிலும்" in v["snippet"]["title"] else 1,
                         v["status"].get("publishAt") or v["snippet"]["publishedAt"])
    for v in sorted(videos, key=release):
        want = wanted(v)
        for key, p in managed.items():
            there = v["id"] in inside[key]
            if key in want and not there:
                changes += 1
                print(f"add    {p['title'][:34]:34} <- {v['snippet']['title'][:60]}")
                if apply:
                    add_to_playlist(token, p["id"], v["id"])
            elif key not in want and there:
                changes += 1
                print(f"remove {p['title'][:34]:34} -> {v['snippet']['title'][:60]}")
                if apply:
                    req = urllib.request.Request(f"{API}/playlistItems?id={inside[key][v['id']]}", method="DELETE",
                                                 headers={"Authorization": f"Bearer {token}"})
                    urllib.request.urlopen(req, timeout=60).read()
    print(f"{changes} change(s){'' if apply else ' to make (dry run: add --apply)'}")


if sys.argv[1:2] == ["sync"]:
    sync("--apply" in sys.argv)
elif sys.argv[1:2] == ["add"]:
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
