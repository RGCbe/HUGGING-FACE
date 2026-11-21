"""Which questions are next for Manoj Explains, and when their videos go public.

    python3 next_topic.py [--count 2]

Reads every upload on the channel (public, private and scheduled) with the channel's own upload app (the
environment variables named in config.json), and picks the first topics in topics.json whose "match" words are in no
upload's title. Each topic gets the next free day after today and after the last scheduled upload: the English video
at publish_time.en, the Tamil one at publish_time.ta (India time). Prints JSON:
{"channel": {...}, "topics": [{"slug", "question", ..., "en_at": ISO-UTC, "ta_at": ISO-UTC}], "uploaded": [titles]}
Exits with status 2 when every topic is done (add more to topics.json).
"""
import argparse
import datetime
import json
import os
import sys
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(HERE, "config.json")))
CH = cfg["channel"]


def token():
    body = urllib.parse.urlencode({"client_id": os.environ[CH["client_id_env"]].strip(),
                                   "client_secret": os.environ[CH["client_secret_env"]].strip(),
                                   "refresh_token": os.environ[CH["refresh_token_env"]].strip(),
                                   "grant_type": "refresh_token"}).encode()
    return json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", data=body, timeout=60))["access_token"]


def get(path, tok, **params):
    url = "https://www.googleapis.com/youtube/v3/" + path + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok})
    return json.load(urllib.request.urlopen(req, timeout=60))


def uploads(tok):
    me = get("channels", tok, part="snippet,contentDetails", mine="true")["items"][0]
    playlist = me["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, page = [], None
    while True:
        params = {"part": "contentDetails", "playlistId": playlist, "maxResults": 50}
        if page:
            params["pageToken"] = page
        d = get("playlistItems", tok, **params)
        ids += [i["contentDetails"]["videoId"] for i in d.get("items", [])]
        page = d.get("nextPageToken")
        if not page:
            break
    titles, scheduled = [], []
    for k in range(0, len(ids), 50):
        for v in get("videos", tok, part="snippet,status", id=",".join(dict.fromkeys(ids[k:k + 50])))["items"]:
            titles.append(v["snippet"]["title"])
            if v["status"].get("publishAt"):
                scheduled.append((v["snippet"]["title"],
                                  datetime.datetime.fromisoformat(v["status"]["publishAt"].replace("Z", "+00:00"))))
    return me, titles, scheduled


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=cfg.get("topics_per_run", 2))
    a = ap.parse_args()
    tok = token()
    me, titles, scheduled = uploads(tok)
    topics = json.load(open(os.path.join(HERE, "topics.json")))["topics"]
    # only the lore videos keep the daily slot taken (the F-Rank recaps and other uploads have their own times)
    lore = [at for title, at in scheduled if any(t["match"].lower() in title.lower() for t in topics)]
    last = max(lore, default=None)
    low = [t.lower() for t in titles]
    todo = [t for t in topics if not any(t["match"].lower() in x for x in low)]
    if not todo:
        print(json.dumps({"done": True, "uploaded": titles}, ensure_ascii=False))
        sys.exit(2)
    tz = ZoneInfo(cfg["timezone"])
    day = datetime.datetime.now(tz).date() + datetime.timedelta(days=1)
    if last:
        day = max(day, last.astimezone(tz).date() + datetime.timedelta(days=1))
    out = []
    for t in todo[: a.count]:
        at = {}
        for lang in ("en", "ta"):
            hh, mm = map(int, cfg["publish_time"][lang].split(":"))
            local = datetime.datetime(day.year, day.month, day.day, hh, mm, tzinfo=tz)
            at[lang + "_at"] = local.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        out.append(dict(t, **at))
        day += datetime.timedelta(days=1)
    print(json.dumps({"channel": {"id": me["id"], "title": me["snippet"]["title"]}, "topics": out,
                      "uploaded": titles}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
