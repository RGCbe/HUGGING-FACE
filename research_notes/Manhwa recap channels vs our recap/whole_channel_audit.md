# Whole-channel audit: "Tea Break with Manoj" (UCOEtL8JtwJ4TVJiJewHpwew), its production and its pipeline

Audit date: 29-30 October 2026. Read-only. Channel data comes from the YouTube Data API v3 with the owner's own token, using 123 quota units: channels.list mine=true, the uploads playlist, search.list forMine=true (100 units), videos.list, playlists.list and playlistItems.list. Local files were measured with ffprobe, ffmpeg ebur128, librosa pYIN and Python. Note: during the audit the coordinator removed the Episode 1 recap (wca8rGT6xlk) and its Short (5lejbz98fCc) from the true-history playlists and set them to private until 2026-11-06 and 2026-11-08. The API pull below already shows that state.

Source shorthand used below:
- **[API]**: YouTube Data API v3 responses pulled 2026-10-29 (https://www.googleapis.com/youtube/v3/), saved at /tmp/claude-0/-home-user-HUGGING-FACE/1f6a9d07-9b37-5360-b91a-1c1bc7ba9d52/scratchpad/yt/data.json.
- **[thumb test]**: each video's served hqdefault.jpg compared with YouTube's three auto frames (hq1/hq2/hq3.jpg) and with our local thumbnail files. The score is the mean absolute grey-level difference on a 160x90 grid (0 = identical; 255 = maximum).
- **[voice test]**: librosa 0.11 pYIN, 60-400 Hz, octave errors outside 0.55x-1.8x of the median removed, 20 ms frames.

## 1. The channel: every upload, its numbers, packaging, thumbnails and schedule

### Takeaway
The channel has 13 uploads: 5 public, 8 private and scheduled, and no unlisted ones. In total it has 8 subscribers and 386 views. 46% of all views come from one Short (Emu War "Round 1", 179 views). No upload has a comment. **No video has a custom thumbnail.** Every served thumbnail is a frame of the video itself, usually a busy board with a burned-in caption. The channel is still unverified (`longUploadsStatus: eligible`). Saturday, Monday and Wednesday at 18:00 IST is kept for every history video. The F-Rank recap and its Short break it (Friday and Sunday), and the week of 6-11 Nov carries five uploads.

### Cited Findings
- **Channel totals:** "Tea Break with Manoj", handle @teabreakwithmanoj, created 2026-10-23 10:18 UTC, country IN.
  - subscriberCount 8, viewCount 386, public videoCount 5.
  - status: `longUploadsStatus: "eligible"`, `isChannelMonetizationEnabled: false`, `madeForKids: false`.
  - Channel keywords: "funny history" "history facts" "true stories" "weird history" "Emu War".
  - The description promises "New video every Saturday, Shorts on Monday and Wednesday" and ends "Hello friends, I'm Manoj."
  - — [API channels.list mine=true]
- **Verification signal:** "eligible" means long uploads can be unlocked by verifying, so the channel is not verified. This fits the earlier log line "thumbnail not set (403): custom thumbnails need a phone-verified channel". YouTube: you can upload your own video thumbnails "if your account is verified", and for Shorts "Your account must be verified to use this feature" (Shorts thumbnails only from Studio on a computer) — [API channels.list status](https://www.googleapis.com/youtube/v3/channels); [upload.py set_thumbnail](file:///home/user/HUGGING-FACE/videos/doodle/upload.py); [YouTube Help 72431](https://support.google.com/youtube/answer/72431)
- **Every upload** ([API videos.list part=snippet,contentDetails,statistics,status,processingDetails,fileDetails]; times converted to IST):

  | # | Video id | Title (chars) | Length | Public at (IST) / state | Views / likes / comments | Playlists | Thumbnail served |
  |---|---|---|---|---|---|---|---|
  | 1 | z2hg0AKBbe4 | Welcome to Tea Break with Manoj: Funny True History (51) | 0:36 | public, Fri 23 Oct 17:49 | 56 / 6 / 0 | none | auto frame hq2 (diff 0.0) |
  | 2 | _HFf832UDjc | Welcome to Tea Break with Manoj ☕ Funny True History #shorts | 0:36 | public, Sat 24 Oct 07:52 | 39 / 2 / 0 | none | auto frame hq2 (diff 1.3) |
  | 3 | rUER31XYzwY | The Emu War: When Birds Beat an Army (1932) (43) | 3:28 | public, Sat 24 Oct 18:00 | 98 / 3 / 0 | Funny True History Stories; Weird Wars; Animals | auto frame hq2 (diff 0.0) |
  | 4 | kALR1MFNVkM | 10 Bullets for 1 Bird?! The Emu War (1932) #shorts (50) | 0:34 | public, Mon 26 Oct 18:00 | 19 / 2 / 0 | Funny History Shorts | auto frame hq2 (diff 0.6) |
  | 5 | d31tIOx8Ghs | Soldiers With Machine Guns vs Emus: Round 1 (1932) #shorts (58) | 0:39 | public, Wed 28 Oct 18:00 | 179 / 4 / 0 | Funny History Shorts | a video frame that matches none of the three auto frames (diffs 17.6-18.0): a frame picked in the app, not a designed image |
  | 6 | UBMNs8fQV1Q | The Pig War: When One Pig Nearly Started a War (1859) (53) | 4:22 | private, scheduled Sat 31 Oct 18:00 | 0 | Funny True History Stories; Weird Wars; Animals | a video frame (the Winfield Scott handshake board); not our "WAR OVER A PIG?!" thumbnail (diff 69.4) |
  | 7 | Vpof_YytMKM | One Pig Almost Started a War (1859) #shorts (43) | 1:00 (59.3 s) | private, scheduled Mon 2 Nov 18:00 | 0 | Funny History Shorts | video frame |
  | 8 | ZFIozeQ1puc | Who Stopped the Pig War? (1859) #shorts (39) | 0:46 | private, scheduled Wed 4 Nov 18:00 | 0 | Funny History Shorts | video frame |
  | 9 | wca8rGT6xlk | His Tea Gives You 1 Hour of Power \| The F-Rank Tea Seller, Episode 1 (68) | 3:10 | private, scheduled Fri 6 Nov 18:00 | 0 | none | a video frame (dark wolf panel, caption "Inside the dungeon,"); not our "HIS TEA = 1 HOUR OF POWER" thumbnail (diff 79.4) |
  | 10 | J5nVh2oJ1mI | The Shortest War Ever: Over in 38 Minutes (1896) (48) | 3:35 | private, scheduled Sat 7 Nov 18:00 | 0 | Funny True History Stories; Weird Wars | video frame ("Your manager's email..." board) |
  | 11 | 5lejbz98fCc | He drank the F-Rank's tea... #webtoon #manhwa (45) | 0:45 | private, scheduled Sun 8 Nov 18:00 | 0 | none | video frame |
  | 12 | f7nhRNTN2FI | A Whole Navy Gone in 3 Minutes (1896) #shorts (45) | 0:58 | private, scheduled Mon 9 Nov 18:00 | 0 | Funny History Shorts | video frame |
  | 13 | 45MfcsHV-vE | The Quick Exit That Ended a War (1896) #shorts (46) | 0:56 | private, scheduled Wed 11 Nov 18:00 | 0 | Funny History Shorts | video frame |

  — [API]; [thumb test]; local custom thumbnails [pig-war_thumbnail.jpg](file:///root/.cache/tea-break/work/pig-war/out/pig-war_thumbnail.jpg), [recap_thumbnail.jpg](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/out/recap_thumbnail.jpg)
- **Thumbnail method:** YouTube does not serve auto frames (hq1-3) for private videos (404), so the 8 private videos could only be compared with our local custom thumbnails. Both checked (Pig War, recap) are clearly different images. Viewed side by side, all 8 served thumbnails are frames of the video with small top-third text and a yellow caption box, so no custom image is set on any of the 13 videos. The Zanzibar run's own report says its thumbnail "failed with a 403 because the channel's phone number isn't verified yet" — [thumb test]; [Zanzibar session result, 2026-10-28 17:11 UTC](https://claude.ai/code/session_015TghYxR3wZNx7eGqUnno3T)
- **Other metadata on all 13:**
  - category 27 (Education), except the recap and its Short, which are 24 (Entertainment).
  - language en; madeForKids false; license youtube; definition hd.
  - `contentDetails.caption: false`: no caption track is uploaded, and captions are burned into the picture.
  - `status.containsSyntheticMedia` is not returned for any video.
  - The recap and its Short have `embeddable: false`; all others are true.
  - — [API]
- **Tags:** the long history videos have 12 search-style tags each (e.g. "pig war", "pig war 1859", "funny history", "true story"). The history Shorts have 6. The recap has 10 generic ones ("webtoon", "manhwa", "anime", "tea") — [API]
- **Description pattern (long history videos):**
  1. "The [X] of [year] really happened: ..." followed by "The true story, explained in N minutes."
  2. Sources (2 links). Chapters: Emu 10, Pig 10, Zanzibar 11.
  3. A summary paragraph with names and numbers.
  4. "Do you know a funny true story like this? Tell me in the comments."
  5. An AI note ("The voice is an AI copy of my own voice; the pictures are made with an AI image model (FLUX.2 klein), and the music is original.").

  The Emu War Shorts link the full video (https://youtu.be/rUER31XYzwY). The Pig War and Zanzibar Shorts only say "Full video on the channel." with no link — [API]; [meta.json](file:///home/user/HUGGING-FACE/videos/teabreak/example/meta.json)
- **Zanzibar title:** the title does not contain "Zanzibar". The weekly skill now says "The title must contain the topic's `match` words ... (the name people search for, such as 'Anglo-Zanzibar War'): a catchy title without the name ('The Shortest War Ever') is not found by search." "Anglo-Zanzibar war" appears only in the tags and the description — [API]; [SKILL.md step 9](file:///home/user/HUGGING-FACE/.claude/skills/tea-break-weekly/SKILL.md)
- **Playlists (all public):**

  | Playlist | Items |
  |---|---|
  | Funny True History Stories (PLUAmyQAv4d68) | 3 |
  | Funny History Shorts (PLNMchGZEVlZw) | 6 |
  | Weird Wars in History (PLW9zRU1t75yY) | 3 |
  | Animals That Made History (PLNdt13_t8exE) | 2 |
  | History's Craziest Hoaxes and Crazes (PLNx3CJ___yNM) | 0 |
  | Strange But True History (PLCxGCvqyFIG4) | 0 |

  The two intro videos are in no playlist. Two public playlists are empty — [API playlists.list mine=true, playlistItems.list]
- **Rhythm:** the config sets publish_time 18:00 Asia/Kolkata, long_day Saturday, shorts_days Monday and Wednesday, and length 120-300 s. The schedule above follows it for Emu War, Pig War and Zanzibar. The recap is Friday 6 Nov and its Short Sunday 8 Nov, so 6-11 Nov has five uploads (Fri, Sat, Sun, Mon, Wed). The intro (16:9 and vertical) was published off-schedule. The intro says "A new story every Saturday, and short ones on Monday and Wednesday." — [config.json](file:///home/user/HUGGING-FACE/videos/teabreak/config.json); [API]; [00-intro/voiceover_en.txt](file:///home/user/HUGGING-FACE/videos/00-intro/voiceover_en.txt)
- **Uploaded files vs local files:**
  - Byte-identical: the Pig War Shorts (25,365,186 and 12,757,962 bytes), the recap (34,046,067) and the recap Short (12,978,513).
  - The local pig-war.mp4 (109,546,487 bytes) differs from the uploaded file (109,384,243 bytes), so the local copy was re-rendered after upload.
  - — [API fileDetails.fileSize]; ffprobe on [pig-war out/](file:///root/.cache/tea-break/work/pig-war/out/) and [recap out/](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/out/)
- **Comments and analytics could not be read:** commentThreads.list returned 403 "insufficient authentication scopes" (the token's scope is only `https://www.googleapis.com/auth/youtube`). The YouTube Analytics API returned 403 "has not been used in project 906871128572 before or it is disabled". So there are no retention, CTR, impressions or traffic-source numbers; commentCount from statistics is 0 on all videos — [API]

### Inferences
- With no custom thumbnails, every video competes in search and browse with a random-looking board frame. The Pig War frame is a handshake, Zanzibar's a man at a laptop, and the recap's a dark wolf panel with "Inside the dungeon,". These say nothing about the hook. On a 386-view channel, this is probably the biggest packaging loss you can fix in a day (verify the phone, then set the thumbnails that already exist locally).
- Views so far are tiny and come mostly from one Short (179 of 391 summed video views). No conclusion about the voice, or anything else, can be drawn from them. Round 1 and 10 Bullets have the same voice, style and story but 179 vs 19 views, which points to topic, hook and distribution rather than voice.
- The Zanzibar title is the skill's own example of a title that "is not found by search". Changing it to include "Anglo-Zanzibar War" before 7 Nov is cheap.
- `embeddable: false` on the recap pair stands out against the other 11 videos. It may be a side effect of the change to private and is worth checking in Studio.
- The API returns no `containsSyntheticMedia` field for any video. Whether the AI label is on cannot be confirmed from the API, even though upload.py sends it and the Zanzibar report says "All three carry YouTube's AI-content label".

### Gaps
- No retention, CTR, impressions, traffic sources or audience data: the Analytics API is disabled in the OAuth project, and the token lacks the yt-analytics scope.
- Comment text could not be read (scope). The counts are 0 anyway.
- The AI-label state could not be verified through the API. Check it in YouTube Studio.
- For the private videos, the served frame could not be matched to a specific auto frame (hq1-3 return 404 while private). It is only shown not to be our designed thumbnail.

## 2. Scripts and first 15 seconds, judged against SCRIPT_STYLE.md

### Takeaway
All three history scripts open with the same template: "Before you (start) laugh(ing), this is real history. In [year]... But how / what happened next?" They then use the same second line, "Hello friends, I'm Manoj. In this video, I'll tell you how [X] started, what happened next, and who won in the end. Every word is true, and the sources are in the description." They end with the same comments line, "Do you know a funny true story like this, from your town or your family? Tell me in the comments. It could be my next video." SCRIPT_STYLE.md now bans every one of these. Outside the template greeting, the stories barely use contractions (Zanzibar: 0, Pig War: 1). The automated Zanzibar script (28 Oct) copied the Pig War template almost word for word, because the weekly skill tells the writer to copy the Pig War files. The recap has none of the history templates, but it breaks the style rules on "It is the year...", "This is Arjun. He is eighteen...", and reading the bubbles.

### Cited Findings
- **The new rules (SCRIPT_STYLE.md, committed 2026-10-29 19:49 UTC as cdd81d9, pushed):**
  - "Contractions, always".
  - "Never three short sentences of the same shape in a row".
  - "About one honest reaction or small opinion a minute".
  - "Tell the story, don't describe the picture".
  - "Fresh words every video. The only fixed sentence is the greeting ... no 'In this video, I'll tell you...', no stock ending".
  - It also gives the Pig War's own greeting line as its "Before" example of what not to write.
  - "If the listening test fails a line, rephrase it the way a person would say it. Don't chop it into shorter sentences".
  - — [SCRIPT_STYLE.md](file:///home/user/HUGGING-FACE/videos/SCRIPT_STYLE.md)
- **The weekly writer's instructions conflict with those rules:**
  - The SKILL says "Read `videos/SCRIPT_STYLE.md` before writing, and follow it" and "never the same words as an earlier video; no 'In this video, I'll tell you...'". But it also says "The finished example to copy is The Pig War".
  - The scheduled task's prompt says "Copy the files in videos/teabreak/example/ (The Pig War) for the shape of every file you write".
  - The example voiceover_en.txt still contains "In this video, I'll tell you how one pig started the Pig War, what happened next, and who won in the end. Every word is true, and the sources are in the description." and the fixed comments line.
  - The SKILL's description template requires "Do you know a funny true story like this? Tell me in the comments." in every description.
  - — [SKILL.md](file:///home/user/HUGGING-FACE/.claude/skills/tea-break-weekly/SKILL.md); [example/voiceover_en.txt](file:///home/user/HUGGING-FACE/videos/teabreak/example/voiceover_en.txt); [scheduled task trig_01Ekjz2QMnfZbRedZKZcteJJ prompt, via list_triggers]
- **First 15 seconds** (words whose start time is under 15.0 s, from each video's timing.json):
  - **Intro (45 words):** "Ever wished history was this much fun? Hello friends, I'm Manoj, and welcome to Tea Break with Manoj. This channel is for busy people. You have a short tea break, and I have a short, funny story from history to go with it. Every story" — [00-intro/timing.json](file:///home/user/HUGGING-FACE/videos/00-intro/timing.json)
  - **Emu War (47 words):** "Before you start laughing, this is real history. In nineteen thirty-two, an army declared war on birds, with machine guns. But what happened next? Hello friends, I'm Manoj. In this video, I'll tell you how the Emu War started, what happened, and who won in the end." — [01-emu-war/timing.json](file:///home/user/HUGGING-FACE/videos/01-emu-war/timing.json)
  - **Pig War (43 words):** "Before you laugh, this is real history. In eighteen fifty-nine, one dead pig almost started a war between America and Britain. But how? Hello friends, I'm Manoj. In this video, I'll tell you how one pig started the Pig War, what happened next," — [pig-war/timing.json](file:///root/.cache/tea-break/work/pig-war/timing.json)
  - **Zanzibar** (no local timing; the first ~39 words at the Pig War's 157 wpm): "Before you laugh, this is real history. In eighteen ninety-six, Britain and Zanzibar fought a war that was over before your tea got cold. But how? Hello friends, I'm Manoj. In this video, I'll tell you how the shortest" — script recovered from the weekly run's transcript ([session cse_015TghYxR3wZNx7eGqUnno3T, 2026-10-28 14:40 UTC](https://claude.ai/code/session_015TghYxR3wZNx7eGqUnno3T)), with its first-round rewording applied
  - **F-Rank recap (38 words):** "This boy is the weakest hunter on Earth. He sells tea for ten rupees a glass. But anyone who drinks his tea becomes unstoppable, for exactly one hour. Hello friends, I'm Manoj. Today is something new: our very" — [recap/timing.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/timing.json)
- **Hook scores** (the project's own hookscore.py, the tool the weekly skill requires; ≥60 = WORKABLE): Emu War 69, Pig War 69, Zanzibar 61, recap 34 (WEAK), intro 33 (WEAK) — [hookscore.py](file:///home/user/HUGGING-FACE/.claude/skills/yt-script/hookscore.py)
- **Counts per script** (emotion tags removed; a "same-shape run" is 3+ sentences in a row of ≤6 words each; uncontracted forms are phrases like "it is", "was not", "he would"):

  | Script | Lines | Words | Sentences (median words) | Contractions (outside the template greeting line) | Uncontracted forms | Runs of 3+ short sentences | Template sentences shared with other videos |
  |---|---|---|---|---|---|---|---|
  | Intro | 7 | 99 | 9 (11) | 2 (I'm, I'll) | 0 | 0 | "sources are always in the description" |
  | Emu War | 11 | 577 | 82 (5) | 9 (7: it's, can't, you've, that's, doesn't, here's, that's) | 1 ("was not") | 6 (longest 9 in a row: "This was the perfect chance! / The army was ready. / They started shooting... / and got just twelve emus. / Then? / The gun jammed. / And the rest of the emus? / Bye bye. / Gone.") | 8: "Before you start laughing, this is real history"; "In this video, I'll tell you how"; "who won in the end"; "Every word is true"; "sources are in the description"; "Just like a plan from your manager..."; "Who won?"; the fixed comments line |
  | Pig War | 15 | 656 | 76 (8) | 4 (1: "here's"; "we'll" is inside Pickett's quote) | 4 ("was not" x2, "he would", "they would") | 3 ("Griffin said no. / He wanted one hundred dollars. / Cutlar refused.") | 8: same as Emu War plus "But how?" |
  | Zanzibar | 15 | 541 | 54 (9) | 2 (0) | 2 ("is not only jokes", "were not soldiers") | 1 ("Big plan. / Great speech. / Quick exit.") | 9: same set, including "Just like your manager's email on a Friday evening" |
  | Recap | 29 | 468 | 61 (7) | 5 (4) | 7 ("It is the year", "Here is episode one", "He is eighteen", "there is" x2, "like it is poison", "What is this power?") | 2 | none from the history videos; it has its own "Hello friends, I'm Manoj. Today is something new" |

  — measured by script_audit.py on the files linked above
- **Owner's own reactions (counted by hand):**
  - **Emu War:** 8 narrator asides ("Nice idea, right?", "Double trouble for the farmers.", "Just like a plan from your manager in a Monday meeting. Perfect on paper.", "Bye bye. Gone.", "Do the maths.", "Ten bullets. For one bird.", "That's the level of this war."). None is in the first person.
  - **Pig War:** about 8 ("Simple, right?", "What could go wrong?", "Happy anniversary.", the mango-tree comparison, "And this one? Over a pig.", "Finally, someone sensible.", "But here's the funny part."). None in the first person.
  - **Zanzibar:** 4 written asides plus the owner's real recording, the only first-person reaction in any script: "[mytake] This war was shorter than my tea break. Some of my office meetings last longer than this whole war!"
  - **Recap:** 3 small asides ("zero manners", "Oh no.", "the smartest thing a hunter can do. They run."). "I'm undercharging" is Arjun's thought, not Manoj's.
  - **Intro:** none.
  - — scripts linked above; [topics.json my_take](file:///home/user/HUGGING-FACE/videos/teabreak/topics.json)
- **Lines that only describe the picture:**
  - History videos: none found. The pictures are generated to illustrate the narration.
  - Recap: about 9 of 29 lines narrate what the panel already shows or read its bubble. Examples: "Viktor points at Arjun and laughs." (SCRIPT_STYLE.md's own "not" example), "Holding the glass like it is poison, he asks: tea from an F-Rank? Is it poisoned with weakness?", "Their tank goes flying, and his shield cracks in half.", "And then, his body starts to glow. Golden power fills his hands. What is this power?" (the panel bubble reads "WHAT... IS THIS POWER?!"), "The golden light fades away. His sword just bounces off the armor.", "They crawl out of the Gate, barely alive.", "Viktor storms back to the tea stall and grabs Arjun.", "But deep inside the Gate, a giant red eye opens."
  - The earlier audit found that for 11 of 20 bubbles the narrator says essentially the same words.
  - — [recap.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json); [our_recap_audit.md](file:///home/user/HUGGING-FACE/research_notes/Manhwa%20recap%20channels%20vs%20our%20recap/our_recap_audit.md)
- **Other recap violations of SCRIPT_STYLE.md:**
  - "It is the year twenty thirty-one." and "This is Arjun. He is eighteen years old ... Business is slow." are the exact "Before" examples the style guide rewrites.
  - "Here is episode one" uses the banned "here is".
  - — [recap.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json); [SCRIPT_STYLE.md](file:///home/user/HUGGING-FACE/videos/SCRIPT_STYLE.md)
- **The listening test pushes toward choppy lines:** in the Zanzibar run, lines that failed Whisper were reworded by splitting them. "He had been friendly with Britain, and some people suspected foul play." became "The Sultan was a friend of Britain. Some people suspected foul play." The run report says "two rounds of rewording were needed" — [Zanzibar session events, 2026-10-28 15:42 UTC](https://claude.ai/code/session_015TghYxR3wZNx7eGqUnno3T)
- **Sound tags in the Emu War script:** it contains inline "[chuckle]" and "[laugh]". The current skill says "No sound tags like [laugh]: the voice reads them out." The aligned word timings do not include those words — [01-emu-war/voiceover_en.txt](file:///home/user/HUGGING-FACE/videos/01-emu-war/voiceover_en.txt); [SKILL.md](file:///home/user/HUGGING-FACE/.claude/skills/tea-break-weekly/SKILL.md)

### Inferences
- The first 15 seconds of every history video are mostly the same 25-30 words. A returning viewer hears a formula, and a new viewer gets a hook and then about 7 seconds of channel promise ("In this video, I'll tell you how... who won in the end") before the story starts. In the history videos, the story starts at about 0:19-0:21.
- The repetition is built into the pipeline, not a one-off. While the example file and the scheduled prompt both say "copy the Pig War", the next automated script (4 Nov) is likely to repeat the template again, even though SCRIPT_STYLE.md is now on the branch. Rewriting the example's voiceover, hooks and meta to the new style would fix the source.
- The missing contractions and the short-shape runs (Emu War's median sentence is 5 words) are a script problem that no voice can hide. They are exactly what SCRIPT_STYLE.md calls "sounds like a computer".
- The hook formula scores well on hookscore.py (61-69) because the scorer rewards "you", a date and "But how?". Scoring alone keeps choosing the same opener.

### Gaps
- The Zanzibar script is rebuilt from the run's transcript (first draft plus round-one rewording). The second round of rewording was not captured, so 1-2 lines may differ from what was voiced.
- Per-line timing for Zanzibar is not available locally (the run's work folder was in another container), so its first 15 seconds are estimated from word count.
- Whether Emu War's "[chuckle]"/"[laugh]" were actually spoken can't be told from the files (the Emu War voice files are not in this container).

## 3. Voice: the reference recording, the clone, emotion tags and the owner's own clips

### Takeaway
The single reference the clone copies (ref_cut.wav, 11.61 s, 33 words of a bank announcement) has these measured properties:
- a narrow pitch range: 4.6 semitones between the 5th and 95th percentile, median 128.6 Hz, standard deviation 1.69 st;
- a fast, unbroken pace: 170.5 wpm, with one pause of 0.18 s in the whole clip;
- a dark tone: the 2-5 kHz presence band is 30 dB under the band below 200 Hz.

The clone reproduces this closely in the Pig War. Per-line median pitch is 125.7-132.4 Hz, the median within-line range is 4.5 semitones, and lines tagged "excited", "shocked" or "funny" measure the same as calm ones. No emotion samples exist, so the tags do nothing. The owner's real "my take" clip (Zanzibar) is about 7 dB noisier than the reference: its noise floor is -37.2 dBFS against -43.8. It is pitched about 1.4 semitones higher (139 Hz) but is not much wider in range (5.0 st).

### Cited Findings
- **Reference files** (contents not reproduced):
  - ~/.cache/tea-break/voice/ref_cut.wav: PCM 24 kHz mono, 11.61 s; its transcript ref_cut.txt has 33 words.
  - Also present: ref_en.wav (12.00 s) and ref_en.opus (12.0 s).
  - ~/.cache/tea-break/voice/deep/deep.wav and deeper.wav, created 2026-10-29 19:44, are the same length as ref_cut.wav and have pitch medians of 111.3 Hz and 102.1 Hz (about -2.5 and -4 semitones). They look like pitched-down copies of the reference; no pipeline config refers to them.
  - — ffprobe; [voice test]
- **Reference measurements** [voice test] on ref_cut.wav:

  | Measure | Value |
  |---|---|
  | Median F0 | 128.6 Hz |
  | F0 5th-95th percentile | 119.3-155.5 Hz = 4.6 semitones |
  | F0 standard deviation | 1.69 semitones |
  | Voiced share | 80% of the clip |
  | Pace | 170.5 wpm over the clip (174 over the talking span) |
  | Pauses ≥0.12 s | 1 (0.18 s total) |
  | Speech level (90th pct of 20 ms frames) | -15.9 dBFS |
  | Noise floor (10th pct) | -43.8 dBFS, so 27.9 dB below speech |
  | 2-5 kHz vs <200 Hz | -30.2 dB |
  | >8 kHz share | -40.5 dB of total |

- **The clone, Pig War** (15 lines, [voice test] on pig-war/tts/line_NN.wav):
  - median per-line F0 127.9 Hz, range of line medians 125.7-132.4 Hz;
  - median within-line range 4.5 semitones (4.0-5.5), median SD 1.44 semitones;
  - line pace 139-188 wpm, median 157 (word count / line length);
  - the "excited" lines (L1, L13) have ranges of 5.1 and 4.2 st; "shocked" (L12) 4.5; "warm" L15 5.5.
  - — [pig-war/tts](file:///root/.cache/tea-break/work/pig-war/tts/)
- **The clone, recap** (earlier audit):
  - median F0 129.4 Hz, within-line spread 4.9 semitones, per-line medians 123.5-141.1 Hz;
  - all 7 question lines end flat or falling;
  - no vocal pause before any punchline word;
  - `tts/refs.json` is `{}`, and voice.log says "emotion samples: none yet (every line in the usual voice)";
  - Kruskal-Wallis across tag groups: F0 p=0.51, range p=0.61, loudness p=0.92 (no detectable effect).
  - — [our_recap_audit.md](file:///home/user/HUGGING-FACE/research_notes/Manhwa%20recap%20channels%20vs%20our%20recap/our_recap_audit.md); [refs.json](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/tts/refs.json)
- **How emotion samples are wired:** build.py downloads `teabreak/emotion/{excited,mysterious,funny,shocked,serious,warm}.opus` and .txt from the private dataset in config.json (`voice_repo: Rggroups/super-kural-voice`). A missing sample falls back to the single reference. The Pig War work folder has no refs.json at all — [build.py emotion_refs()](file:///home/user/HUGGING-FACE/videos/teabreak/build.py); [config.json](file:///home/user/HUGGING-FACE/videos/teabreak/config.json)
- **The owner's own clip** (mytake-anglo-zanzibar-war.opus, 48 kHz Opus, 7.06 s):
  - median F0 139.4 Hz; 127.9-170.7 Hz = 5.0 semitones; SD 1.59 st;
  - speech -16.4 dBFS, noise floor -37.2 dBFS, so 20.7 dB below speech (reference 27.9 dB);
  - presence -27.8 dB.
  - build.py splices it in as-is, with no denoise or high-pass. The whole voice track then goes through `loudnorm=I=-16` in mix.py, which raises the clip's noise together with its speech.
  - For comparison, the earlier audit measured the clone's pause floor at about -59.5 dBFS.
  - — [voice test]; [build.py](file:///home/user/HUGGING-FACE/videos/teabreak/build.py); [mix.py](file:///home/user/HUGGING-FACE/videos/doodle/mix.py); [our_recap_audit.md](file:///home/user/HUGGING-FACE/research_notes/Manhwa%20recap%20channels%20vs%20our%20recap/our_recap_audit.md)
- **Benchmarks from the sibling notes (not channel-specific):** OverseerOS measured 53 long-form YouTube voiceovers at a median 166.5 WPM. Suggested recap narration targets are 155-175 WPM, with 0.3-0.8 s beat pauses after reveals — [narration_and_audio.md](file:///home/user/HUGGING-FACE/research_notes/Manhwa%20recap%20channels%20vs%20our%20recap/narration_and_audio.md), citing [OverseerOS](https://www.overseeros.com/blog/youtube-script-length-word-count)

### Inferences
- The numbers support the owner's diagnosis that the clone sounds like the reference:
  - same median pitch (128.6 vs 127.9 Hz);
  - same narrow range (4.6 vs 4.5 st);
  - near-identical pace (170 vs 157 wpm);
  - almost no pauses;
  - tags that change nothing.

  A formal announcement as the only reference, and no emotion samples, is the most likely cause.
- The owner's casual 7-second clip is not much more varied in pitch range (5.0 st). Recording new reference and emotion samples in a deliberately storytelling delivery (more pauses, wider range) probably matters more than recording them at all. This is an inference from one short clip.
- The my-take clip will sound noticeably different from the clone: noisier (about 22 dB worse floor than the clone's pauses), higher, brighter. A noise-reduction and level-matching step, or re-recording in a quieter space, would make the switch less jarring.
- Even a perfect voice cannot fix the script patterns in section 2: template lines, uncontracted forms, runs of short sentences. Both need work. Nothing measured here shows that the voice, rather than packaging or topic, decides whether viewers stay. That would need retention data, which is not available.

### Gaps
- No retention curves, so the claim that the voiceover is the main reason viewers stay can't be tested.
- No human listening test or reference narrator recording was measured for comparison; the "flat" judgement is relative.
- The Emu War and Zanzibar voice files are not in this container, so only the Pig War and recap clones were measured.

## 4. Pictures and video: the doodle engine, style, motion and pacing

### Takeaway
Every history video is a row of 1920x1080 "boards" on cream paper. Each board has one FLUX.2 [klein] picture (Cloudflare Workers AI) with the top third left empty for handwritten labels, stamps and calendars. Pictures paint in row by row behind a drawn pen, then zoom 4% over 8 seconds. The camera pans 0.5 s to the next board about every 10-11 s, with a whoosh. The style is consistent and clean. The boards often repeat the narration in writing (for example "1. How it started 2. What happened next 3. Who won? sources in the description"), and apart from the pen, a slow zoom and the pans, nothing moves.

### Cited Findings
- **Engine:**
  - "A video is a row of scenes on one long whiteboard"; `PAN = 0.5` seconds to the next scene.
  - Pictures are "painted in row by row behind the pen, then slowly zooming in", with defaults rows 4, zoom 0.04, zoomDur 8 s.
  - Items still drawing when the camera leaves are sped up.
  - Rendering is headless Chromium at 30 fps. Captions are burned-in ASS (Patrick Hand font) with numbers shown as digits.
  - — [engine.js](file:///home/user/HUGGING-FACE/videos/doodle/engine.js); [README.md](file:///home/user/HUGGING-FACE/videos/doodle/README.md)
- **Style:** config.json style: "Hand-drawn cartoon illustration with flat colours and clean black ink outlines, warm cream paper background ... The top third of the picture is plain empty cream paper. No text". style_ref is ../00-intro/img/s2.png; the end card is ../00-intro/img/s7.png. The skill asks for about one picture per 10 seconds (20-24), with "No flags, no blood, no gore" — [config.json](file:///home/user/HUGGING-FACE/videos/teabreak/config.json); [SKILL.md step 6](file:///home/user/HUGGING-FACE/.claude/skills/tea-break-weekly/SKILL.md)
- **Pacing:**
  - Emu War: 21 pictures (e01-e21) over 3:28, about one per 9.9 s.
  - Pig War: 23 pictures (p01-p23) plus the end card over 4:22, with 26 whoosh (board-change) events, so about one board per 10 s. It also has 7 stamps and 1 pop.
  - Zanzibar: 22 pictures (p01-p22 per its run log).
  - — [01-emu-war/img](file:///home/user/HUGGING-FACE/videos/01-emu-war/img/); [pig-war/img](file:///root/.cache/tea-break/work/pig-war/img/); [pig-war/events.json](file:///root/.cache/tea-break/work/pig-war/events.json); [Zanzibar session events](https://claude.ai/code/session_015TghYxR3wZNx7eGqUnno3T)
- **What the Pig War stills show** (contact sheets sheet_1 and sheet_3, viewed):
  - consistent cream-paper style; recurring characters drawn the same way (the spotted pink pig);
  - labels in the top third ("1859", "1 PIG = WAR?", "TRUE STORY", "HAPPY ANNIVERSARY!", "THE ALCOHOL!", "WHO WON?");
  - the greeting board writes the template outline ("Hello friends! I'm Manoj / 100% TRUE / 1. How it started 2. What happened next 3. Who won? / sources in the description").
  - — [stills/sheet_1.png](file:///root/.cache/tea-break/work/pig-war/stills/sheet_1.png); [stills/sheet_3.png](file:///root/.cache/tea-break/work/pig-war/stills/sheet_3.png)
- **Rendered outputs found** (ffprobe):

  | File | Size, fps | Length |
  |---|---|---|
  | pig-war.mp4 | 1920x1080, 30 fps | 261.97 s |
  | pig-war_short1.mp4 | 1080x1920 | 59.33 s |
  | pig-war_short2.mp4 | 1080x1920 | 45.23 s |
  | pig-war_tiktok.mp4 | 1080x1920 | 261.97 s |
  | recap.mp4 | 1920x1080 | 189.8 s |
  | short.mp4 | 1080x1920 | 44.4 s |
  | tiktok_part1-3 | 1080x1920 | 67.9 / 66.7 / 62.9 s |

  No Emu War or Zanzibar renders exist in this container — [pig-war/out](file:///root/.cache/tea-break/work/pig-war/out/); [recap/out](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/out/)
- **Shorts layout:** a cream page with an orange title ("THE PIG WAR (1859)"), a subtitle, the 16:9 board in the middle (about the middle third of the frame) and captions under it. This is visible in the served Shorts thumbnails and in a frame of pig-war_short1.mp4 — [thumb test]; frame grab
- **Recap visuals** (earlier audit): 27 panel changes in 189.8 s (8.5 per minute), a median of 6.0 s per panel, and the picture "completely still in about 72% of frames". It has no zooms, shakes or cuts; the comic column covers 52% of the 16:9 frame — [our_recap_audit.md](file:///home/user/HUGGING-FACE/research_notes/Manhwa%20recap%20channels%20vs%20our%20recap/our_recap_audit.md)

### Inferences
- A board change every ~10 s is slow next to fast-cut explainer and recap styles. Within a board, the only motion is the row-by-row paint-in, a 4% zoom and handwriting. Whether that loses viewers can't be tested without retention data.
- In the vertical Shorts the actual picture fills only about a third of the screen, with a static title above and captions below. That is a small picture on a phone.
- Boards that write out the template outline make the template more visible, so they repeat the problem in section 2.

### Gaps
- No Emu War or Zanzibar render was available to measure in this container. The Zanzibar video was only seen as its served thumbnail frame.
- Motion per frame (how much of each video is still) was measured only for the recap (earlier audit), not for the doodle videos.

## 5. Music and sound: moods, stings, mix levels and loudness

### Takeaway
The music is synthesised per video by score.py: 9 moods at 66-112 bpm, played on the FluidR3 General MIDI set, and 4 stings (rimshot, wahwah, tada, hit). It is mixed by mix.py with the voice at -16 LUFS and the music at x0.3 gain, side-chain ducked. The music drops out around each punchline, and the master is normalised to -14 LUFS. Every rendered file measures -14.1 to -14.6 LUFS integrated with a 2.2-5.3 LU loudness range. The Pig War uses 15 mood segments, 6 stings and 8 punchline drop-outs in 4:22.

### Cited Findings
- **Moods and tempos:**

  | Mood | Tempo |
  |---|---|
  | playful | 112 bpm |
  | curious | 96 bpm |
  | sneaky | 104 bpm |
  | suspense | 84 bpm |
  | dramatic | 100 bpm |
  | triumphant | 108 bpm |
  | sad | 66 bpm |
  | warm | 92 bpm |
  | silence | 90 (no notes) |

  The fade is 1.2 s each side of a mood change, and moods shorter than 3 s are folded into the one before. Stings are levelled to -18 dB RMS — [score.py](file:///home/user/HUGGING-FACE/videos/doodle/score.py)
- **Mix chain:**
  1. Voice `loudnorm=I=-16:TP=-2:LRA=11`; music `volume=0.30`.
  2. `sidechaincompress=threshold=0.02:ratio=6:attack=20:release=450`.
  3. Punchline silence from 0.9 s before to 0.5 s after the punch word (0.12 s ramps).
  4. Effects x0.5 and stings x0.35, added after ducking.
  5. Final `loudnorm=I=-14:TP=-1.5:LRA=11`.
  - The README says the music "sits 18-20 dB under" the voice. The earlier audit measured the recap's ducked music at -33.3 LUFS against the voice at -16.0 (17.3 LU under).
  - — [mix.py](file:///home/user/HUGGING-FACE/videos/doodle/mix.py); [README.md](file:///home/user/HUGGING-FACE/videos/doodle/README.md); [our_recap_audit.md](file:///home/user/HUGGING-FACE/research_notes/Manhwa%20recap%20channels%20vs%20our%20recap/our_recap_audit.md)
- **Pig War sound timeline:**
  - Moods in order: curious 0 s, warm 8.4, curious 21.0, playful 43.3, sneaky 61.8, playful 77.7, suspense 103.2, dramatic 110.5, suspense 150.0, warm 166.3, playful 182.3, curious 207.9, triumphant 231.9, sad 242.4, warm 250.7.
  - Stings: tada 82.4, rimshot 102.2, wahwah 127.7, hit 149.1, rimshot 206.7, wahwah 249.7.
  - 8 punch drop-outs, 26 whooshes, 7 stamps, 1 pop.
  - — [pig-war/events.json](file:///root/.cache/tea-break/work/pig-war/events.json)
- **Loudness** (ffmpeg ebur128, integrated / LRA):

  | File | Integrated | LRA |
  |---|---|---|
  | pig-war.mp4 | -14.3 LUFS | 4.0 LU |
  | pig-war_short1 | -14.2 | 3.9 |
  | pig-war_short2 | -14.1 | 2.2 |
  | pig-war_tiktok | -14.3 | 4.1 |
  | recap.mp4 | -14.3 | 4.1 |
  | short.mp4 | -14.6 | 3.9 |
  | tiktok_part1 | -14.4 | 3.6 |
  | tiktok_part2 | -14.5 | 4.3 |
  | tiktok_part3 | -14.3 | 5.3 |

  Earlier audit: recap true peak -0.9 dBFS — ebur128 on the files in section 4; [our_recap_audit.md](file:///home/user/HUGGING-FACE/research_notes/Manhwa%20recap%20channels%20vs%20our%20recap/our_recap_audit.md)
- **The skill's music rules:** "Give each mood at least 8 seconds ... use 5 to 8 moods in a video"; "About one sting every 40 seconds, never the same one twice in a row" — [SKILL.md step 7](file:///home/user/HUGGING-FACE/.claude/skills/tea-break-weekly/SKILL.md)

### Inferences
- The technical delivery is consistent and at platform loudness. Nothing measured is broken.
- The Pig War has 15 mood events against the skill's "5 to 8 moods". Some repeat (curious x3, playful x3, warm x3), so it changes mood about every 17 s. This may sound busy under a calm narration. The recap changes 5 times a minute (earlier audit).
- A low loudness range (2-5 LU) fits a narrow vocal delivery plus constant music. The music never stops except at punchlines.

### Gaps
- No stems were saved for the Pig War, so its voice-to-music gap was not measured directly; only the recap's was (earlier audit).
- No listening judgement of the General MIDI instrument quality was made.

## 6. WEBTOON: "The F-Rank Tea Seller" series page and the creator profile

### Takeaway
The CANVAS series is live with 1 episode ("Episode 1 - Ten Rupees a Glass", up 29 Oct 2026), 5 views, 1 subscriber and 0 likes. Its genres are Fantasy and Comedy, and the creator name is "Tea Break Comics". The profile bio promises "new episode every Thursday!" and links to the YouTube channel, and shows 0 followers. No Episode 2 exists in the repository, while the recap (6 Nov) and WEBTOON both promise a weekly Thursday episode.

### Cited Findings
- **Series page:**
  - Title "The F-Rank Tea Seller"; genre labels "Fantasy" and "Comedy"; author "Tea Break Comics".
  - Counters "view 5", "subscribe 1"; episode list: "Episode 1 - Ten Rupees a Glass", "UP Oct 29, 2026", "like 0".
  - Summary: "In 2031, monster Gates have opened in every city ... Arjun is an F-Rank, the weakest there is, so he sells chai next to Mumbai's biggest Gate for ten rupees a glass. Nobody knows that anyone who drinks his tea becomes unstoppable... for exactly one hour."
  - — [WEBTOON series page, fetched 2026-10-29](https://www.webtoons.com/en/canvas/the-f-rank-tea-seller/list?title_no=1182633)
- **Creator profile:**
  - Name "Tea Break Comics"; profile picture TeaBreakComics_profile.png (g-wcommunity.pstatic.net, uploaded 2026-10-29).
  - Bio: "Tea Break Comics by Manoj 🍵 Fantasy-comedy webtoons with fights and laughs. Now: The F-Rank Tea Seller, new episode every Thursday! Made with AI tools."
  - Link: youtube.com/@TeaBreakwithManoj.
  - Server-rendered counters "Series 0, Followers 0". The series list loads by script, so "Series 0" may be a placeholder.
  - — [WEBTOON creator profile](https://www.webtoons.com/p/community/en/u/_ejxkqn)
- **Publish pack:** "Episode 1 published Oct 29, 2026; weekly on Thursdays". Genre "Fantasy (main), Comedy (second)". The creator's note says "Created by Manoj · Made with AI tools ... New episode every week." — [PUBLISH.txt](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/upload/PUBLISH.txt)
- **Episodes in the repo:** videos/manga/f-rank/ contains only ep01 (no ep02 folder) — local file listing
- **YouTube cross-promotion:** the recap description says "Read Episode 1 free on WEBTOON ... New episode every Thursday" and "our own webtoon by Tea Break Comics. Created by Manoj, made with AI tools." The recap is now scheduled for Fri 6 Nov, after the Thursday 5 Nov date when Episode 2 would be due — [API]; [recap.json meta](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/recap.json)

### Inferences
- The "every Thursday" promise appears on WEBTOON, in the YouTube recap and in the Short, but nothing is in production for Episode 2. If 5 Nov passes without an episode, the recap goes public a day later promising a schedule that has already slipped.
- The WEBTOON numbers (5 views, 1 subscriber) are what a day-one CANVAS series gets. They say nothing yet about the story's appeal.

### Gaps
- WEBTOON's series counters and episode list are partly script-rendered. The profile's "Series 0" and the exact follower count were not confirmed in a browser.
- No WEBTOON comments or ranking data were collected.

## 7. TikTok: the files we make, and the plan

### Takeaway
We make two kinds of TikTok file:
- the weekly history run renders one full-length vertical video (Pig War: 4:22, 1080x1920);
- the manga recap is cut into three parts of just over a minute each (67.9 / 66.7 / 62.9 s), with "PART n/3" labels and a "PART 2 IS NEXT / FOLLOW SO YOU DON'T MISS IT!" end card.

The recap parts keep text clear of TikTok's own overlays (commit 7f22734). The history TikTok step was never given that fix: its captions sit at about y≈1550 of 1920, inside the bottom ~500 px that TikTok covers according to our own recap.py. No Emu War TikTok file or plan was found locally.

### Cited Findings
- **The history TikTok step (build.py step_tiktok):** "The whole story as one vertical video (TikTok pays only for videos over a minute): the board in the middle of a cream page, the title above it and big captions under it". The board is 1080x608 at y=660, the title at y=250 (fontsize 118) and the subtitle at y=420. The meta.json caption pattern is "In 1859, one dead pig almost started a war between America and Britain… with warships and cannons 🐷 The full true story. #pigwar #history #funnyhistory #truestory #learnontiktok" — [build.py](file:///home/user/HUGGING-FACE/videos/teabreak/build.py); [meta.json](file:///home/user/HUGGING-FACE/videos/teabreak/example/meta.json)
- **Overlay zones:** recap.py states "TikTok covers the top ~150 px (tabs) and the bottom ~500 px (name, caption, sound)". In a frame of pig-war_tiktok.mp4 at 30 s, the caption box is centred about 1,550 px from the top, inside that bottom zone — [recap.py](file:///home/user/HUGGING-FACE/videos/manga/recap.py); frame grab of [pig-war_tiktok.mp4](file:///root/.cache/tea-break/work/pig-war/out/pig-war_tiktok.mp4)
- **Recap TikTok parts:**
  - 67.9 / 66.7 / 62.9 s at -14.4 / -14.5 / -14.3 LUFS.
  - Labels "PART 1/3 · THE F-RANK TEA SELLER" (and 2/3, 3/3). The part-1 end card reads "PART 2 IS NEXT / FOLLOW SO YOU DON'T MISS IT!".
  - The earlier audit notes that parts 2 and 3 "start mid-story with no 'previously' line".
  - — [tiktok.log](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/tiktok.log); [tiktok/label*.txt](file:///home/user/HUGGING-FACE/videos/manga/f-rank/ep01/recap/tiktok/); [our_recap_audit.md](file:///home/user/HUGGING-FACE/research_notes/Manhwa%20recap%20channels%20vs%20our%20recap/our_recap_audit.md)
- **Process:** the weekly run sends the TikTok video and both Shorts to the owner and gives a caption to paste, with "a reminder to switch on 'AI-generated content' under More options when posting". The Zanzibar run did this ("I sent you the TikTok video and the two Shorts as files"; caption "...shorter than your tea break ☕ The full true story. #history #funnyhistory #truestory #shortestwar #zanzibar #learnontiktok") — [SKILL.md step 10](file:///home/user/HUGGING-FACE/.claude/skills/tea-break-weekly/SKILL.md); [Zanzibar session result](https://claude.ai/code/session_015TghYxR3wZNx7eGqUnno3T)
- **Emu War:** no TikTok file is in the repo or cache. The TikTok step was added on 2026-10-24 (commit 90a1e14, "Weekly Tea Break: a full-length vertical video for TikTok"), after Emu War was made and uploaded (commits 7abc219 and 548447a, 23-24 Oct). The only Emu War verticals are its two YouTube Shorts — `git log`; local listing

### Inferences
- A 4:22 vertical with a small 16:9 board in the middle and captions under TikTok's caption overlay is a weak TikTok format. Applying the recap's overlay-safe layout to the history TikTok step is a small code change.
- The "pays only for videos over a minute" premise drives both formats, but it is an internal claim. It could not be checked against TikTok's own page (see Gaps).

### Gaps
- TikTok's Creator Rewards Program page could not be read: support.tiktok.com redirected to an FAQ page that returned only a title. The "over one minute" rule and the eligibility thresholds are unverified here.
- What, if anything, the owner has posted on TikTok, and how it did, is unknown: there are no files or stats for it locally.
- The "Emu War TikTok plan" named in the brief was not found in the repo, the skills or the research notes.

## 8. Automation, credentials and policy risks

### Takeaway
A scheduled task runs the weekly writer every Wednesday at 05:40 IST in a fresh cloud session. It clones the pushed branch (which now includes SCRIPT_STYLE.md) and makes and uploads one story. The next run is Wed 4 Nov 2026 00:10 UTC. The YouTube refresh token still worked at 2026-10-30 01:13 UTC. If the OAuth app is in Testing mode, Google expires it 7 days after issue, about 30 Oct 10:45 UTC. That would break next.py at step 2 and every upload, while videos already scheduled would still go public. The other standing risks:
- the channel is unverified, so there are no custom thumbnails;
- YouTube's inauthentic-content rule, which names "templated storylines" and "AI-generated content made with generic or unoriginal templates giving the impression of mass production";
- the token's narrow scope and the disabled Analytics API, which leave the pipeline blind to retention and comments.

### Cited Findings
- **Weekly task "Tea Break weekly video" (trig_01Ekjz2QMnfZbRedZKZcteJJ):**
  - cron `CRON_TZ=Asia/Kolkata 40 5 * * 3`; enabled; persist_session false (a fresh session each time); push notification on.
  - last fired 2026-10-28 14:35 UTC (a re-run of a failed run, per the follow-up check task); next run 2026-11-04 00:10 UTC.
  - Prompt: clone https://github.com/rgcbe/hugging-face, branch claude/youtube-agent-skill-48ifal; "Follow .claude/skills/tea-break-weekly/SKILL.md ... exactly"; "Copy the files in videos/teabreak/example/ (The Pig War) for the shape of every file you write"; "Do not ask questions".
  - — [list_triggers, 2026-10-29]
- **The branch is in sync:** the local claude/youtube-agent-skill-48ifal equals origin (51a5641), and SCRIPT_STYLE.md (cdd81d9) is pushed, so the 4 Nov run will see it — `git status -sb`, `git log`
- **What the run does:**
  - next.py picks the first topic whose `match` words are in no upload's title or description, and schedules after the last scheduled upload. The next story is "great-moon-hoax" (22 topics, 3 done); this was inferred from the order and not run.
  - The voice step takes "About 30-50 minutes"; pictures use Cloudflare's free 10,000 neurons/day ("about 70 pictures").
  - — [next.py](file:///home/user/HUGGING-FACE/videos/teabreak/next.py); [topics.json](file:///home/user/HUGGING-FACE/videos/teabreak/topics.json); [SKILL.md](file:///home/user/HUGGING-FACE/.claude/skills/tea-break-weekly/SKILL.md)
- **Token expiry check:**
  - A one-shot task "Check if the YouTube key expired" (trig_01J3xEEwnh6h9NrS7uZroC88) is set for 2026-10-30 11:30 UTC. Its prompt: "Testing-mode keys stop 7 days after they were made; this one was connected 23 Oct ~10:45 UTC".
  - The fix it describes: "publish the app (Google Auth Platform → Audience → Publish app), make a new refresh token ... replace YT_REFRESH_TOKEN_ADULT".
  - Token refreshes succeeded on 2026-10-29 and 2026-10-30 01:13 UTC; the granted scope is `https://www.googleapis.com/auth/youtube`.
  - — [list_triggers]; token test (no token printed)
- **Google's rule:** a project whose OAuth consent screen is external and in "Testing" "is issued a refresh token expiring in 7 days", "unless the only OAuth scopes requested are a subset of name, email address, and user profile" — [Google Identity, OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- **What uses the token:**
  - next.py `token()` runs first in step 2, so an expired token stops the run before research.
  - upload.py does uploads, the AI label, thumbnails and playlist adds.
  - The check-in tasks list uploads with it.
  - Videos already uploaded with a publishAt "go public by itself at its time" (the skill's own description).
  - — [next.py](file:///home/user/HUGGING-FACE/videos/teabreak/next.py); [upload.py](file:///home/user/HUGGING-FACE/videos/doodle/upload.py); [SKILL.md step 9](file:///home/user/HUGGING-FACE/.claude/skills/tea-break-weekly/SKILL.md)
- **Scope and Analytics:** the "youtube" scope is not enough for commentThreads.list (403 "insufficient authentication scopes"). The YouTube Analytics API is disabled in project 906871128572 (403) — [API]
- **YouTube Partner Program, generic/repetitive ("inauthentic") content:** "Image slideshows, templated storylines, or scrolling text with minimal or no narrative, commentary, or educational value" and "AI-generated content made with generic or unoriginal templates giving the impression of mass production". The changelog's latest entry is the 15 July 2025 rename to "inauthentic content" — [YouTube Help, YPP policies](https://support.google.com/youtube/answer/1311392). The sibling note covers third-party reporting of a July 2026 clarification and flags it as a conflict — [visuals_structure_policy.md](file:///home/user/HUGGING-FACE/research_notes/Manhwa%20recap%20channels%20vs%20our%20recap/visuals_structure_policy.md)
- **Custom thumbnails need verification** (video and Shorts) — [YouTube Help 72431](https://support.google.com/youtube/answer/72431); the channel shows `longUploadsStatus: eligible` [API]
- **Monetisation state:** `isChannelMonetizationEnabled: false`, 8 subscribers — [API]

### Inferences
- **If the token expires on 30 Oct and nothing is done before 4 Nov:**
  - the weekly run fails at step 2 (next.py) and reports with a push notification;
  - no story is made for Sat 14 Nov, and no playlists or labels are set;
  - the check tasks fail;
  - Pig War (31 Oct, 2 Nov, 4 Nov), the recap (6, 8 Nov) and Zanzibar (7, 9, 11 Nov) still go public as scheduled.

  Publishing the OAuth app removes the 7-day limit. Re-consenting with youtube.force-ssl and enabling the Analytics API would also unlock comments and retention.
- **Inauthentic-content exposure (judgement, not a ruling):** the channel today is AI voice, AI pictures, and the same hook opener, greeting sentence, outline board, comments line and description template every week, made by an unattended weekly job. That is close to the wording "templated storylines" and "giving the impression of mass production". Against it: each script is researched with two named sources, has jokes and commentary, and one video carries the owner's real recorded take. Removing the fixed template lines and adding the owner's own reactions and recordings is the most direct way to reduce the risk. These are the same changes SCRIPT_STYLE.md asks for.

#### Ranked flags across the whole channel (what looks weak or broken)
1. **No custom thumbnail on any of 13 videos.** The channel is unverified; verify the phone and set the existing designed thumbnails (Pig War before 31 Oct, Zanzibar and recap before 6-7 Nov).
2. **The template opening and ending are repeated in every history video,** and the weekly writer is still told to copy them (the example files and the scheduled prompt conflict with SCRIPT_STYLE.md). The 4 Nov run will probably repeat them.
3. **The OAuth token may expire on 30 Oct** (Testing mode). The 4 Nov run and all uploads would fail; the narrow scope and disabled Analytics leave no retention or comment data.
4. **The voice is a clone of an 11.6 s formal announcement,** with no emotion samples. The measured pitch range is about 4.5 semitones, pacing is fast with almost no pauses, and emotion tags do nothing. The owner's own clip is noisier by about 7 dB against the reference and is not cleaned.
5. **Scripts barely use contractions outside the greeting** (Zanzibar 0, Pig War 1). The Emu War has runs of up to 9 short sentences, and listening-test rewrites chop lines further.
6. **The Zanzibar title lacks "Zanzibar"** against the skill's own rule. Pig War and Zanzibar Shorts do not link the full video.
7. **The schedule breaks around the recap:** Fri and Sun posts, five uploads in 6-11 Nov. The recap promises a weekly Thursday WEBTOON episode that does not exist yet, and the recap pair is set to `embeddable: false`.
8. **TikTok:** the history vertical puts captions under TikTok's bottom overlay; the recap's overlay fix wasn't ported. No Emu War TikTok exists.
9. **Minor:**
   - two public playlists are empty, and the intro videos are in no playlist;
   - the Pig War music has 15 mood changes against the skill's 5-8;
   - the AI label can't be confirmed through the API;
   - the local pig-war.mp4 differs from the uploaded file.

### Gaps
- Whether the OAuth app is actually in Testing mode is not visible from the token. Only the expiry, or Google Cloud Console, would show it.
- YPP eligibility thresholds were not fetched in this pass.
- How YouTube actually judges this channel under the inauthentic-content rule can't be known before a YPP review. The exposure above is a judgement.
