# Manoj Explains: how the automation works, step by step

## Part 1: what Manoj does, once (about 20 minutes)

1. **Create the channel** on the **new Google email** (Manoj, 20 Nov: "new channel with new mail"): sign in to
   YouTube with that email, "Create a channel", name **Manoj Explains**, handle **@manoj-d-explains** (done 20 Nov 2026: channel id UC7m2wBWnP-KLyfrtXcYKyjQ).
2. **Profile picture and banner.** YouTube Studio, Customisation, Branding: upload `brand/manoj_explains_logo.png`
   as the picture and `brand/manoj_explains_banner.jpg` as the banner. Basic info: paste the description from
   `brand/channel_about.md`.
3. **Its own upload app, on the new email** (Manoj opened the Google Cloud console with the new email, 20 Nov; this
   also gives the channel its own YouTube upload allowance, separate from Tea Break). At console.cloud.google.com,
   signed in with the new email:
   1. Project picker at the top, "New project", name `Manoj Explains`, Create, then select it.
   2. Search "YouTube Data API v3", open it, Enable.
   3. Menu, "Google Auth Platform" (older menus: "APIs & Services", "OAuth consent screen"), "Get started":
      app name `Manoj Explains uploader`, support email the new email, Audience **External**, contact email the new
      email, agree, Create.
   4. "Audience": **Publish app**, Confirm (status "In production"; in "Testing" Google cancels the key after 7 days).
   5. "Clients", "Create client": type **Web application**, name `Manoj Explains uploader`, under "Authorized
      redirect URIs" add `https://developers.google.com/oauthplayground`, Create. Copy the **Client ID** and the
      **Client secret** at once (the secret is shown only now; "Download JSON" keeps both).
4. **Upload permission (the key).** developers.google.com/oauthplayground: gear icon, tick "Use your own OAuth
   credentials", paste the **new** Client ID and Client secret; in "Input your own scopes" type
   `https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube`; "Authorize APIs"; sign in
   with the new email and choose **Manoj Explains**; if Google says the app is not verified: "Advanced", "Go to
   Manoj Explains uploader (unsafe)" (it is his own app); "Exchange authorization code for tokens"; copy the
   **Refresh token**.
5. **Save the three values** in Claude's cloud environment settings (the environment menu in the session title, Edit),
   as environment variables, never in the chat:
   - `YT_CLIENT_ID_MOVIES`: the Client ID
   - `YT_CLIENT_SECRET_MOVIES`: the Client secret
   - `YT_REFRESH_TOKEN_MOVIES`: the Refresh token
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
- **YouTube upload allowance:** the channel has its own upload app (10,000 units a day; an upload uses about
  1,600), so a run uploads at most four videos, well inside it.
- **Pictures:** the free picture service allows about 60 a day; a topic needs about 22, so a run makes two topics.
- **Nothing copyrighted, ever:** no clips, stills, posters, comic panels, logos, film music, actors' faces, or AI
  pictures of Marvel characters.

## Status (20 Nov 2026)

- Channel made by Manoj on his new email; its own upload app and key saved; key tested: scopes `youtube` and
  `youtube.upload`, channel UC7m2wBWnP-KLyfrtXcYKyjQ.
- Scheduled tasks (fresh cloud session each time, no computer needed; no connectors needed):
  - "Manoj Explains: daily lore video (EN + TA)": every day 9:53 am India time.
  - "Manoj Explains: Saturday report": Saturday 6:47 pm India time.
  - The fortnightly compilation is added once there are 10-15 videos.
- First videos: "Who is Doctor Doom?", English https://youtu.be/_cmNok1vVhg (public 20 Nov, 7 pm India time) and
  Tamil https://youtu.be/AddGAaSefUs (8 pm); channel description, keywords, banner and three playlists set up.
- Daily from 21 Nov: one question a day, English 5:30 am India time, Tamil 8 pm; the daily run is at 9:53 am.
