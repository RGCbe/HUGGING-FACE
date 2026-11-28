"""Multi-language localization for YouTube titles and descriptions.
Generates localized metadata for all major Indian languages (Hindi, Telugu, Tamil,
Malayalam, Kannada, Bengali, Marathi, Gujarati, Punjabi, English) for YouTube Data API v3.

Usage:
    python3 localize.py "Video Title #shorts" [--description "Description text"] [--lang en|ta]
"""
import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request

INDIAN_LANGUAGES = {
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "en": "English",
}


def _translate_text(text, target_lang, source_lang="auto"):
    """Translate text using standard HTTP translation API with retry."""
    if not text or not text.strip():
        return ""
    # Extract and preserve hashtags
    tags = re.findall(r"#\w+", text)
    clean_text = re.sub(r"#\w+", "", text).strip()
    if not clean_text:
        return text

    url = (
        "https://translate.googleapis.com/translate_a/single?client=gtx"
        f"&sl={source_lang}&tl={target_lang}&dt=t&q={urllib.parse.quote(clean_text)}"
    )
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        },
    )

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                translated = "".join(seg[0] for seg in data[0] if seg[0]).strip()
                if tags:
                    translated += " " + " ".join(tags)
                return translated
        except Exception:
            if attempt < 2:
                time.sleep(0.5)
    return text  # fallback to original


def build_localizations(
    title, description="", default_lang="en", targets=None
):
    """Build a YouTube localizations dictionary for major Indian languages.

    Args:
        title: Video title (max 100 chars).
        description: Video description.
        default_lang: Source/default language code ('en', 'ta', etc.).
        targets: List of language codes to generate. Defaults to all
          INDIAN_LANGUAGES except default_lang.

    Returns:
        dict: {"hi": {"title": "...", "description": "..."}, ...}
    """
    if targets is None:
        targets = [k for k in INDIAN_LANGUAGES if k != default_lang]

    localizations = {}
    for code in targets:
        if code == default_lang:
            continue
        try:
            loc_title = _translate_text(title, code, source_lang=default_lang)
            # YouTube titles must be <= 100 characters
            loc_title = loc_title[:100]

            loc_desc = ""
            if description and description.strip():
                # For long descriptions, translate the first 1-2 paragraphs
                paras = description.strip().split("\n\n")
                first_part = "\n\n".join(paras[:2])
                rest = "\n\n".join(paras[2:])
                loc_first = _translate_text(
                    first_part, code, source_lang=default_lang
                )
                loc_desc = (loc_first + "\n\n" + rest).strip()[:5000]

            localizations[code] = {
                "title": loc_title,
                "description": loc_desc or description[:5000],
            }
        except Exception as e:
            print(
                f"  Warning: failed to localize for {code} ({INDIAN_LANGUAGES.get(code)}): {e}",
                file=sys.stderr,
            )

    return localizations


def update_youtube_video(video_id, token_env="YT_REFRESH_TOKEN", id_env="YT_CLIENT_ID", secret_env="YT_CLIENT_SECRET", targets=None):
    """Fetch an existing YouTube video, translate its title/description into Indian languages, and update it on YouTube."""
    from upload import access_token
    token = access_token(token_env, id_env, secret_env)

    # 1. Fetch current video details
    get_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,localizations&id={video_id}"
    req = urllib.request.Request(get_url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    items = data.get("items", [])
    if not items:
        sys.exit(f"Video {video_id} not found on YouTube.")

    item = items[0]
    snip = item["snippet"]
    title = snip["title"]
    desc = snip.get("description", "")
    default_lang = snip.get("defaultLanguage") or ("ta" if any('\u0b80' <= c <= '\u0bff' for c in title) else "en")

    print(f"Updating localizations for YouTube video: {video_id} ('{title[:40]}...')")
    print(f"  Detected default language: {default_lang} ({INDIAN_LANGUAGES.get(default_lang, default_lang)})")

    # 2. Build localizations
    loc = build_localizations(title, desc, default_lang=default_lang, targets=targets)

    # 3. Update video on YouTube
    body = {
        "id": video_id,
        "snippet": {
            "title": title,
            "description": desc,
            "categoryId": snip.get("categoryId", "27"),
            "defaultLanguage": default_lang,
            "defaultAudioLanguage": snip.get("defaultAudioLanguage", default_lang)
        },
        "localizations": loc
    }
    put_url = "https://www.googleapis.com/youtube/v3/videos?part=snippet,localizations"
    put_req = urllib.request.Request(
        put_url,
        data=json.dumps(body).encode(),
        method="PUT",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(put_req) as r:
        res = json.load(r)
    print(f"SUCCESS: Updated {video_id} on YouTube with {len(loc)} Indian languages!")
    return loc


def main():
    parser = argparse.ArgumentParser(
        description="Localize YouTube title and description into Indian languages."
    )
    parser.add_argument("title_or_id", help="Video title to localize, OR YouTube video ID if --update is passed")
    parser.add_argument(
        "--description", default="", help="Video description to localize"
    )
    parser.add_argument(
        "--lang", default="en", help="Source language (en, ta, etc.)"
    )
    parser.add_argument(
        "--update", action="store_true", help="Update an existing YouTube video directly by ID"
    )
    parser.add_argument(
        "--token-env", default="YT_REFRESH_TOKEN", help="Environment variable for YouTube refresh token"
    )
    parser.add_argument(
        "--client-id-env", default="YT_CLIENT_ID", help="Environment variable for YouTube client ID"
    )
    parser.add_argument(
        "--client-secret-env", default="YT_CLIENT_SECRET", help="Environment variable for YouTube client secret"
    )
    args = parser.parse_args()

    if args.update:
        update_youtube_video(args.title_or_id, token_env=args.token_env, id_env=args.client_id_env, secret_env=args.client_secret_env)
    else:
        loc = build_localizations(
            args.title_or_id, args.description, default_lang=args.lang
        )
        print(json.dumps(loc, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
