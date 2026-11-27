"""When the next Money Tea Talks Short goes public, and which topic it tells.

    python3 videos/money/next.py      prints {"publish_at": ISO-UTC, "publish_at_ist": "...", "topic": {...},
                                              "used_topics": [...], "scheduled": [...], "too_far_ahead": bool}

Reads the money playlist (config.json "playlist" in videos/teabreak/config.json) on the Tea Break channel: every Short
there carries a "Money Tea Talks:" line and a "Topic: SLUG" line in its description (an "OLD COPY" is skipped). The
next slot is the first of config.json "days" at "publish_time" (India time) that is after the last scheduled Short and
at least "min_lead_hours" from now; the topic is the first one in topics.json not used yet. "too_far_ahead" is true
when that slot is more than "max_ahead_days" away: the run then makes nothing.
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
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def main():
    tok = access_token(CH["refresh_token_env"], CH["client_id_env"], CH["client_secret_env"])

    def get(path, **p):
        req = urllib.request.Request("https://www.googleapis.com/youtube/v3/" + path + "?" + urllib.parse.urlencode(p),
                                     headers={"Authorization": "Bearer " + tok})
        return json.load(urllib.request.urlopen(req, timeout=60))

    tb = json.load(open(os.path.join(HERE, "..", "teabreak", "config.json")))
    playlist = tb["playlists"][cfg["playlist"]]["id"]
    ids, page = [], None
    while True:
        d = get("playlistItems", part="contentDetails", playlistId=playlist, maxResults=50,
                **({"pageToken": page} if page else {}))
        ids += [i["contentDetails"]["videoId"] for i in d.get("items", [])]
        page = d.get("nextPageToken")
        if not page:
            break
    tz = ZoneInfo(cfg["timezone"])
    scheduled, used, last = [], [], None
    for k in range(0, len(ids), 50):
        for v in get("videos", part="snippet,status", id=",".join(ids[k:k + 50]))["items"]:
            desc = v["snippet"]["description"]
            if desc.startswith("OLD COPY") or not re.search(r"(?im)^\s*money tea talks\s*:", desc):
                continue
            at = v["status"].get("publishAt") or v["snippet"]["publishedAt"]
            when = datetime.datetime.fromisoformat(at.replace("Z", "+00:00"))
            last = max(last, when) if last else when
            m = re.search(r"(?m)^Topic: ([a-z0-9-]+)\s*$", desc)
            if m:
                used.append(m.group(1))
            scheduled.append({"id": v["id"], "title": v["snippet"]["title"], "topic": m.group(1) if m else None,
                              "public_at_ist": when.astimezone(tz).strftime("%Y-%m-%d %H:%M"),
                              "privacy": v["status"]["privacyStatus"]})
    now = datetime.datetime.now(tz)
    hh, mm = (int(x) for x in cfg["publish_time"].split(":"))
    earliest = now + datetime.timedelta(hours=cfg["min_lead_hours"])
    if last:
        earliest = max(earliest, last.astimezone(tz) + datetime.timedelta(minutes=1))
    day = earliest.date()
    while True:
        slot = datetime.datetime(day.year, day.month, day.day, hh, mm, tzinfo=tz)
        if DAYS[day.weekday()] in cfg["days"] and slot >= earliest:
            break
        day += datetime.timedelta(days=1)
    topics = json.load(open(os.path.join(HERE, "topics.json"), encoding="utf-8"))["topics"]
    todo = [t for t in topics if t["slug"] not in used]
    print(json.dumps({
        "publish_at": slot.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "publish_at_ist": slot.strftime("%A %d %b %Y, %H:%M India time"),
        "too_far_ahead": (slot - now).days > cfg["max_ahead_days"],
        "topic": todo[0] if todo else None,
        "used_topics": used,
        "scheduled": sorted(scheduled, key=lambda s: s["public_at_ist"]),
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
