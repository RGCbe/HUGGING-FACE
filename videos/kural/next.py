"""Which kural is next, and when should it go live?

    python3 next.py CHANNEL    prints {"kural": N, "publish_at": "...Z" or null, "last_on_channel": M}

CHANNEL is a key of "channels" in config.json (kids, adult). Reads that channel's public feed and its
Shorts and Videos pages (no login needed) and finds the highest "Thirukkural N" or "Super Kural #N"
already published, so a day that failed is simply tried again the next day. publish_at is today's
publish_time in config.json, in UTC. If that is less than an hour away (or past), publish_at is
null: the video goes public as soon as it is uploaded, so the next morning's run sees it on the
channel and moves on. Exits with status 2 once last_kural is done, 3 if the channel is not set up yet (no channel_id), and
4 if neither the feed nor the pages could be read.
"""
import datetime
import json
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

cfg = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")))
channel = cfg["channels"][sys.argv[1]]
if not channel["channel_id"]:
    print(json.dumps({"kural": None, "error": f"channel {sys.argv[1]} has no channel_id in config.json yet"}))
    sys.exit(3)


def fetch(url, tries=3):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except OSError:  # urllib errors, timeouts; YouTube's feed sometimes answers 404 for hours
            if k + 1 < tries:
                time.sleep(5 * (k + 1))
    return None


# The channel's public feed, and its Shorts and Videos pages as a second source: the feed has
# gone down for a whole morning before, while the pages kept working.
texts, sources = [], []
feed = fetch(f"https://www.youtube.com/feeds/videos.xml?channel_id={channel['channel_id']}")
if feed:
    root = ET.fromstring(feed)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    texts += [e.find("a:title", ns).text or "" for e in root.findall("a:entry", ns)]
    sources.append("feed")
for tab in ("shorts", "videos"):
    page = fetch(f"https://www.youtube.com/{channel['handle']}/{tab}") if channel.get("handle") else None
    if page:
        texts.append(page)
        sources.append(tab)
if not sources:
    print(json.dumps({"kural": None, "error": "could not read the channel's feed or pages; try again later"}))
    sys.exit(4)
# titles are "Thirukkural N for Kids: ..." (or "Thirukkural N: ..."); the first ones were "Super Kural #N"
done = [int(n) for t in texts for n in re.findall(r"(?:super\s*kural\s*#?|thirukkural)\s*(\d+)", t, re.I)]
last = max(done, default=0)
kural = max(last + 1, channel["first_kural"])
if kural > cfg["last_kural"]:
    print(json.dumps({"kural": None, "last_on_channel": last, "done": True}))
    sys.exit(2)

tz = ZoneInfo(cfg["timezone"])
now = datetime.datetime.now(tz)
hh, mm = map(int, cfg["publish_time"].split(":"))
at = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
publish_at = at.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if at - now >= datetime.timedelta(hours=1) else None
print(json.dumps({"kural": kural, "publish_at": publish_at, "last_on_channel": last, "read": sources}))
