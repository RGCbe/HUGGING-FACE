"""Which story is next for Tea Break with Manoj, and when its videos go public.

    python3 next.py    prints {"slug", "topic", "wikipedia", "long_at", "shorts_at": [..], "uploaded": [titles]}

Reads every upload on the channel (public, private and scheduled) with the channel's YouTube key
(YT_CLIENT_ID, YT_CLIENT_SECRET and the refresh token named in config.json), and picks the first
topic in topics.json whose "match" words are in no upload's title, so a week that failed is simply
made again next time. The long video goes public on the first long_day (Saturday) after today, and
after the last upload already scheduled, at publish_time; its two Shorts on the shorts_days after that. Exits with status 2 when every
topic is done (add more to topics.json).
"""
import datetime
import json
import os
import sys
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(HERE, "config.json")))
topics = json.load(open(os.path.join(HERE, "topics.json")))
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def token():
    body = urllib.parse.urlencode({"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
                                   "refresh_token": os.environ[cfg["channel"]["refresh_token_env"]],
                                   "grant_type": "refresh_token"}).encode()
    return json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", data=body, timeout=60))["access_token"]


def get(path, tok, **params):
    url = "https://www.googleapis.com/youtube/v3/" + path + "?" + urllib.parse.urlencode(params)
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization": "Bearer " + tok}), timeout=60))


def uploads():
    """Every upload's title, and the latest time one of them is scheduled to go public (or None)."""
    tok = token()
    playlist = get("channels", tok, part="contentDetails", mine="true")["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    titles, ids, page = [], [], None
    while True:
        params = {"part": "snippet", "playlistId": playlist, "maxResults": 50}
        if page:
            params["pageToken"] = page
        d = get("playlistItems", tok, **params)
        titles += [i["snippet"]["title"] for i in d.get("items", [])]
        ids += [i["snippet"]["resourceId"]["videoId"] for i in d.get("items", [])]
        page = d.get("nextPageToken")
        if not page:
            break
    scheduled = []
    for k in range(0, len(ids), 50):
        for v in get("videos", tok, part="status", id=",".join(ids[k:k + 50])).get("items", []):
            if v["status"].get("publishAt"):
                scheduled.append(datetime.datetime.fromisoformat(v["status"]["publishAt"].replace("Z", "+00:00")))
    return titles, max(scheduled, default=None)


def after(day, name):
    """The first date strictly after `day` that falls on weekday `name`."""
    return day + datetime.timedelta(days=(DAYS.index(name) - day.weekday() - 1) % 7 + 1)


def at(day):
    tz = ZoneInfo(cfg["timezone"])
    hh, mm = map(int, cfg["publish_time"].split(":"))
    local = datetime.datetime(day.year, day.month, day.day, hh, mm, tzinfo=tz)
    return local.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


titles, last_scheduled = uploads()
todo = [t for t in topics if not any(t["match"].lower() in title.lower() for title in titles)]
if not todo:
    print(json.dumps({"slug": None, "uploaded": titles}))
    sys.exit(2)
start = datetime.datetime.now(ZoneInfo(cfg["timezone"])).date()
if last_scheduled:  # never on top of a week that is already scheduled
    start = max(start, last_scheduled.astimezone(ZoneInfo(cfg["timezone"])).date())
long_day = after(start, cfg["long_day"])
shorts = []
for name in cfg["shorts_days"]:
    shorts.append(after(shorts[-1] if shorts else long_day, name))
print(json.dumps(dict(todo[0], long_at=at(long_day), shorts_at=[at(d) for d in shorts], uploaded=titles), indent=1))
