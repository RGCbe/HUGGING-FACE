"""What Tamil office and IT viewers are watching now: the topics for the Office Life Lessons channel.

    python3 trends.py [--days 90] [--out trends.json]

Searches YouTube (Data API, the Tea Break upload app's quota: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN_ADULT)
for Tamil office / IT / career videos and Shorts from the last --days days, and groups them into themes (appraisal,
manager, layoff, first job, salary, resignation, ...) by the words in their titles. Each theme gets its total and
median views and its three biggest examples, so a run can pick a theme that is wanted and write OUR OWN story about it.
Only titles and view counts are read: no one's video, audio or words are used.
"""
import argparse
import datetime
import json
import os
import re
import statistics
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "doodle"))
from upload import access_token  # noqa: E402

QUERIES = ["IT job tamil", "office life tamil shorts", "IT employee life tamil", "corporate life tamil",
           "manager office tamil", "appraisal hike tamil", "layoff IT tamil", "fresher job tamil",
           "work life balance tamil", "office politics tamil", "resignation notice period tamil", "salary tamil IT"]
THEMES = {
    "appraisal / hike": r"apprais|hike|increment|rating|promotion|promot",
    "manager / boss": r"manager|boss|team lead|\bTL\b|மேனேஜர்|பாஸ்",
    "layoff / job loss": r"layoff|lay off|fired|termination|job loss|வேலை போச்சு|recession",
    "first job / fresher": r"fresher|first job|first salary|campus|முதல் வேலை|முதல் சம்பளம்",
    "salary / money": r"salary|சம்பளம்|lakh|ctc|package|pf\b|tax",
    "resignation / switching": r"resign|notice period|switch|counter offer|ராஜினாமா|relieving",
    "work-life balance / stress": r"work.?life|stress|burnout|overtime|weekend|night shift|மன அழுத்தம்",
    "office politics / colleagues": r"office politic|colleague|took credit|toxic|gossip|whatsapp group|coworker|சக ஊழியர்",
    "interview / skills": r"interview|\bskills?\b|resume|upskill|\bAI\b|certif",
    "work from home / office": r"work from home|wfh|hybrid|return to office|rto",
}
# a video counts only if it is about work at all (a search also returns news and films)
WORK = r"\bjob|office|\bIT\b|company|manager|boss|salary|employee|corporate|interview|fresher|layoff|resign|hike|" \
       r"apprais|work|career|வேலை|ஆபீஸ்|சம்பளம்|கம்பெனி"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--out", default=os.path.join(HERE, "trends.json"))
    a = ap.parse_args()
    tok = access_token("YT_REFRESH_TOKEN_ADULT")

    def get(path, **p):
        req = urllib.request.Request("https://www.googleapis.com/youtube/v3/" + path + "?" + urllib.parse.urlencode(p),
                                     headers={"Authorization": "Bearer " + tok})
        return json.load(urllib.request.urlopen(req, timeout=60))

    after = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=a.days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids = []
    for q in QUERIES:
        s = get("search", part="snippet", q=q, type="video", relevanceLanguage="ta", regionCode="IN", order="viewCount",
                publishedAfter=after, maxResults=25)
        ids += [i["id"]["videoId"] for i in s["items"]]
    ids = list(dict.fromkeys(ids))
    videos = []
    for k in range(0, len(ids), 50):
        for v in get("videos", part="snippet,statistics,contentDetails", id=",".join(ids[k:k + 50]))["items"]:
            text = v["snippet"]["title"] + " " + " ".join(v["snippet"].get("tags", [])[:10])
            if not re.search(WORK, text, re.I):
                continue
            videos.append({"id": v["id"], "title": v["snippet"]["title"], "channel": v["snippet"]["channelTitle"],
                           "views": int(v["statistics"].get("viewCount", 0)), "date": v["snippet"]["publishedAt"][:10],
                           "themes": [t for t, pat in THEMES.items() if re.search(pat, text, re.I)]})
    themes = []
    for t in THEMES:
        g = [v for v in videos if t in v["themes"]]
        if g:
            themes.append({"theme": t, "videos": len(g), "total_views": sum(v["views"] for v in g),
                           "median_views": int(statistics.median(v["views"] for v in g)),
                           "examples": [{"title": v["title"], "views": v["views"], "channel": v["channel"]}
                                        for v in sorted(g, key=lambda v: -v["views"])[:3]]})
    themes.sort(key=lambda t: -t["median_views"])
    out = {"checked": datetime.date.today().isoformat(), "days": a.days, "videos": len(videos), "themes": themes,
           "top_titles": [{"title": v["title"], "views": v["views"]} for v in sorted(videos, key=lambda v: -v["views"])[:25]]}
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for t in themes:
        print(f"{t['theme']:30s} {t['videos']:3d} videos | median {t['median_views']:>9,} | total {t['total_views']:>12,} | "
              f"e.g. {t['examples'][0]['title'][:60]} ({t['examples'][0]['views']:,})")


if __name__ == "__main__":
    main()
