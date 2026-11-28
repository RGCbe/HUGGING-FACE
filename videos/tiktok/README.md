# Tea Break Uploader (TikTok)

Sends the owner's finished vertical videos to his own TikTok inbox as drafts. He adds the caption and posts
each one in the TikTok app. It uses TikTok's Login Kit (`user.info.basic`) and the Content Posting API
Upload flow (`video.upload`).

| Part | Where |
|---|---|
| The app (`worker.js`) | Cloudflare Worker `tea-break-uploader` on the account's workers.dev address |
| Website, Terms, Privacy (`site/`) | Static Space `Rggroups/tea-break-uploader`, https://rggroups-tea-break-uploader.static.hf.space/ |
| Queue, tokens, owner | The Worker's KV namespace `tea-break-uploader` |

## Keys (never in the repo or the chat)
- The cloud environment holds `CF_ACCOUNT_ID` and `CF_WORKERS_TOKEN`, a Cloudflare "Edit Cloudflare Workers" token used by `deploy.py` and `tiktok_queue.py`.
- The Worker's secrets hold `TIKTOK_CLIENT_KEY` and `TIKTOK_CLIENT_SECRET`. The owner adds them in the Cloudflare dashboard. In Sandbox these are the sandbox app's own key and secret.

## Use
    python3 deploy.py [--verify tiktokXXXX.txt]   # put the app online, or update it
    python3 tiktok_queue.py add out/pig-war_tiktok.mp4 --name pig-war --title "The Pig War (1859)" --caption "..."
    python3 tiktok_queue.py list

Then the owner opens the app, clicks **Send to TikTok**, taps the TikTok notification, pastes the caption and posts.

## How it works
- The first TikTok account that connects becomes the owner. Any other account is refused.
- Sessions are HMAC-signed cookies, and `/send` checks the request's origin.
- Each TikTok upload chunk is one KV value: 12 MiB chunks, with the last up to 24 MiB, or one chunk for videos up to 24 MiB. This follows TikTok's Media Transfer Guide. The Worker deletes the chunks once TikTok has the video.

## Limits
- TikTok allows at most 5 pending inbox uploads per 24 hours, and 6 upload starts per minute.
- An unaudited app can only upload drafts, which are posted from the app.
- Cloudflare KV's free tier allows 1 GB of storage and 1,000 writes a day.
