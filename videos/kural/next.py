"""Which kural is next, and when should it go live?

    python3 next.py CHANNEL    prints {"kural": N, "publish_at": "...Z" or null, "last_on_channel": M}

CHANNEL is a key of "channels" in config.json (kids, adult). Reads that channel's public feed (no
login needed) and finds the highest "Super Kural #N" already
published, so a day that failed is simply tried again the next day. publish_at is today's
publish_time in config.json, in UTC. If that is less than an hour away (or past), publish_at is
null: the video goes public as soon as it is uploaded, so the next morning's run sees it on the
channel and moves on. Exits with status 2 once last_kural is done, and 3 if the channel is not set up yet (no channel_id).
"""
import datetime
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

cfg = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")))
channel = cfg["channels"][sys.argv[1]]
if not channel["channel_id"]:
    print(json.dumps({"kural": None, "error": f"channel {sys.argv[1]} has no channel_id in config.json yet"}))
    sys.exit(3)
url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel['channel_id']}"
with urllib.request.urlopen(url, timeout=60) as r:
    root = ET.fromstring(r.read())
ns = {"a": "http://www.w3.org/2005/Atom"}
titles = [e.find("a:title", ns).text or "" for e in root.findall("a:entry", ns)]
done = [int(m.group(1)) for t in titles for m in [re.search(r"super\s*kural\s*#?\s*(\d+)", t, re.I)] if m]
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
print(json.dumps({"kural": kural, "publish_at": publish_at, "last_on_channel": last}))
