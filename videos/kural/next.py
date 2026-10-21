"""Which kural is next, and when should it go live?

    python3 next.py            prints {"kural": N, "publish_at": "...Z", "last_on_channel": M}

Reads the channel's public feed (no login needed) and finds the highest "Super Kural #N" already
published, so a day that failed is simply tried again the next day. publish_at is today's
publish_time in config.json (or tomorrow's, if that is less than two hours away), in UTC.
Exits with status 2 once last_kural is done.
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
url = f"https://www.youtube.com/feeds/videos.xml?channel_id={cfg['channel_id']}"
with urllib.request.urlopen(url, timeout=60) as r:
    root = ET.fromstring(r.read())
ns = {"a": "http://www.w3.org/2005/Atom"}
titles = [e.find("a:title", ns).text or "" for e in root.findall("a:entry", ns)]
done = [int(m.group(1)) for t in titles for m in [re.search(r"super\s*kural\s*#?\s*(\d+)", t, re.I)] if m]
last = max(done, default=0)
kural = max(last + 1, cfg["first_kural"])
if kural > cfg["last_kural"]:
    print(json.dumps({"kural": None, "last_on_channel": last, "done": True}))
    sys.exit(2)

tz = ZoneInfo(cfg["timezone"])
now = datetime.datetime.now(tz)
hh, mm = map(int, cfg["publish_time"].split(":"))
at = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
if at - now < datetime.timedelta(hours=2):
    at += datetime.timedelta(days=1)
print(json.dumps({"kural": kural, "publish_at": at.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                  "last_on_channel": last}))
