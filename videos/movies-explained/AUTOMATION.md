# Manoj Explains: how the automation works, step by step

## Part 1: what Manoj does, once (about 15 minutes)

1. **Create the channel** on the **new Google email** (Manoj, 20 Nov: "new channel with new mail"): sign in to
   YouTube with that email, "Create a channel", name **Manoj Explains**, handle **@ManojExplainsMovies**.
2. **Profile picture and banner.** YouTube Studio, Customisation, Branding: upload `brand/manoj_explains_logo.png`
   as the picture and `brand/manoj_explains_banner.jpg` as the banner. Basic info: paste the description from
   `brand/channel_about.md`.
3. **Let the new email use the upload app.** The upload app (the Google Cloud project whose Client ID and secret the
   Tea Break uploads use) belongs to the **old** email. Sign in to console.cloud.google.com with the old email,
   open that project, "Google Auth Platform" (or "APIs & Services", "OAuth consent screen"):
   - if its status is **Testing**: add the new email under "Audience", "Test users". Better still, press
     "Publish app" (In production): in Testing, Google cancels the key after 7 days;
   - if it is already **In production**: nothing to do here.
4. **Upload permission (the key).** In Google's OAuth Playground (developers.google.com/oauthplayground): gear icon,
   "Use your own OAuth credentials" with the same Client ID and Client secret as Tea Break; scopes
   `https://www.googleapis.com/auth/youtube.upload` and `https://www.googleapis.com/auth/youtube`; "Authorize APIs";
   sign in with the **new email** and choose **Manoj Explains**; if Google says the app is not verified, "Advanced",
   "Go to ..." (it is your own app); "Exchange authorization code for tokens"; copy the **refresh token**.
   (If Google says `redirect_uri_mismatch`, tell Claude: there is another way.)
5. **Save the key.** Claude's cloud environment settings (the environment menu in the session title, Edit): add an
   environment variable named `YT_REFRESH_TOKEN_MOVIES` with the refresh token as its value. Never paste it in
   the chat.
6. **Tell Claude "channel ready".** That is the last thing you need to do.

## Part 2: what Claude sets up, once

1. The channel's playlists ("Marvel lore", "Marvel lore in Tamil", "Before Avengers: Doomsday") and upload defaults.
2. `config.json` (channel, times, playlists) and `topics.json` (the questions in order, each with its sources).
3. A skill (`.claude/skills/manoj-explains/SKILL.md`): the whole recipe of one video, from the question to the
   scheduled upload, so every run makes it the same way.
4. Scheduled runs in the cloud (they need no computer of yours):
   - **Monday and Thursday:** two new topics each run; each topic becomes an English and a Tamil video, scheduled
     for the coming days at 7 pm (English) and 8 pm (Tamil) India time. Four topics a week, eight videos.
   - **Every second Sunday:** the last 10-15 videos joined into one 30-40 minute video, English and Tamil.
   - **Every Saturday:** a short report: views, subscribers, the best and worst videos, what to change.
5. The first uploads: "Who is Doctor Doom?" (already made), then the rest of the run-up to Avengers: Doomsday.

## Part 3: what every scheduled run does (no one has to watch it)

1. Picks the next question in `topics.json` that the channel does not have yet.
2. Researches it and writes `sources.md`.
3. Writes the English script (the first line must score at least 60) and the Tamil script.
4. Voices both in Manoj's AI voice; checks every English word and that every Tamil part is heard as Tamil.
5. Makes the pictures (3D anime, our own, Manoj's anime self at the start and end) and looks at every one.
6. Builds the videos (`lore_video.py`), checks frames and loudness.
7. Writes titles, descriptions (sources, "made with AI", "fan channel, not linked to Marvel or Disney"), tags.
8. Uploads both as private, scheduled, in the right playlists.
9. Sends Claude's main session a report: what was made, when it goes out, anything that failed.

If a run fails (voice credits used up, picture allowance used up, a fact that cannot be sourced), it stops, makes
nothing half-done public, and the report says why; the next run carries on.

## Part 4: limits to know

- **Voice credits:** about 3,800 per topic (English and Tamil); four topics a week fit the ElevenLabs plan next to
  Tea Break and the devotional channel. More needs a free voice model.
- **YouTube upload allowance:** the upload app is shared by all the channels (10,000 units a day; an upload uses
  about 1,600), so a run uploads at most four videos and never on the same day as another channel's big upload.
- **Pictures:** the free picture service allows about 60 a day; a topic needs about 22, so a run makes two topics.
- **Nothing copyrighted, ever:** no clips, stills, posters, comic panels, logos, film music, actors' faces, or AI
  pictures of Marvel characters.
