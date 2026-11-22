"""When the next Office Tea Talks Short goes public, and which office stories the channel already told.

    python3 next.py      prints {"publish_at": ISO-UTC, "recent": [{"title", "theme", "date"}], "count": N}

Reads every upload of the channel (Tea Break; public, private and scheduled) with its key (config.json "channel"),
keeps only the office stories (their descriptions carry a "Theme:" line), finds the last scheduled one, and gives the
next free day after today at publish_time (India time). "theme" is read from the
"Theme:" line every description carries, and "used_points" from its "Point:" line (points.json ids), so a run does
not tell the same theme two days running or use a point twice.
"""
import datetime
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "doodle"))
from upload import access_token  # noqa: E402

cfg = json.load(open(os.path.join(HERE, "config.json")))
CH = cfg["channel"]


def main():
    tok = access_token(CH["refresh_token_env"], CH["client_id_env"], CH["client_secret_env"])

    def get(path, **p):
        req = urllib.request.Request("https://www.googleapis.com/youtube/v3/" + path + "?" + urllib.parse.urlencode(p),
                                     headers={"Authorization": "Bearer " + tok})
        return json.load(urllib.request.urlopen(req, timeout=60))

    me = get("channels", part="snippet,contentDetails", mine="true")["items"][0]
    ids, page = [], None
    while True:
        d = get("playlistItems", part="contentDetails", playlistId=me["contentDetails"]["relatedPlaylists"]["uploads"],
                maxResults=50, **({"pageToken": page} if page else {}))
        ids += [i["contentDetails"]["videoId"] for i in d.get("items", [])]
        page = d.get("nextPageToken")
        if not page:
            break
    recent, last = [], None
    for k in range(0, len(ids), 50):
        for v in get("videos", part="snippet,status", id=",".join(ids[k:k + 50]))["items"]:
            m = re.search(r"^Theme: (.+)$", v["snippet"]["description"], re.M)
            if not m:  # the channel's other videos (Tea Break's history stories) keep their own times
                continue
            at = v["status"].get("publishAt") or v["snippet"]["publishedAt"]
            when = datetime.datetime.fromisoformat(at.replace("Z", "+00:00"))
            last = max(last, when) if last else when
            pt = re.search(r"^Point: (p\d+)$", v["snippet"]["description"], re.M)
            recent.append({"title": v["snippet"]["title"], "theme": m.group(1).strip() if m else None,
                           "point": pt.group(1) if pt else None, "date": when.date().isoformat()})
    tz = ZoneInfo(cfg["timezone"])
    day = datetime.datetime.now(tz).date() + datetime.timedelta(days=1)
    if last:
        day = max(day, last.astimezone(tz).date() + datetime.timedelta(days=1))
    hh, mm = map(int, cfg["publish_time"].split(":"))
    at = datetime.datetime(day.year, day.month, day.day, hh, mm, tzinfo=tz).astimezone(datetime.timezone.utc)
    recent.sort(key=lambda r: r["date"], reverse=True)
    used = sorted({r["point"] for r in recent if r["point"]})
    print(json.dumps({"channel": me["snippet"]["title"], "publish_at": at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                      "recent": recent[:30], "count": len(recent), "used_points": used}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
