# Tea Break on Facebook and Instagram

The owner's wish (23 Nov 2026): "i want to upload full video into instagram and facebook and i want to match with
youtube". Every Tea Break with Manoj video that goes public on YouTube (Shorts and full videos, Tamil and English)
also goes on the **Tea Break with Manoj** Facebook Page and on Instagram **@teabreakwithmanoj**, at the same time.

## How it works

1. `videos/doodle/upload.py` uploads a video to YouTube. When the upload json's defaults have `"meta": "tea-break"`
   (the Office Tea Talks recipe and `videos/teabreak/build.py`, `tamil.py`, `tamil_shorts.py` write it), it runs
   `meta.py queue` for that video. A queueing failure only prints a warning and the command to run by hand.
2. `meta.py queue YOUTUBE_ID FILE.mp4` reads the title, description, language, privacy and publish time from
   YouTube and stores the mp4 and `entries/ID.json` in the **private** dataset `Rggroups/meta-queue`.
3. A scheduled task runs `python3 videos/meta/meta.py run` every hour:
   - **Facebook**: a Short (vertical, at most 90 s) as a Page **Reel**, a full video as a Page **video**. If the
     YouTube time is more than 15 minutes away, Facebook schedules it for that time; otherwise it goes up now.
   - **Instagram**: a **Reel**, posted on the first run after the YouTube time (Instagram cannot schedule). Wide
     full videos are fine as Reels, up to 15 minutes. If Instagram's upload server refuses the file, Instagram is
     asked to fetch the Facebook copy instead.
   - Each platform is marked done in the entry, with its id and link, so nothing is posted twice. A failure is
     recorded and retried on the next run. If an earlier run was cut off mid-post, the next run checks whether that
     post already exists before posting again.

```bash
python3 videos/meta/meta.py check              # read-only: token, Page, Instagram link, quota, expiry
python3 videos/meta/meta.py status             # the queue
python3 videos/meta/meta.py run --dry-run      # what would be posted now
python3 videos/meta/meta.py run                # post (what a scheduled task runs)
```

Captions: the YouTube title without `#shorts`, a blank line, and the description without its `Theme:`, `Point:`
and `OLD COPY` lines. Facebook keeps the YouTube link `https://youtu.be/ID` at the end. Instagram has no link, at
most 2,200 characters and 30 hashtags.

Older Tea Break videos have no saved file and are skipped. Never download from YouTube.

## One-time setup (done 22-23 Nov 2026)

- Meta app **Tea Break Poster** (id 1476202361138315), owned by the owner.
- A long-lived **user** token with pages_show_list, pages_read_engagement, pages_manage_posts, publish_video,
  instagram_basic and instagram_content_publish. It never expires, but its data access ends about 22 Feb 2027.
  `check` warns 14 days before that. The owner then logs in to the app again and saves the new token.
- The token is saved as `META_PAGE_TOKEN` in the environment settings, never in the repo. The Page token is fetched
  from it on every run and kept in memory only.
- Page id 1454609281069084 and Instagram user id 17841478583761343 (the Instagram account is linked to the Page).
  Instagram allows 100 posts in 24 hours.

## Rules

- Never print, log or store a key. Meta keys go only to graph.facebook.com, graph-video.facebook.com and
  rupload.facebook.com (meta.py refuses any other host). HF_TOKEN goes only to the owner's Rggroups datasets.
  The YouTube login is used read-only and goes only to Google.
- The queue dataset must be private: meta.py creates it private and refuses to use it if it is not.
- Video files never go in this repo. They live in the private dataset.
- Post only the owner's own Tea Break videos. If something posts wrongly, delete only that post and report it.

## First test (23 Nov 2026)

- Facebook: the Tamil office Short kP8JfuFd2P0 was published as a Reel. t1B3j_aoA6s, AFf4DW2yeng and t2lZBSnr8YQ
  were scheduled for their YouTube times, and the API shows all three as scheduled.
- Instagram: refused for now. The resumable upload returns `ProcessingFailedError` for every file tried: the
  original, a faststart copy, and a stereo re-encode, from both Python and curl. Asking Instagram to fetch the
  Facebook copy ends in error 2207076. Instagram does not define that code; forum reports say it clears up with a
  later retry. The entry stays `failed` and every run retries it. If it keeps failing, the owner should check the
  Instagram app for an account notice and confirm that @teabreakwithmanoj is a professional account.
