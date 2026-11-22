"""How viewers answer the Tamil office / IT videos that work: numbers and top comments, for script research.

    python3 audience.py --search "office comedy tamil shorts" "manager comedy tamil" [--days 365] [--top 25] --out a.json
    python3 audience.py --ids VIDEO_ID [VIDEO_ID ...] --out a.json

Uses the YouTube Data API with the Tea Break upload app's sign-in (YT_CLIENT_ID, YT_CLIENT_SECRET,
YT_REFRESH_TOKEN_ADULT). A search costs 100 units of the daily 10,000. Reading numbers and comments costs 1 unit per
call.

Comments need more than that sign-in: it can't read them. They work only once a YouTube Data API key is saved as a
network secret for youtube.googleapis.com (header X-Goog-Api-Key). Without one, each video's comments are skipped
with a note.

For each video it keeps:
- title, channel, date, length, views, likes and comments;
- likes per 1,000 views and comments per 1,000 views;
- the 100 most relevant top-level comments: their text, likes and reply counts. Commenters' names are never stored.

Each comment is tagged by what the viewer did:
- laughed;
- said "same here" (relatable);
- tagged a friend;
- told their own story;
- asked for more;
- argued.

So a script can be written for the reaction we want. Nobody's video or audio is downloaded: only public numbers and
comment text, read through the official API.
"""
import argparse
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "doodle"))
from upload import access_token  # noqa: E402

TAGS = {
    "laugh": r"😂|🤣|😆|😅|\blol\b|\bhaha|semma|sema\b|vera level|வேற லெவல்|சிரிச்ச|சிரிப்பு|comedy|funny",
    "relatable": r"\bsame\b|enakkum|எனக்கும்|\breal(ity)?\b|\btrue\b|உண்மை|நிஜம்|relat|exactly|my (manager|boss|office|company|tl)"
                 r"|our (manager|office|company)|எங்க (ஆபீஸ்|மேனேஜர்|கம்பெனி|office|manager)|engal|enga (office|manager)|naanum|நானும்",
    "tag": r"@\w",
    "story": r"\b(i was|i am|i got|i had|my experience|happened to me)\b|நான் |எனக்கு |enaku |naan ",
    "more": r"part ?2|next part|அடுத்த பாகம்|continue|waiting for|more videos|இன்னும்",
    "argue": r"\bwrong\b|\bnot true\b|disagree|தப்பு|பொய்|\bfake\b|cringe|worst",
}


def api(tok, path, **p):
    req = urllib.request.Request("https://www.googleapis.com/youtube/v3/" + path + "?" + urllib.parse.urlencode(p),
                                 headers={"Authorization": "Bearer " + tok})
    return json.load(urllib.request.urlopen(req, timeout=60))


def seconds(iso):
    m = re.fullmatch(r"P(?:\d+D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    return 0 if not m else int(m[1] or 0) * 3600 + int(m[2] or 0) * 60 + int(m[3] or 0)


def is_tamil(v):
    s = v["snippet"]
    text = s["title"] + " " + s.get("description", "")[:300] + " " + " ".join(s.get("tags", [])[:20])
    return bool(re.search(r"[஀-௿]", text) or re.search(r"\btamil\b", text, re.I)
                or (s.get("defaultAudioLanguage") or "").startswith("ta"))


def comments(vid, n=100):
    # The upload sign-in cannot read comments (it lacks the youtube.force-ssl scope), so comments are read without it
    # from youtube.googleapis.com. That only works once a YouTube Data API key is saved in the environment's settings
    # as a network secret for that host (header X-Goog-Api-Key). Without one, comments are skipped and noted.
    url = "https://youtube.googleapis.com/youtube/v3/commentThreads?" + urllib.parse.urlencode(
        {"part": "snippet", "videoId": vid, "order": "relevance", "maxResults": n, "textFormat": "plainText"})
    try:
        r = json.load(urllib.request.urlopen(url, timeout=60))
    except urllib.error.HTTPError as e:
        return [], f"comments unavailable ({e.code}: no API key, or comments turned off)"
    out = []
    for it in r.get("items", []):
        c = it["snippet"]["topLevelComment"]["snippet"]
        text = c["textDisplay"]
        out.append({"text": text, "likes": c.get("likeCount", 0), "replies": it["snippet"].get("totalReplyCount", 0),
                    "tags": [k for k, rx in TAGS.items() if re.search(rx, text, re.I)]})
    return out, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--search", nargs="*", default=[])
    ap.add_argument("--ids", nargs="*", default=[])
    ap.add_argument("--days", type=int, default=365)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    tok = access_token("YT_REFRESH_TOKEN_ADULT")
    ids = list(dict.fromkeys(a.ids))
    after = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=a.days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    for q in a.search:
        r = api(tok, "search", part="id", q=q, type="video", maxResults=50, order="viewCount", publishedAfter=after,
                regionCode="IN", relevanceLanguage="ta")
        ids += [i["id"]["videoId"] for i in r.get("items", []) if i["id"]["videoId"] not in ids]
    vids = []
    for i in range(0, len(ids), 50):
        vids += api(tok, "videos", part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50])).get("items", [])
    if a.search:
        vids = [v for v in vids if is_tamil(v)]
    vids.sort(key=lambda v: -int(v["statistics"].get("viewCount", 0)))
    vids = vids[:a.top] if a.search else vids
    rows = []
    for v in vids:
        st, sn = v["statistics"], v["snippet"]
        views = int(st.get("viewCount", 0)) or 1
        cs, note = comments(v["id"])
        rows.append({
            "id": v["id"], "title": sn["title"], "channel": sn["channelTitle"], "published": sn["publishedAt"][:10],
            "seconds": seconds(v["contentDetails"].get("duration")), "views": views,
            "likes": int(st.get("likeCount", 0)), "comments": int(st.get("commentCount", 0)),
            "likes_per_1k": round(1000 * int(st.get("likeCount", 0)) / views, 1),
            "comments_per_1k": round(1000 * int(st.get("commentCount", 0)) / views, 2),
            "tag_share": {k: round(sum(k in c["tags"] for c in cs) / len(cs), 2) for k in TAGS} if cs else {},
            "top_comments": cs, "note": note,
        })
        print(f'{rows[-1]["views"]:>10,} {rows[-1]["likes_per_1k"]:>5} {rows[-1]["comments_per_1k"]:>5}  {len(cs):>3} comments  {sn["title"][:70]}', flush=True)
    json.dump({"checked": datetime.date.today().isoformat(), "queries": a.search, "videos": rows},
              open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
